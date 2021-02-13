#!/usr/bin/env python
from livereload import Server, shell
import os

source_dir = "/docs/_source"
server = Server()
server.watch(
    source_dir,
    shell('jupyter-book build -W -n --keep-going --builder html --path-output /docs/_jupyter-book . ', cwd=source_dir),
    delay=1,
)
server.serve(
    root='/docs/_jupyter-book/_build/html',
    host='0.0.0.0',
    port=8001
)
