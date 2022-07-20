FROM python:3.9-slim-bullseye

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apt update -y && apt upgrade -y \
    && DEBIAN_FRONTEND=noninteractive apt install -y python3-dev memcached

# copy requirements list and docker entrypoint
COPY requirements.txt requirements_deploy.txt entrypoint.sh ./

# copy backend for install
COPY ./backend_library /app/backend_library

# install dependencies
RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install --no-cache-dir -r requirements.txt \
    && python3 -m pip install --no-cache-dir -r requirements_deploy.txt \
    && python3 -m pip install --no-cache-dir /app/backend_library/src \
    && rm -rf /app/backend_library \
    && apt autoremove

# copy webserver
COPY ./webserver /app/webserver

#copy and set entrypoint
ENTRYPOINT ["sh", "/entrypoint.sh"]
