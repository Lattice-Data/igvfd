# No shebang, on purpose: the interpreter comes from the calling shell's ENOEXEC fallback, so it
# depends on the entrypoint -- bash via docker/wait-for-local-services-entrypoint.sh (the compose
# path CI uses), dash via the image's own scripts/pyramid/entrypoint.sh. Declared sh here because
# that is the stricter of the two; a '#!/bin/bash' would pin bash and change the dash path, which
# is a behaviour change rather than a lint fix.
# shellcheck shell=sh
generate-mappings --app-name app config/pyramid/ini/development.ini --relative-output-directory src/igvfd/mappings
