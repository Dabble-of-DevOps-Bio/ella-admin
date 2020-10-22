#!/usr/bin/env bash

make dev

# TODO will probably have to wait for a port or something here

docker-compose -f local.yml exec docs bash -c "cd /docs && \\
    sphinx-build -b html -c . _source html"

S3="dabble-of-devops-ella-admin-docs"

aws s3 sync --acl public-read docs/html s3://${S3} --delete

aws cloudfront create-invalidation --distribution-id E3BP80XMG5T8AW --paths "/*"
