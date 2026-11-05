# Removing an object type

Removing a type from igvfd is three things, all done by hand and in this order: unlink every reference to its objects, delete the objects from Postgres, and delete the type's OpenSearch index. The code change that removes the schema and the type does none of the last two for you. In particular, the mapping update only deletes old indices that are empty, and nothing ever empties the index of a type that no longer exists.

Automating the deletion was considered for DB2-85 (snovault2 PR 2) and dropped: permanent removal is rare, the risk of accidental destruction is high, and diverging from upstream snovault makes it harder to debug with the IGVF DACC team. Keep it manual.

The worked example is the Treatment type: removed in DB2-75 Release B ([v16.0.0, #160](https://github.com/Lattice-Data/igvfd/pull/160)) with the rows and the index left in place, which caused the DB2-85 incident described at the end. The procedures below are the ones used to clean it up on 2026-11-05.

## What to change in igvfd

A type removal touches the same places as adding one, in reverse: the schema and its changelog in `src/igvfd/schemas/`, the type class in `src/igvfd/types/`, the regenerated mapping file in `src/igvfd/mappings/`, the search config in `src/igvfd/searches/configs/`, its audits, and the inserts, fixtures and tests that mention the type. The backend dashboard in `cdk/infrastructure/constructs/dashboards/` lists collections, so it and its CDK snapshot change too. igvf-ui and the db2-flattener read properties by name, so grep both before the change ships.

## 1. Unlink every reference

Properties on other types that link to the removed type need their own schema version bump and an upgrade that drops or rewrites the values (see [updating_schemas.md](updating_schemas.md)), shipped and batch-upgraded before or with the release that removes the type. Afterwards no `links` row may point at the objects:

```sql
SELECT source, rel, target FROM links WHERE target IN ('<uuid>'::uuid, ...);
```

This must return nothing before step 2. snovault's delete cascades over `links`, so a live object still pointing at a removed row would silently lose that link row.

## 2. Delete the objects from Postgres

Use snovault's own `RDBStorage.delete_by_uuid`, which removes the resource row, its current and historical property sheets, its unique keys and its link rows. A delete writes a transaction record but does not notify the indexer, because only item create and update put an `updated` list on the transaction. It is irreversible except from an RDS snapshot, so:

1. Take a manual RDS snapshot and wait until it is available (`aws rds create-db-snapshot`, then `aws rds wait db-snapshot-available`).
2. From the `pyramid` container, read-only: `SELECT rid, item_type FROM resources WHERE rid IN (...)` must return exactly the expected rows of the removed type, and the `links` query above must return nothing.
3. From the same container, in one transaction: re-run both checks, call `app.registry[STORAGE].write.delete_by_uuid(uuid)` for each row, count the rows left in `resources`, `keys`, `current_propsheets`, `propsheets` and `links` for those UUIDs, and commit only if every count is zero. Boot the app the way `batchupgrade` does (`pyramid.paster.get_app` on `config/pyramid/ini/$INI_NAME`, with `SQLALCHEMY_URL` exported as in `scripts/pyramid/batchupgrade.sh`) and run the work under `transaction.manager`, so a failed check rolls everything back.
4. Confirm `/<uuid>/` returns 404.

If the rows are left in place instead, they are inert but not harmless: a direct request returns a 500, and while the index below still exists they can be queued for reindexing and fail (see the incident).

## 3. Delete the OpenSearch index

Each type has its own index, named `<type>_<hash>` and carrying two aliases, the type name and the shared `snovault-resources`. From the `pyramid` container:

```bash
# every index under the shared alias; anything that is not an index_name in src/igvfd/mappings/*.json is stale
curl -s "$OPENSEARCH_URL/_cat/aliases/snovault-resources?h=index&s=index"
curl -s "$OPENSEARCH_URL/_cat/indices/<type>*?v&h=index,docs.count"
curl -s -XDELETE "$OPENSEARCH_FOR_WRITING_URL/<type>_<hash>"
```

Delete by exact index name. OpenSearch refuses to delete an alias name, so a typo that hits the type alias fails safe. Deleting the index drops its own aliases; the shared alias stays on every other index.

Expect to also see empty `<type>_<oldhash>` indices of types that still exist: at deploy time the mapping update queues the reindex and then runs the old-index cleanup before the indexer has drained the old indices, so they are only deleted on the following mapping run. Those are normal and need no action.

## The incident, if steps 2 and 3 are skipped

Symptoms: the `...InvalidationQueue...DeadLetterQueueHasMessagesAlarm` is in ALARM, `/indexer-info` shows messages in `invalidation_dead_letter_queue` and `has_indexing_errors: true`, and the backend logs show `UnknownItemTypeError: <removed type>`.

Cause: the removed type's index is still under `snovault-resources`. Editing anything its documents embed (a lab, an award, a controlled term) queues them for reindexing, rendering them fails because the type is not registered, and after the retries the messages land in the dead-letter queue. The mapping update logs show `<index> is not latest but still has documents, skipping delete`.

Fix: do steps 3 and 2 above, then purge the dead-letter queue (`aws sqs purge-queue` on the queue whose name contains `DeadLetterQueue`), and check `/indexer-info` and the alarm. The alarm follows the SQS metric, which publishes every five minutes.
