# Getting started

## Prerequisites

- Python 3.12
- Poetry 2.1.3
- Make

Docker or Podman is optional.

## Install and run

```bash
git clone https://github.com/ONSdigital/survey-genie.git
cd survey-genie

cp .env.example .env
make install
make templates
make provision-user
make run
```

`make provision-user` runs `scripts/provision_users.py` and creates the local `users.json` used by `AUTH_MODE=local`.

Open:

```text
http://127.0.0.1:5000
```

## Use a custom survey

Set an absolute path in `.env`:

```text
SURVEY_DEFINITION_FILE=/absolute/path/to/survey.json
```

The `create_app()` function in `src/survey_genie/app.py` loads and validates the definition during application startup. Invalid JSON or unsupported configuration prevents the application from starting.

## Containers

```bash
make docker-build
make docker-run
```

or:

```bash
make podman-build
make podman-run
```

The supplied container targets mount `users.json` at `/app/users.json`; configure:

```text
LOCAL_USERS_FILE=/app/users.json
```

## Development

```bash
make all-tests
make check-python-nofix
make run-docs
```

Use `make help` for all supported targets.
