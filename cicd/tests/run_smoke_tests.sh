#!/bin/bash

# Wrapper script to run the smoke tests locally
#
# Expected Env variables:
# CICD_PROJECT_ID - The project id for the CICD project
# GENIE_UI_URL - The URL of the Survey Assist UI to run the tests against
# UI_SA_ID_TOKEN - A valid Google Identity Token generated from your credentials (assuming you're running locally)
#
#
# Expected parameter: [sandbox|dev|preprod]
#
# Example ./run_smoke_tests.sh dev

# Please set the environment variable CICD_PROJECT_ID i.e. export CICD_PROJECT_ID=

if [[ -z "${CICD_PROJECT_ID:-}" ]]; then
   echo "Please set the environment variable CICD_PROJECT_ID i.e. export CICD_PROJECT_ID="
   exit 1
fi

if [[ $1 = "sandbox" ]] || [[ $1 = "dev" ]] || [[ $1 = "preprod" ]]; then
   echo Test environment "$1"
   export TARGET_ENVIRONMENT=$1
else
  echo "Please pass test environment of 'sandbox', 'dev' or 'preprod' e.g. ./run_smoke_tests.sh sandbox"
  exit 1
fi

if [[ -z "${GENIE_UI_URL}" ]]; then
    echo Environment variable GENIE_UI_URL was not set, getting ${1} url from parameter store:
    GENIE_UI_URL=$(gcloud parametermanager parameters versions describe ${1} --parameter=infra-test-config --location=global --project ${CICD_PROJECT_ID} --format=json | python3 -c "import sys, json; print(json.load(sys.stdin)['payload']['data'])" | base64 --decode | python3 -c "import sys, json; print(json.load(sys.stdin)['proxy-api-url'])")
    export GENIE_UI_URL
    echo "$GENIE_UI_URL"
else
    echo Using GENIE_UI_URL="$GENIE_UI_URL"
fi
#
# Example way to set token after gcloud auth login
# export UI_SA_ID_TOKEN=`gcloud auth print-identity-token`
if [[ -z "${UI_SA_ID_TOKEN}" ]]; then
    echo Environment variable UI_SA_ID_TOKEN was not set, getting a new identity token from local credentials, if authenticated.
    UI_SA_ID_TOKEN=$(gcloud auth print-identity-token)
    export UI_SA_ID_TOKEN
else
    echo Using currently set UI_SA_ID_TOKEN. If this becomes stale, run export UI_SA_ID_TOKEN=\`gcloud auth print-identity-token\`
fi

poetry run pytest -s cicd
