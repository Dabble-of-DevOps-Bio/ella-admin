#!/usr/bin/env bash

make dev

# TODO will probably have to wait for a port or something here

rm -rf docs/html

#docker-compose -f local.yml build docs
#docker-compose -f local.yml restart docs
docker-compose -f local.yml exec docs bash -c "cd /docs && \\
    sphinx-build -b html -c . _source html"

S3="dabble-of-devops-ella-admin-docs"
DISTRO="E28L1WGVJ2MBIH"

aws s3 sync --acl public-read docs/html s3://${S3} --delete

aws s3 website s3://${S3}/ --index-document index.html

aws cloudfront create-invalidation --distribution-id ${DISTRO} --paths "/*"

rm -rf docs/html
