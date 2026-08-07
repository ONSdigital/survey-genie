"""Tests for configurable survey routes."""

from http import HTTPStatus
from typing import cast

from flask import Flask
from flask.testing import FlaskClient

from survey_genie.auth.decorators import SESSION_USER_KEY
from survey_genie.routes.survey import SURVEY_RESPONSES_KEY
from survey_genie.survey.models import (
    GuidancePage,
    SurveyDefinition,
    SurveyFeedback,
)
from survey_genie.survey.session import SURVEY_FEEDBACK_RESPONSES_KEY


def _authenticate(client: FlaskClient) -> None:
    """Authenticate the Flask test client.

    Args:
        client: Flask test client to authenticate.
    """
    with client.session_transaction() as flask_session:
        flask_session[SESSION_USER_KEY] = "person@example.com"


def _insert_guidance_page(
    app: Flask,
    page: GuidancePage,
    index: int,
) -> None:
    """Insert guidance into the configured survey.

    Args:
        app: Configured Flask application.
        page: Guidance page to insert.
        index: Position in the ordered page list.
    """
    survey_definition = cast(
        SurveyDefinition,
        app.extensions["survey_definition"],
    )
    survey_definition["survey_pages"]["pages"].insert(
        index,
        page,
    )


def test_first_question_renders(client: FlaskClient) -> None:
    """Test that the first configured question renders."""
    _authenticate(client)

    response = client.get("/start/questions/q0")
    response_text = response.get_data(as_text=True)

    assert response.status_code == HTTPStatus.OK
    assert "Select your age range from the options below" in response_text
    assert "16-24" in response_text
    assert "25-34" in response_text


