"""Main UI routes."""

from __future__ import annotations

from http import HTTPStatus
import logging
from typing import cast

from flask import Blueprint, abort, current_app, render_template, session, url_for
from flask.typing import ResponseReturnValue

from survey_genie.auth.decorators import SESSION_USER_KEY, login_required
from survey_genie.survey.models import SurveyDefinition
from survey_genie.survey.session import clear_survey_session_data


def _get_survey_definition() -> SurveyDefinition:
    """Return the survey definition loaded during application startup.

    Returns:
        SurveyDefinition: Configured survey definition.
    """
    return cast(
        SurveyDefinition,
        current_app.extensions["survey_definition"],
    )


def _get_survey_start_url(
    survey_definition: SurveyDefinition,
) -> str | None:
    """Return the first available URL in the configured survey journey.

    Args:
        survey_definition: Validated survey definition.

    Returns:
        str | None: Introduction or first survey-page URL, or None when
            neither section is enabled.
    """
    if survey_definition["survey_intro"]["enabled"]:
        return url_for("main.start")

    survey_pages = survey_definition["survey_pages"]

    if not survey_pages["enabled"]:
        return None

    start_page_id = survey_pages["start_page_id"]
    start_page = next(page for page in survey_pages["pages"] if page["page_id"] == start_page_id)

    endpoint = "survey.guidance" if start_page["page_type"] == "guidance" else "survey.question"

    return url_for(
        endpoint,
        page_id=start_page_id,
    )


logger = logging.getLogger(__name__)

main_blueprint = Blueprint("main", __name__)


@main_blueprint.get("/")
@login_required
def index() -> ResponseReturnValue:
    """Render the protected landing page.

    Returns:
        ResponseReturnValue: Home page template response.
    """
    removed_keys = clear_survey_session_data()

    if removed_keys:
        logger.info(
            "Cleared survey session data keys=%s",
            sorted(removed_keys),
        )

    survey_definition = _get_survey_definition()

    return render_template(
        "index.html",
        page_title="Home",
        authenticated_user=session.get(SESSION_USER_KEY),
        survey_start_url=_get_survey_start_url(survey_definition),
    )


@main_blueprint.get("/start")
@login_required
def start() -> ResponseReturnValue:
    """Render the configured survey introduction page.

    Returns:
        ResponseReturnValue: Survey introduction template response.

    Raises:
        NotFound: If the survey introduction is disabled.
    """
    survey_definition = _get_survey_definition()
    survey_intro = survey_definition["survey_intro"]

    if not survey_intro["enabled"]:
        abort(HTTPStatus.NOT_FOUND)

    intro = survey_intro.get("intro")
    if intro is None:
        logger.error(
            "Enabled survey introduction has no content",
            extra={"wave_id": survey_definition["wave_id"]},
        )
        abort(HTTPStatus.INTERNAL_SERVER_ERROR)

    navigation_items = [
        {
            "url": entry["link"],
            "text": entry["text"],
        }
        for entry in intro["navigation"]["entries"]
    ]

    survey_page_urls = {
        page["page_id"]: url_for(
            ("survey.guidance" if page["page_type"] == "guidance" else "survey.question"),
            page_id=page["page_id"],
        )
        for page in survey_definition["survey_pages"]["pages"]
    }

    return render_template(
        "survey_intro.html",
        page_title=survey_definition["survey_title"],
        survey=survey_definition,
        intro=intro,
        navigation_items=navigation_items,
        survey_page_urls=survey_page_urls,
        authenticated_user=session.get(SESSION_USER_KEY),
    )


@main_blueprint.get("/cookies")
def cookies() -> ResponseReturnValue:
    """Render the cookies page.

    Returns:
        ResponseReturnValue: Cookies page template response.
    """
    return render_template("cookies.html", page_title="Cookies")


@main_blueprint.get("/accessibility")
def accessibility() -> ResponseReturnValue:
    """Render the accessibility statement page.

    Returns:
        ResponseReturnValue: Accessibility statement template response.
    """
    return render_template("accessibility.html", page_title="Accessibility statement")


@main_blueprint.get("/privacy")
def privacy() -> ResponseReturnValue:
    """Render the privacy notice page.

    Returns:
        ResponseReturnValue: Privacy notice template response.
    """
    return render_template("privacy.html", page_title="Privacy notice")


@main_blueprint.get("/health")
def health() -> ResponseReturnValue:
    """Provide a basic health check response.

    Returns:
        ResponseReturnValue: JSON payload indicating service health.
    """
    return {"status": "ok"}
