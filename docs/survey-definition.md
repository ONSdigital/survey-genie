# Survey definitions

Survey definitions are loaded by `load_survey_definition()` in `src/survey_genie/survey/loader.py` and represented by the `TypedDict` models in `src/survey_genie/survey/models.py`.

Only schema version `1` is supported.

## Root structure

```json
{
  "schema_version": 1,
  "survey_title": "Example survey",
  "wave_id": "example-wave",
  "survey_intro": {
    "enabled": true,
    "intro": {
      "navigation": {
        "header": "In this section",
        "aria_label": "Sections in this page",
        "entries": []
      },
      "sections": []
    }
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

`survey_feedback` is optional. `survey_intro.intro` is required only when the introduction is enabled.

## Introduction

The introduction is one page containing navigation and ordered sections.

```json
{
  "survey_intro": {
    "enabled": true,
    "intro": {
      "navigation": {
        "header": "In this section",
        "aria_label": "Sections in this page",
        "entries": [
          {
            "link": "#start",
            "text": "Start the survey"
          }
        ]
      },
      "sections": [
        {
          "id": "start",
          "heading": "Start the survey",
          "blocks": []
        }
      ]
    }
  }
}
```

Section IDs use lowercase letters, numbers and hyphens. Navigation links must refer to defined section IDs.

### Paragraph block

Paragraphs support inline `text` and `link` items.

```json
{
  "type": "paragraph",
  "content": [
    {
      "type": "text",
      "text": "Read our "
    },
    {
      "type": "link",
      "text": "privacy information",
      "link": "/privacy",
      "new_window": false
    }
  ]
}
```

Supported links are anchors, root-relative paths, `https` URLs and `mailto` links.

### Button block

A button must define exactly one of `link` or `target_page_id`.

```json
{
  "type": "button",
  "text": "Start now",
  "target_page_id": "q1",
  "variants": ["loader"]
}
```

### Panel block

```json
{
  "type": "panel",
  "variant": "info",
  "heading": "Before you start",
  "paragraphs": [
    [
      {
        "type": "text",
        "text": "Your answers are confidential."
      }
    ]
  ]
}
```

Supported panel variants are:

- `info`
- `warn`
- `warn-branded`
- `pending`

## Survey pages

`survey_pages.pages` is an ordered, linear journey. `start_page_id` must match one page. Supported page types are `question` and `guidance`.

### Radio question

```json
{
  "page_id": "q1",
  "page_type": "question",
  "page_title": "Employment status",
  "question_name": "employment_status",
  "question": {
    "text": "Are you currently employed?",
    "description": "Include self-employment."
  },
  "answer": {
    "type": "radio",
    "name": "employment-status",
    "required": true,
    "options": [
      {
        "id": "employment-status-yes",
        "label": "Yes",
        "value": "yes"
      },
      {
        "id": "employment-status-no",
        "label": "No",
        "value": "no"
      }
    ]
  },
  "submit_button": {
    "text": "Save and continue"
  }
}
```

Radio option IDs and values must be unique within the question.

### Text question

A text answer is rendered with `onsInput` unless `multiline` is `true`, when it is rendered with `onsTextarea`.

```json
{
  "page_id": "q2",
  "page_type": "question",
  "page_title": "Job title",
  "question_name": "job_title",
  "question": {
    "text": "What is your job title?",
    "guidance": {
      "content": "Use the title shown on your contract."
    },
    "justification": {
      "title": "Why we ask this question",
      "content": "This helps us classify occupations."
    }
  },
  "answer": {
    "type": "text",
    "name": "job-title",
    "required": true,
    "multiline": false,
    "character_limit": 150,
    "placeholder": ""
  },
  "submit_button": {
    "text": "Save and continue"
  }
}
```

For multiline text:

```json
{
  "type": "text",
  "name": "job-description",
  "required": true,
  "multiline": true,
  "rows": 8,
  "character_limit": 500
}
```

`rows` is valid only when `multiline` is `true`.

### Question placeholders

A question can include a response from an earlier question.

```json
{
  "text": "Describe what you do as a JOB_TITLE",
  "placeholders": [
    {
      "placeholder": "JOB_TITLE",
      "source_question_name": "job_title"
    }
  ]
}
```

The source must be a preceding question. When its response is unavailable, the journey redirects to that earlier question.

### Guidance page

```json
{
  "page_id": "g1",
  "page_type": "guidance",
  "page_title": "Before the next section",
  "guidance_overview": "The next questions are about your organisation.",
  "guidance_subsection": "Answer for your main job.",
  "continue_button": {
    "text": "Continue"
  }
}
```

## Feedback

Feedback is optional and follows the final survey page when enabled.

Feedback supports `question` pages only. Answer types are:

- `radio`, required or optional
- `text`, which must have `"required": false`

```json
{
  "survey_feedback": {
    "enabled": true,
    "start_page_id": "f1",
    "pages": [
      {
        "page_id": "f1",
        "page_type": "question",
        "page_title": "Survey feedback",
        "question_name": "feedback_comment",
        "question": {
          "text": "How could we improve this survey?"
        },
        "answer": {
          "type": "text",
          "name": "feedback-comment",
          "required": false,
          "multiline": true,
          "rows": 5,
          "character_limit": 500
        },
        "submit_button": {
          "text": "Continue"
        }
      }
    ]
  }
}
```

Blank optional feedback responses are not retained.

## Journey and response behaviour

Routes are implemented in `src/survey_genie/routes/survey.py`:

- `/start/questions/<page_id>`
- `/start/guidance/<page_id>`
- `/start/feedback/<page_id>`
- `/start/complete`

Pages run in array order. There is no conditional routing.

Survey and feedback responses are stored separately in the Flask session. The `complete()` route logs both collections with the configured `wave_id`; it does not save them to persistent storage.
