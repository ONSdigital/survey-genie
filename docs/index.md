# Survey Genie

Survey Genie is a lightweight JSON-configured survey framework built with Flask and the ONS Design System.

## Current capabilities

- Optional introduction page with navigation, paragraphs, links, buttons and panels
- Ordered survey journey with question and guidance pages
- Radio, single-line text and multiline text answers
- Question descriptions, guidance, justification and placeholders
- Optional feedback journey with radio or optional text questions
- Fixed completion page
- Local-file or Google Cloud Storage authentication
- Session-backed prototype responses

## Documentation

- [Getting started](getting-started.md)
- [Environment variables](environment-variables.md)
- [Survey definitions](survey-definition.md)
- [Supported ONS components](ons-components.md)

## Scope

The application is intended for prototypes and small-scale testing. Survey responses are held in the Flask session and logged at completion; they are not persisted to a database.
