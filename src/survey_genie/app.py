"""Flask application factory for Survey Genie."""

from __future__ import annotations

import logging
from pathlib import Path

from flask import Flask
from jinja2 import ChainableUndefined, ChoiceLoader, FileSystemLoader

from .auth.routes import auth_blueprint
from .auth.service import AuthService, build_auth_store
from .config import Settings, load_settings
from .routes.main import main_blueprint
from .routes.survey import survey_blueprint
from .survey.loader import SurveyDefinitionError, load_survey_definition
from .survey.models import SurveyDefinition

logger = logging.getLogger(__name__)


def create_app(
    settings: Settings | None = None,
    auth_service: AuthService | None = None,
    survey_definition: SurveyDefinition | None = None,
) -> Flask:
    """Create and configure the Survey Genie application.

    Args:
        settings: Optional runtime settings.
        auth_service: Optional authentication service implementation.
        survey_definition: Optional preloaded definition, primarily for tests.

    Returns:
        Configured Flask application.

    Raises:
        RuntimeError: If the configured survey definition cannot be loaded.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        force=True,
    )

    resolved_settings = settings or load_settings()
    resolved_definition = survey_definition

    if resolved_definition is None:
        survey_path = Path(resolved_settings.survey_definition_file)

        try:
            resolved_definition = load_survey_definition(survey_path)
        except SurveyDefinitionError as exc:
            logger.exception(
                "Failed to load survey definition from %s",
                survey_path,
            )
            raise RuntimeError(f"Unable to start with survey definition {survey_path}") from exc

        logger.info(
            "Loaded survey definition from %s with schema version %s",
            survey_path,
            resolved_definition["schema_version"],
        )

    app = Flask(__name__, template_folder="app_templates")
    app.jinja_env.undefined = ChainableUndefined

    design_templates = Path(__file__).parent / "templates"
    loaders = []

    if app.jinja_loader is not None:
        loaders.append(app.jinja_loader)

    loaders.append(FileSystemLoader(str(design_templates)))
    app.jinja_loader = ChoiceLoader(loaders)

    app.secret_key = resolved_settings.secret_key
    app.config["settings"] = resolved_settings
    app.config["auth_service"] = auth_service or AuthService(build_auth_store(resolved_settings))

    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=resolved_settings.session_cookie_secure,
    )

    app.extensions["survey_definition"] = resolved_definition

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(survey_blueprint)

    @app.context_processor
    def inject_template_context() -> dict[str, Settings | str]:
        """Expose application configuration within templates.

        Returns:
            Template context containing application configuration.
        """
        return {
            "settings": resolved_settings,
            "service_name": resolved_definition["survey_title"],
        }

    logger.info(
        "Created Survey Genie application with auth_mode=%s",
        resolved_settings.auth_mode,
    )

    return app
