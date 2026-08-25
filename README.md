# Survey Genie

Survey Genie is a lightweight Flask framework for running JSON-configured survey prototypes with the [ONS Design System](https://service-manual.ons.gov.uk/design-system).

It currently supports:

- an optional introduction page
- an ordered survey journey containing question and guidance pages
- an optional feedback journey
- a fixed completion page
- local-file or Google Cloud Storage password authentication
- session-backed responses for prototype use

> Survey Genie is intended for short-lived prototypes and small-scale testing. It does not currently persist survey responses to a database or provide production-grade identity management.

## Requirements

- Python 3.12
- Poetry 2.1.3
- Make
- Docker or Podman, when running the container locally

## Run locally

```bash
git clone https://github.com/ONSdigital/survey-genie.git
cd survey-genie

cp .env.example .env
make install
make templates
make provision-user
make run
```

Open `http://127.0.0.1:5000` and sign in with the user created by `make provision-user`.

To use a custom survey definition, set an absolute path in `.env`:

```text
SURVEY_DEFINITION_FILE=/absolute/path/to/survey.json
```

Useful Makefile targets:

```bash
make help                 # list available targets
make install              # install Poetry dependencies
make templates            # download ONS Design System templates
make provision-user       # create a local users.json
make run                  # run Flask in debug mode
make run-docs             # serve the MkDocs documentation
make all-tests            # run tests with coverage
make check-python-nofix   # run formatting, lint, type and security checks
make docker-build
make docker-run
make podman-build
make podman-run
```

## Environment variables

| Variable | Required | Default | Purpose |
|---|---:|---|---|
| `FLASK_SECRET_KEY` | Production: yes | `dev-only-change-me` | Signs Flask sessions. Use a strong secret outside local development. |
| `SERVICE_NAME` | No | `Survey Genie` | Service name displayed by the application. |
| `AUTH_MODE` | No | `local` | Authentication source: `local` or `gcs`. |
| `LOCAL_USERS_FILE` | Local auth: yes | `users.json` | Path to the local password-hash file. Use `/app/users.json` in the supplied container. |
| `GCP_AUTH_BUCKET_NAME` | GCS auth: yes | None | Google Cloud Storage bucket containing the users file. |
| `GCP_AUTH_BLOB_NAME` | No | `users.json` | Object name within the authentication bucket. |
| `SESSION_COOKIE_SECURE` | No | `false` | Set to `true` when served over HTTPS. |
| `SURVEY_DEFINITION_FILE` | No | bundled `example_survey.json` | JSON survey definition loaded and validated at application startup. |

## Survey definitions

A definition uses schema version `1` and has three configurable journey sections:

```json
{
  "schema_version": 1,
  "survey_title": "Example survey",
  "wave_id": "example-wave",
  "survey_intro": {
    "enabled": true,
    "intro": {}
  },
  "survey_pages": {
    "enabled": true,
    "start_page_id": "q1",
    "pages": []
  },
  "survey_feedback": {
    "enabled": true,
    "start_page_id": "f1",
    "pages": []
  }
}
```

When `survey_intro.enabled` is `true`, the landing-page **Start survey**
button opens the introduction page.

When `survey_intro.enabled` is `false` and `survey_pages.enabled` is `true`,
the button links directly to the page identified by
`survey_pages.start_page_id`.

The button is not displayed when both sections are disabled.


Supported survey page types:

- `question`
- `guidance`

Supported answer types for survey questions:

- `radio`
- `text`, rendered as either a single-line input or multiline textarea
- text answers may define an optional `label`
- questions may define optional `definition`, `guidance` and `justification` content

Supported feedback pages:

- `question` pages only
- `radio` answers, required or optional
- `text` answers, optional only

Supported introduction blocks:

- `paragraph`, containing inline text and links
- `button`, linking to a URL or survey page
- `panel`
- table-of-contents navigation to introduction sections

See [Survey definitions](docs/survey-definition.md) for the complete supported structure and examples.

## ONS Design System components

Survey Genie renders the journey using these ONS Design System macros:

- `onsButton`
- `onsPanel`
- `onsTableOfContents`
- `onsQuestion`
- `onsRadios`
- `onsInput`
- `onsTextarea`

Application templates must continue to use ONS macros rather than hand-written form controls.

## Documentation

```bash
make run-docs
```

The detailed documentation is under [`docs/`](docs/index.md).

## Current limitations

- Responses are stored in the Flask session and logged when the completion page is reached.
- There is no database or response export.
- Page order is linear; conditional routing is not supported.
- Survey and feedback definitions are loaded only at application startup.
- The completion page is currently fixed rather than JSON-configurable.
- Authentication is suitable for prototypes, not a replacement for centrally managed SSO or IAP.

## Development checks

```bash
make all-tests
make check-python-nofix
```
