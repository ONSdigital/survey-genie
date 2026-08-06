# Supported ONS Design System components

Survey Genie uses downloaded ONS Design System Nunjucks macros through Jinja. Run:

```bash
make templates
```

The current survey templates use:

| Macro | Used for | Template |
|---|---|---|
| `onsButton` | Introduction actions, guidance continuation and question submission | `survey_intro.html`, `survey_guidance.html`, `survey_question.html` |
| `onsPanel` | Introduction information panels and completion messaging | `survey_intro.html`, `survey_complete.html` |
| `onsTableOfContents` | Introduction section navigation | `survey_intro.html` |
| `onsQuestion` | Question title, description, guidance, justification and errors | `survey_question.html` |
| `onsRadios` | Radio answer questions | `survey_question.html` |
| `onsInput` | Single-line text answers | `survey_question.html` |
| `onsTextarea` | Multiline text answers | `survey_question.html` |

## Authoring rule

New controls and patterns should use an existing ONS Design System macro or component. Do not replace supported macros with hand-written HTML form controls.

The JSON schema currently exposes only the components and configurations documented here. Adding another ONS component requires coordinated updates to:

- `src/survey_genie/survey/models.py`
- `src/survey_genie/survey/loader.py`
- the relevant template under `src/survey_genie/app_templates/`
- route handling in `src/survey_genie/routes/survey.py`, where submission behaviour changes
- tests and these documentation pages
