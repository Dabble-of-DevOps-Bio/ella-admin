FROM dabbleofdevops/ella:1.11.1

USER root

ARG RSTUDIO_VERSION=1.3.1073
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY ./requirements /requirements

# Since we're building PDFs this requires a million packages
RUN apt-get update -y \
    && apt-get upgrade -y \
    # dependencies for building Python packages
    && apt-get install -y  \
    apt-utils build-essential \
    # psycopg2 dependencies
    ca-certificates \
    apt-transport-https \
    curl \
    libxslt-dev  \
    gnupg \
    pandoc libpangocairo-1.0-0 \
    libcairo2  lsb-release xdg-utils  \
    python3-lxml \
    gettext \
    texlive-latex-recommended \
    texlive-fonts-recommended \
    texlive-latex-extra \
    latexmk \
    texlive-xetex  \
    chromium-chromedriver \
    && apt-get install -y $(cat /requirements/pyppeteer_reqs.txt) \
    && curl -sL https://deb.nodesource.com/setup_14.x | bash - \
    && apt-get install -y nodejs \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# All imports needed for autodoc.
RUN pip install -r /requirements/local.txt -r /requirements/production.txt
RUN pip install -r /requirements/docs.txt

WORKDIR /docs

#CMD make livehtml
