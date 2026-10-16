#!/bin/bash
cd /igvfd || exit 1
create-mapping config/pyramid/ini/development.ini --app-name app --dry-run > /asset-output/mapping.json
