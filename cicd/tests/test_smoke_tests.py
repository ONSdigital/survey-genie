"""Smoke Tests for the GENIE UI."""

import os

import requests


class TestGenieUI:  # pylint: disable=too-few-public-methods
    """Smoke Tests for the Genie UI."""

    target_environment = os.environ.get("TARGET_ENVIRONMENT")
    if target_environment is None:
        print(
            """TARGET_ENVIRONMENT environment variable is not set.
            Optionally, set this to select the environment to proxy
            i.e. sandbox(default), dev or preprod."""
        )
        target_environment = "sandbox"

    url_base = os.environ.get("GENIE_UI_URL")
    if url_base is None:
        raise ValueError("GENIE_UI_URL environment variable is not set.")

    id_token = os.environ.get("UI_SA_ID_TOKEN")
    if id_token is None:
        raise ValueError("UI_SA_ID_TOKEN environment variable is not set.")

    def test_survey_assist_api_status(self) -> None:
        """Test GENIE UI returns successful response (via proxy API)."""
        endpoint = f"{self.url_base}/genie-ui/{self.target_environment}"

        print(f"Calling {endpoint}...")
        response = requests.get(
            endpoint,
            headers={"Authorization": f"Bearer {self.id_token}"},
            timeout=30,
        )

        print("Checking status code is 200..")
        assert (
            response.status_code == 200  # noqa: PLR2004
        ), f"Expected status code 200, but got {response.status_code}."