def test_invalid_question_page_returns_not_found(
    client: FlaskClient,
) -> None:
    """Test that an unknown question page returns not found."""
    _authenticate(client)

    response = client.get("/start/questions/missing")

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_required_response_returns_bad_request(
    client: FlaskClient,
) -> None:
    """Test that an empty required response is rejected."""
    _authenticate(client)

    response = client.post(
        "/start/questions/q0",
        data={},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_radio_value_outside_configured_options_returns_bad_request(
    client: FlaskClient,
) -> None:
    """Test that an unconfigured radio value is rejected."""
    _authenticate(client)

    response = client.post(
        "/start/questions/q0",
        data={"age-range": "not-configured"},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_response_is_saved_in_session(
    client: FlaskClient,
) -> None:
    """Test that a valid response is stored in the session."""
    _authenticate(client)

    client.post(
        "/start/questions/q0",
        data={"age-range": "25-34"},
    )

    with client.session_transaction() as flask_session:
        responses = cast(
            dict[str, dict[str, str]],
            flask_session[SURVEY_RESPONSES_KEY],
        )

    assert responses["q0"] == {
        "question_name": "age_range_question",
        "response_name": "age-range",
        "value": "25-34",
    }


def test_first_question_redirects_to_second_question(
    client: FlaskClient,
) -> None:
    """Test that the first question redirects to the next question."""
    _authenticate(client)

    response = client.post(
        "/start/questions/q0",
        data={"age-range": "16-24"},
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"].endswith("/start/questions/q1")


def test_final_question_redirects_to_completion(
    client: FlaskClient,
) -> None:
    """Test that the final question redirects to completion."""
    _authenticate(client)

    with client.session_transaction() as flask_session:
        flask_session[SURVEY_RESPONSES_KEY] = {
            "q1": {
                "question_name": "job_title_question",
                "response_name": "job-title",
                "value": "Primary school teacher",
            }
        }

    response = client.post(
        "/start/questions/q2",
        data={"job-description": ("I plan lessons and teach primary school pupils.")},
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"].endswith("/start/complete")


def test_saved_response_is_repopulated_when_revisiting_page(
    client: FlaskClient,
) -> None:
    """Test that a previously saved response is rendered again."""
    _authenticate(client)

    with client.session_transaction() as flask_session:
        flask_session[SURVEY_RESPONSES_KEY] = {
            "q1": {
                "question_name": "job_title_question",
                "response_name": "job-title",
                "value": "Primary school teacher",
            }
        }

    response = client.get("/start/questions/q1")

    assert response.status_code == HTTPStatus.OK
    assert "Primary school teacher" in response.get_data(as_text=True)


def test_question_renders_saved_response_in_placeholder(
    client: FlaskClient,
) -> None:
    """Test that saved answers appear in later question text."""
    _authenticate(client)

    with client.session_transaction() as flask_session:
        flask_session[SURVEY_RESPONSES_KEY] = {
            "q1": {
                "question_name": "job_title_question",
                "response_name": "job-title",
                "value": "Primary school teacher",
            }
        }

    response = client.get("/start/questions/q2")
    response_text = response.get_data(as_text=True)

    assert response.status_code == HTTPStatus.OK
    assert "as a primary school teacher" in response_text
    assert "PLACEHOLDER_TEXT" not in response_text


def test_question_redirects_when_placeholder_response_is_missing(
    client: FlaskClient,
) -> None:
    """Test that missing source answers redirect to their question."""
    _authenticate(client)

    response = client.get("/start/questions/q2")

    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"].endswith("/start/questions/q1")


def test_final_survey_page_redirects_to_feedback(
    app: Flask,
    client: FlaskClient,
    survey_feedback: SurveyFeedback,
) -> None:
    """Test that enabled feedback follows the survey journey."""
    _authenticate(client)
    survey_definition = cast(
        SurveyDefinition,
        app.extensions["survey_definition"],
    )
    survey_definition["survey_feedback"] = survey_feedback

    with client.session_transaction() as flask_session:
        flask_session[SURVEY_RESPONSES_KEY] = {
            "q1": {
                "question_name": "job_title_question",
                "response_name": "job-title",
                "value": "Teacher",
            }
        }

    response = client.post(
        "/start/questions/q2",
        data={
            "job-description": "Teaching pupils",
        },
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"].endswith("/start/feedback/fq1")


def test_feedback_response_is_stored_separately(
    app: Flask,
    client: FlaskClient,
    survey_feedback: SurveyFeedback,
) -> None:
    """Test that feedback does not modify survey responses."""
    _authenticate(client)
    survey_definition = cast(
        SurveyDefinition,
        app.extensions["survey_definition"],
    )
    survey_definition["survey_feedback"] = survey_feedback

    with client.session_transaction() as flask_session:
        flask_session[SURVEY_RESPONSES_KEY] = {
            "q0": {
                "question_name": "age_range_question",
                "response_name": "age-range",
                "value": "25-34",
            }
        }

    response = client.post(
        "/start/feedback/fq1",
        data={"survey-ease": "easy"},
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"].endswith("/start/feedback/fq2")

    with client.session_transaction() as flask_session:
        assert flask_session[SURVEY_RESPONSES_KEY]["q0"]["value"] == "25-34"
        assert flask_session[SURVEY_FEEDBACK_RESPONSES_KEY]["fq1"] == {
            "question_name": "survey_ease_question",
            "response_name": "survey-ease",
            "value": "easy",
        }


def test_optional_feedback_text_can_be_skipped(
    app: Flask,
    client: FlaskClient,
    survey_feedback: SurveyFeedback,
) -> None:
    """Test that optional text feedback can be submitted empty."""
    _authenticate(client)
    survey_definition = cast(
        SurveyDefinition,
        app.extensions["survey_definition"],
    )
    survey_definition["survey_feedback"] = survey_feedback

    response = client.post(
        "/start/feedback/fq2",
        data={"other-feedback": ""},
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"].endswith("/start/complete")

    with client.session_transaction() as flask_session:
        feedback_responses = flask_session.get(
            SURVEY_FEEDBACK_RESPONSES_KEY,
            {},
        )

    assert "fq2" not in feedback_responses


def test_optional_feedback_textarea_is_not_required(
    app: Flask,
    client: FlaskClient,
    survey_feedback: SurveyFeedback,
) -> None:
    """Test that optional feedback text omits the required attribute."""
    _authenticate(client)

    survey_definition = cast(
        SurveyDefinition,
        app.extensions["survey_definition"],
    )
    survey_definition["survey_feedback"] = survey_feedback

    response = client.get("/start/feedback/fq2")
    response_text = response.get_data(as_text=True)

    textarea_start = response_text.index("<textarea")
    textarea_end = response_text.index(">", textarea_start)
    textarea_tag = response_text[textarea_start : textarea_end + 1]

    assert response.status_code == HTTPStatus.OK
    assert 'name="other-feedback"' in textarea_tag
    assert "required" not in textarea_tag


def test_guidance_page_renders(
    app: Flask,
    client: FlaskClient,
    guidance_page: GuidancePage,
) -> None:
    """Test that a configured guidance page renders."""
    _authenticate(client)
    _insert_guidance_page(
        app,
        guidance_page,
        index=1,
    )

    response = client.get("/start/guidance/g1")
    response_text = response.get_data(as_text=True)

    assert response.status_code == HTTPStatus.OK
    assert "Describing your work" in response_text
    assert "The next questions ask about" in response_text
    assert "Continue" in response_text


def test_question_redirects_to_following_guidance(
    app: Flask,
    client: FlaskClient,
    guidance_page: GuidancePage,
) -> None:
    """Test that question progression supports guidance."""
    _authenticate(client)
    _insert_guidance_page(
        app,
        guidance_page,
        index=1,
    )

    response = client.post(
        "/start/questions/q0",
        data={"age-range": "16-24"},
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"].endswith("/start/guidance/g1")


def test_guidance_links_to_following_question(
    app: Flask,
    client: FlaskClient,
    guidance_page: GuidancePage,
) -> None:
    """Test that guidance continues to the next question."""
    _authenticate(client)
    _insert_guidance_page(
        app,
        guidance_page,
        index=1,
    )

    response = client.get("/start/guidance/g1")
    response_text = response.get_data(as_text=True)

    assert response.status_code == HTTPStatus.OK
    assert "/start/questions/q1" in response_text


def test_final_guidance_links_to_feedback(
    app: Flask,
    client: FlaskClient,
    guidance_page: GuidancePage,
    survey_feedback: SurveyFeedback,
) -> None:
    """Test that final guidance continues to enabled feedback."""
    _authenticate(client)

    survey_definition = cast(
        SurveyDefinition,
        app.extensions["survey_definition"],
    )
    survey_definition["survey_pages"]["pages"].append(guidance_page)
    survey_definition["survey_feedback"] = survey_feedback

    response = client.get("/start/guidance/g1")
    response_text = response.get_data(as_text=True)

    assert response.status_code == HTTPStatus.OK
    assert "/start/feedback/fq1" in response_text


def test_final_guidance_links_to_completion(
    app: Flask,
    client: FlaskClient,
    guidance_page: GuidancePage,
) -> None:
    """Test that final guidance continues to completion."""
    _authenticate(client)

    survey_definition = cast(
        SurveyDefinition,
        app.extensions["survey_definition"],
    )
    survey_definition["survey_pages"]["pages"].append(guidance_page)

    response = client.get("/start/guidance/g1")
    response_text = response.get_data(as_text=True)

    assert response.status_code == HTTPStatus.OK
    assert "/start/complete" in response_text


def test_radio_response_routes_to_target_question(
    app: Flask,
    client: FlaskClient,
) -> None:
    """Test that a radio option can skip to a later question."""
    _authenticate(client)
    survey_definition = cast(
        SurveyDefinition,
        app.extensions["survey_definition"],
    )
    first_page = cast(
        dict[str, object],
        survey_definition["survey_pages"]["pages"][0],
    )
    answer = cast(
        dict[str, object],
        first_page["answer"],
    )
    options = cast(
        list[dict[str, object]],
        answer["options"],
    )
    options[0]["target_page_id"] = "q2"

    response = client.post(
        "/start/questions/q0",
        data={"age-range": "16-24"},
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"].endswith("/start/questions/q2")


def test_radio_response_routes_to_target_guidance(
    app: Flask,
    client: FlaskClient,
    guidance_page: GuidancePage,
) -> None:
    """Test that a radio option can skip to later guidance."""
    _authenticate(client)
    survey_definition = cast(
        SurveyDefinition,
        app.extensions["survey_definition"],
    )
    pages = survey_definition["survey_pages"]["pages"]
    pages.insert(2, guidance_page)

    first_page = cast(
        dict[str, object],
        pages[0],
    )
    answer = cast(
        dict[str, object],
        first_page["answer"],
    )
    options = cast(
        list[dict[str, object]],
        answer["options"],
    )
    options[1]["target_page_id"] = "g1"

    response = client.post(
        "/start/questions/q0",
        data={"age-range": "25-34"},
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"].endswith("/start/guidance/g1")


def test_feedback_radio_routes_to_target_question(
    app: Flask,
    client: FlaskClient,
    survey_feedback: SurveyFeedback,
) -> None:
    """Test that feedback radio routing skips intermediate feedback."""
    _authenticate(client)
    survey_definition = cast(
        SurveyDefinition,
        app.extensions["survey_definition"],
    )

    first_feedback_page = survey_feedback["pages"][0]
    first_answer = cast(
        dict[str, object],
        first_feedback_page["answer"],
    )
    options = cast(
        list[dict[str, object]],
        first_answer["options"],
    )
    options[0]["target_page_id"] = "fq3"

    survey_feedback["pages"].append(
        {
            "page_id": "fq3",
            "page_type": "question",
            "page_title": "Final feedback",
            "question_name": "final_feedback_question",
            "question": {
                "text": "Would you use this survey again?",
            },
            "answer": {
                "type": "radio",
                "name": "use-again",
                "required": True,
                "options": [
                    {
                        "id": "use-again-yes",
                        "label": "Yes",
                        "value": "yes",
                    },
                    {
                        "id": "use-again-no",
                        "label": "No",
                        "value": "no",
                    },
                ],
            },
            "submit_button": {
                "text": "Submit feedback",
            },
        }
    )
    survey_definition["survey_feedback"] = survey_feedback

    response = client.post(
        "/start/feedback/fq1",
        data={"survey-ease": "easy"},
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"].endswith("/start/feedback/fq3")
