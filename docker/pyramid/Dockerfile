FROM public.ecr.aws/docker/library/python:3.11.15-slim-trixie

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

ENV VIRTUAL_ENV=/opt/venv

ENV REFERENCE_DATABASE_DIRECTORY=/srv/sqlite

RUN useradd -u 1444 -m igvfd

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    git \
    graphviz \
    libjpeg-dev \
    libmagic-dev \
    libpq-dev \
    libsqlite3-dev \
    make \
    zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# graphviz pulls in libgd3, which hard-depends on libheif (DSA-6417-1). A cold build of the
# layer above already resolves to the fixed version; this guards against a cached one.
RUN apt-get update \
    && apt-get install -y --no-install-recommends --only-upgrade \
    libheif1 \
    libheif-plugin-libde265 \
    libheif-plugin-dav1d \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN chown -R igvfd:igvfd $VIRTUAL_ENV

RUN mkdir -p $REFERENCE_DATABASE_DIRECTORY

RUN chown -R igvfd:igvfd $REFERENCE_DATABASE_DIRECTORY

WORKDIR /scripts

COPY --chown=igvfd:igvfd scripts .

RUN chmod -R +x /scripts

WORKDIR /igvfd

COPY --chown=igvfd:igvfd setup.cfg pyproject.toml build-constraint.txt ./

COPY --chown=igvfd:igvfd src/igvfd/__init__.py src/igvfd/__init__.py

USER igvfd

RUN python -m pip install pip==26.0.1

RUN PIP_BUILD_CONSTRAINT=build-constraint.txt pip --use-feature=build-constraint install -e .[test]

COPY --chown=igvfd:igvfd src/igvfd/schema_formats.py src/igvfd/schema_formats.py

COPY --chown=igvfd:igvfd src/igvfd/ontology.py src/igvfd/ontology.py

COPY --chown=igvfd:igvfd assets/ontology.json.gz assets/ontology.json.gz

COPY --chown=igvfd:igvfd src/igvfd/commands/make_reference_db.py src/igvfd/commands/make_reference_db.py

COPY --chown=igvfd:igvfd src/igvfd/commands/make_audit_docstring_json.py src/igvfd/commands/make_audit_docstring_json.py

RUN make-reference-db

COPY --chown=igvfd:igvfd . .

# Runs as igvfd (see USER above) and creates src/igvfd/static/doc/ itself. Must stay
# after the COPY above, which is what puts igvfd/audit/ in place for the audit registry scan.
RUN make-audit-docstring-json

EXPOSE 6543

ENTRYPOINT ["/scripts/pyramid/entrypoint.sh"]

CMD ["/scripts/pyramid/run-production.sh"]
