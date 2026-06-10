# Titanic Data Cleaner Service

## User Manual 

Find after some useful commands to operate the frontend and backend applications.

Clone the project somewhere...

__Build and Run all applications__

```shell
$ cd <...>/titanic-data-cleaner-service 
$ docker compose up -d --build
``` 

__Troubleshooting__

If you get an error like this (if you use Windows): 

```shell
...
ERROR [playwright 8/9] RUN bun install                                                                                                                                             0.4s
------
 > [playwright 8/9] RUN bun install:
0.305 /bin/sh: 1: bun: not found
------
Dockerfile.playwright:17
...
```

Then, you need to bypass _Playwright_ as follows: 

```shell
$ docker compose up backend frontend db mailcatcher -d --build
```

Check that all containers are started: 

```shell
$ docker compose ps
NAME                 ...                     SERVICE       ...      PORTS
titanic-data-cleaner-service-adminer-1       adminer                0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp
titanic-data-cleaner-service-backend-1       backend:latest         0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
titanic-data-cleaner-service-db-1            postgres:18            0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp
titanic-data-cleaner-service-frontend-1      frontend:latest        0.0.0.0:5173->80/tcp, [::]:5173->80/tcp
titanic-data-cleaner-service-mailcatcher-1   schickling/mailcatcher 0.0.0.0:1025->1025/tcp, [::]:1025->1025/tcp, ...
titanic-data-cleaner-service-proxy-1         traefik:3.6            0.0.0.0:80->80/tcp, [::]:80->80/tcp, 0.0.0.0:8090->8080/tcp, [::]:8090->8080/tcp
```

__Troubleshooting__

If you get error like this: 

```shell
...
✘ Container titanic-data-cleaner-service-prestart-1    Error service "prestart" didn't complete successfully: exit 255
...
```

Then wipe out the database volume and restart the containers: 

```shell
$ docker compose down -v
...
$ docker compose up -d --build
``` 

__Quick Tests__

Accessing the frontend: [http://localhost]. 

__Troubleshooting__

If it hangs with a 404 error, then it is a Traefik issue: HTTPS certificates problem. See the Developer section to fix it. 
Use [http://localhost:5173] (e.g. the listening port of the __frontend__) 


## Developer Manual

Access the _Swager UI_ at  [http://localhost:8000/docs]






