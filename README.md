[![pipeline status](https://git.scc.kit.edu/ipd-boehm/ipd-pse-2022/subspace-outlier-profiling/team-2/implementierung/badges/main/pipeline.svg)](https://git.scc.kit.edu/ipd-boehm/ipd-pse-2022/subspace-outlier-profiling/team-2/implementierung/-/commits/main) [![coverage report](https://git.scc.kit.edu/ipd-boehm/ipd-pse-2022/subspace-outlier-profiling/team-2/implementierung/-/jobs/artifacts/main/raw/public/django-tests.svg?job=django-tests)](https://git.scc.kit.edu/ipd-boehm/ipd-pse-2022/subspace-outlier-profiling/team-2/implementierung/-/jobs/artifacts/main/raw/public/django-tests.svg?job=django-tests) [![coverage report](https://git.scc.kit.edu/ipd-boehm/ipd-pse-2022/subspace-outlier-profiling/team-2/implementierung/-/jobs/artifacts/main/raw/public/backend-tests.svg?job=backend-tests)](https://git.scc.kit.edu/ipd-boehm/ipd-pse-2022/subspace-outlier-profiling/team-2/implementierung/-/jobs/artifacts/main/raw/public/backend-tests.svg?job=backend-tests)

# Subspace Outlier Profiler

## Introduction

"Subspace Outlier Profiler" or SOP for short, provides a Platform
for running outlier detection algorithms written in Python on subspaces of
multidimensional datasets.  
SOP is built with the web-framework [Django](https://djangoproject.com) and the frontend
toolkit [Boostrap](https://getbootstrap.com/). All icons used (except for the self-drawn favicon)
are [Bootstrap icons](https://icons.getbootstrap.com/).

---

## Features

Features include, but are not limited to:

+ Uploading own csv-Datasets.
+ Selecting subspace amount and size to analyse.
+ Selecting outlier detection algorithms from the [pyod library](https://pyod.readthedocs.io).
+ Uploading own outlier detection algorithms (see [Implementing own algorithms](#implementing-own-algorithms)).
+ Supports Postgres and MariaDB/MySQL as databases.

---

The project is split into the backend which does all the calculation and scheduling and the webserver.
The backend library is designed to be well usable in other contexts than the webserver used in this project.
For further technical insight have a look at the respective readme files.

---

## Deployment

SOP is meant to be deployed as a docker image, built with the included Dockerfile.
Although the steps to get the app up and running are described in great detail, a basic
knowledge of docker compose will come in handy.
Make sure, that the docker daemon is enabled and running.

The image is designed to be used in a microservice-environment
to provide maximum flexibility to the deployer.  
Therefore, the image runs a gunicorn process that serves the site and requires
a webserver like nginx to proxy http requests to the gunicorn process of the container.
This gives the deployer the freedom to make deployment as simple or as complex as they require.

The services defined in this text are then configured via environment variables (
see [Configuring Deployment](#configuring-deployment)).

If you don't specify an external database, the app will use sqlite as the database. It is strongly discouraged from
doing this, as sqlite does not pair well with parallel accesses,
which is likely to cause problems with this application.
Therefore, we recommend using a standard database like MariaDB/MySQL or PostgreSQL.

To make the process of setting up the webserver, SOP and an external database easier,
we recommend using `docker compose` (preferably compose v2 to be able to apply resource limitations)
(see [Installing Docker](https://docs.docker.com/engine/install/)
and [Installing compose](https://docs.docker.com/compose/install/)).
To do this, clone the git repo and create a file `docker-compose.yaml`
in the parent directory of the git repo and continue reading.

### Setting up the SOP image:

Add to your `docker-compose.yaml`:

```yaml
version: '3.8'

services:
  sop_app:
    container_name: sop_app
    build: ./implementierung
    restart: unless-stopped
    env_file: sop.env
    shm_size: '8gb'
    expose:
      - 8000
    volumes:
      - ./static:/static
      - ./media:/app/webserver/src/main/sop/media
    depends_on:
      - sop_db
```

#### Explanation:

+ `env_file`: use environment variables from file the `sop.env` for configuration.
+ `shm_size`: Since SOP uses shared memory for accessing datasets between processes,
  and docker limits `/dev/shm` to 64 MiByte by default, the size of shared memory
  has to be increased to a reasonable size. Effectively, this should be roughly
  the amount of RAM you are intending to use.
+ `expose`: Expose port 8000 to docker API (this is where gunicorn is listening).
+ `volumes`: If you want [persistent storage](https://docs.docker.com/storage) (and you probably do) use docker volumes
  or bind mounts for locations `/static` and `/app/webserver/src/main/sop/media` to keep results and datasets between
  container restarts.
+ `depends_on`: If you are using an external database, make sure the database starts before sop does.

#### Notes:

+ If you are using bind mounts, create the host directories (here `static` and `media` in the current directory, but you
  can
  create them wherever you want, just remember to adjust the lines in `docker-compose.yaml`).
+ If the system you are deploying on uses SELinux, you might need a [:Z](https://docs.docker.com/storage/bind-mounts/)
  tag at the end of you bind mount.
+ If your compose version supports it, you can
  use [resource limits](https://stackoverflow.com/questions/42345235/how-to-specify-memory-cpu-limit-in-docker-compose-version-3)
  ,
  as the app will use a lot of resources,
  especially CPU time, if you are running many algorithms at once and don't impose limits.

---

### Setting up the webserver image:

The second step is to define the webserver. We recommend using nginx.

The easiest way to get nginx up and running, is to use our nginx image, prepacked with
the upload progress module. By default, the webserver will be accessible from `127.0.0.1:80`.
This probably doesn't need changing if you are using a reverse proxy on the same host to manage requests.

Of course, you can also use any other image containing nginx
like [ this one ](https://hub.docker.com/_/nginx)(see [Example NGINX config](#example-nginx-config))
or an entirely different webserver.

For example, to use our image, add the following lines to your `docker-compose.yaml` under the
existing content:

```yaml
  sop_nginx:
    container_name: sop_nginx
    restart: unless-stopped
    image: albinoboi/nginx-sop:latest
    ports:
      - "80:80"
    volumes:
      - ./static:/static
    depends_on:
      - sop_app
```

#### Explanation:

+ `ports`: bind ports 80 and 443 of nginx container to same ports of host.
+ `volumes`: use the same docker volume / bind mount used in [setting up the django app](#setting-up-the-sop-image)
  so that the webserver can serve static files of the django application.  
  Optionally, bind mount an nginx config file `sop.conf` (see [Example nginx config](#example-nginx-config)) if you have
  to make custom changes to the nginx config or if you are using a webserver different from `albinoboi/nginx-sop`.
+ `depends_on`: Make sure the django app is running before starting the webserver.

#### Example nginx config:

If you want to provide a custom nginx config file (to make the site available from other hosts than localhost, for
example)
or use another image that is not `albinoboi/nginx-sop`, you will have to provide a config file.
You can do this for example, by mounting the config to `/etc/nginx/conf.d/sop.conf`.

(see [NGINX config documentation](https://nginx.org/en/docs/beginners_guide.html)).
An example NGINX config `sop.conf` with the progressbar module enabled:

More info: [NGINX documentation](https://docs.nginx.com/nginx/admin-guide/installing-nginx/installing-nginx-docker/).

```text
# Define upstream django server to forward requests to
upstream django_web {
    server sop_app:8000;
}
        
# Define upload progress data buffer
upload_progress uploadp 1m;
 
server {
    server_name 127.0.0.1;
    listen 80;
    
    # Make uploads up to 500m possible
    client_max_body_size 500m;
    
    # Make upload progress return in json format
    upload_progress_json_output;
 
    # Define root url location and pass requests to django
    location / {
        proxy_pass http://django_web/;
        track_uploads uploadp 30s;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
 
    # Define static file url and location
    location /static/ {
        alias /static/;
    }
 
    # Define upload progress reporting url
    location ^~ /upload_progress {
        report_uploads uploadp;
    }
}
```

#### Notes:

+ The upstream `server` name **must** be the same as the django SOP docker container name.
+ If you are using our nginx image and not replacing the config file, your SOP container name **has** to be `sop_app`.
+ If you are using our image, but want to supply a custom nginx config, the file
  must be mounted to `/etc/nginx/http.d/` instead of `/etc/nginx/conf.d/`(because
  of [Alpine nginx package](https://wiki.alpinelinux.org/wiki/Nginx) directory structure).
+ For upload-progressbars to work correctly under nginx, you have to include
  the [NGINX upload progress module](https://www.nginx.com/resources/wiki/modules/upload_progress/)
  this is because NGINX buffers the uploads before transferring them to django.
  (already packaged in `albinoboi/nginx-sop`)

---

### Setting up the database image (recommended):

The last step is to define a service for the database container.
We will use `postgres` for this example, but feel free to use MariaDB/MySQL.
Add the following to your `docker-compose.yaml`:

```yaml
  sop_db:
    container_name: sop_db
    restart: unless-stopped
    image: postgres:12.0-alpine
    env_file: sop.env
    volumes:
      - ./db-data:/var/lib/postgresql/data
```

#### Explanation:

+ `env_file`: Use environment variables from `sop.env` file for configuring the database.
+ `volumes`: Use docker volume/bind mount for persistent storage.

### Configuring Deployment

Now that the services are defined, it's time to define environment variables to configure
Django and the database. To do this, create the file `sop.env` in the same directory as your
`docker-compose.yaml`:

```text
# Database config
POSTGRES_USER="db_user"
POSTGRES_PASSWORD="securepassword123"
POSTGRES_DB="django_db"
 
# Django config
DJANGO_SETTINGS_MODULE="sop.settings_deploy"
DJANGO_SECRET_KEY="securekey123"
DJANGO_DEBUG="0"
SOP_LOG_LEVEL="INFO"
DJANGO_ALLOWED_HOSTS="127.0.0.1 your-domain.com"
DJANGO_CSRF_TRUSTED_ORIGINS="https://your-domain.com http://127.0.0.1"

#Django database config
DATABASE_ENGINE="django.db.backends.postgresql"
DATABASE_NAME="django_db" # Same as POSTGRES_DB
DATABASE_USER="db_user" # Same as POSTGRES_USER
DATABASE_PASSWORD="securepassword123" # Same as POSTGRES_PASSWORD
DATABASE_HOST="sop_db"
DATABASE_PORT="5432"

# Django admin user creation
DJANGO_SUPERUSER_USERNAME="admin"
DJANGO_SUPERUSER_PASSWORD="secure"
DJANGO_SUPERUSER_EMAIL="admin@admin.com"
```

### Explanation:

+ `Database config`: Define database variables, like user, password and database.
  The exact names of the variables will depend on the database you are using.
  The example here uses postgres.
+ `Django config`: Define django variables. Includes `DJANGO_ALLOWED_HOSTS`, which defines
  the hostnames, from which the app will be reachable, whether debug
  messages should be displayed on invalid requests (insecure) and CSRF trusted origins
  when requests are proxied (has to specify protocol -> http / https).
+ `Django database config`: Define the Database django should connect to. `DATABASE_HOST`
  must be the name of the Database container. Specify the same user, password and database name
  as in the database config.
+ `Django admin user creation`: Django will create a superuser with the defined credentials
  during initial startup, so the deployer is able to log in to the site and create users

Now that you have defined the docker services and environment variables, you're all set.  
Your `docker-compose.yaml` should now look similar to this:

```yaml
version: '3.8'

services:
  sop_app:
    container_name: sop_app
    build: ./implementierung
    restart: unless-stopped
    env_file: sop.env
    shm_size: '8gb'
    expose:
      - 8000
    volumes:
      - ./static:/static
      - ./media:/app/webserver/src/main/sop/media
    depends_on:
      - sop_db

  sop_nginx:
    container_name: sop_nginx
    restart: unless-stopped
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./static:/static
    depends_on:
      - sop_app

  sop_db:
    container_name: sop_db
    restart: unless-stopped
    image: postgres:12.0-alpine
    env_file: sop.env
    volumes:
      - ./db-data:/var/lib/postgresql/data
```

Run `docker compose up -d` and navigate to `http://127.0.0.1` or your custom domain to access
the application (You might have to wait a few moments as database tables and migrations have
to be run on first startup).

To update your app, just pull the changes into you local git repo, stop the compose stack with `docker compose down`
and run `docker compose up --build`.

---

## Implementing own algorithms

SOP supports outlier detection on user-written outlier detection algorithms written in python. These algorithm files
have to contain a class which has the same name as the python file (case-insensitive) and is a subclass of
the `pyod.models.base.BaseDetector` class and implement the required methods
(see [pyod BaseDetector documentation](https://pyod.readthedocs.io/en/latest/api_cc.html#pyod.models.base.BaseDetector))
.

For example, when you upload a python file where the class of the algorithm is called "CoolNewAlgorithm", the file needs
to be named "coolnewalgorithm.py" or "cOoLnEwAlGoRiThM.py".

You can upload your algorithms from inside the app in the "Algorithms" section.

---

## Updating pyod

Our app ships with pyod version 1.0.4 . If you want to update pyod, because they added
a new outlier detection algorithm for example, you will have to modify the `pyodtodb` django
management command, as Database entries have to be created for the new algorithms and the files might have to be
renamed.
To do this, you have to add entries for the new algorithms in the `PYOD_ALGORITHMS` list containing instances of
the `PyodAlgorithm` Dataclass.


