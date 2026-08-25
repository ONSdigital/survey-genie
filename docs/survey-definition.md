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
        "value": "no",
        "target_page_id": "g2"
      }
    ]
  },
  "submit_button": {
    "text": "Save and continue"
  }
}
```

Radio option IDs and values must be unique within the question.

A radio option may define an optional `target_page_id`. When that option is
selected, the journey continues at the target rather than at the next page in
array order.

The target:

- must be in the same section as the radio question
- must appear later in that section's `pages` array
- may identify either a question or guidance page in `survey_pages`
- may identify a later feedback question in `survey_feedback`

Options without `target_page_id` continue to the next configured page.

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
    "definition": {
      "title": "What we mean by job",
      "content": "A job is paid employment or self-employment."
    },
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
    "label": "Job title",
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

`definition` is optional. When supplied, it is passed to the ONS question
component and displayed as supporting definition content.

A definition contains:

- `title` - the definition heading
- `content` - the definition content


`label` is optional for text answers. When supplied, it is displayed as the
label for the `onsInput` or `onsTextarea` component.

The same property is supported for multiline answers:

```json
{
  "type": "text",
  "name": "job-description",
  "label": "Job description",
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

### Previous question navigation

Question pages follow the ONS question pattern and display a `Previous` link
when the respondent has previously answered another question in the same
section.

The first survey question and first feedback question do not display a
`Previous` link.

`Previous` returns to the most recently answered question in the current
journey, including when conditional routing has skipped questions.

When a respondent selects `Previous`, any saved answer for the current
question is discarded. If they return to that question later, they must
answer it again.

Survey and feedback navigation are separate. The first feedback question
does not provide a `Previous` link back to the survey.

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

The landing-page **Start survey** button selects the first available journey
step:

1. The introduction page when `survey_intro.enabled` is `true`.
2. The question or guidance page identified by
   `survey_pages.start_page_id` when the introduction is disabled and
   `survey_pages.enabled` is `true`.
3. No button when both sections are disabled.

An enabled survey section must contain at least one page, and
`start_page_id` must match a configured page.

Routes are implemented in `src/survey_genie/routes/survey.py`:

- `/start/questions/<page_id>`
- `/start/guidance/<page_id>`
- `/start/feedback/<page_id>`
- `/start/complete`

Pages normally run in array order. Radio options may skip forwards by defining
`target_page_id`. Routing cannot move backwards or cross between
`survey_pages` and `survey_feedback`.

Survey and feedback responses are stored separately in the Flask session. The `complete()` route logs both collections with the configured `wave_id`; it does not save them to persistent storage.
