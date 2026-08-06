# Environment variables

Runtime configuration is defined by `Settings` and `load_settings()` in `src/survey_genie/config.py`.

| Variable | Required | Default | Description |
|---|---:|---|---|
| `FLASK_SECRET_KEY` | Production: yes | `dev-only-change-me` | Flask session-signing key. |
| `SERVICE_NAME` | No | `Survey Genie` | Display name for the service. |
| `AUTH_MODE` | No | `local` | Authentication backend: `local` or `gcs`. |
| `LOCAL_USERS_FILE` | Local auth: yes | `users.json` | Local users JSON path. |
| `GCP_AUTH_BUCKET_NAME` | GCS auth: yes | None | Bucket containing the users JSON. |
| `GCP_AUTH_BLOB_NAME` | No | `users.json` | Users JSON object name. |
| `SESSION_COOKIE_SECURE` | No | `false` | Restricts the session cookie to HTTPS when true. |
| `SURVEY_DEFINITION_FILE` | No | bundled `src/survey_genie/survey_definitions/example_survey.json` | Survey JSON loaded at startup. |

## Local example

```text
FLASK_SECRET_KEY=replace-with-a-long-random-secret
SERVICE_NAME=Survey Genie
AUTH_MODE=local
LOCAL_USERS_FILE=users.json
SESSION_COOKIE_SECURE=false
SURVEY_DEFINITION_FILE=/absolute/path/to/survey.json
```

## Google Cloud Storage authentication

```text
AUTH_MODE=gcs
GCP_AUTH_BUCKET_NAME=your-auth-bucket
GCP_AUTH_BLOB_NAME=users.json
SESSION_COOKIE_SECURE=true
```

The Cloud Run service account must be able to read the configured object. Supply `FLASK_SECRET_KEY` through Secret Manager rather than embedding it in an image or source file.
