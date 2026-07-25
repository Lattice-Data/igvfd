def includeme(config):
    config.add_route('matrix-file-set-metadata', '/matrix-file-set-metadata{slash:/?}')
    config.add_route(
        'matrix-file-set-sample-metadata',
        '/matrix-file-set-sample-metadata{slash:/?}'
    )
    config.scan(__name__)
