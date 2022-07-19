FROM python:3.9-bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apt update -y && apt upgrade -y \
    && apt install -y python3-dev memcached

COPY requirements.txt ./
COPY requirements_deploy.txt ./
# install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements_deploy.txt

# copy project
COPY ./webserver /app/webserver
COPY ./backend_library /app/backend_library

WORKDIR /app
# install backend
RUN pip install ./backend_library/src
WORKDIR /app/webserver/src/main/sop

#copy and set entrypoint
COPY ./entrypoint.sh /entrypoint.sh
ENTRYPOINT ["sh", "/entrypoint.sh"]
