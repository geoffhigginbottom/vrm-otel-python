# VRM OTEL Python

# Introduction
Lambda function that collects data from the VRM APIs then pushes it into Splunk Observability as Custom Metrics.

# Env Vars
The following env variables are required

ACCESS_TOKEN
AFT_MPPT_ID
FWD_MPPT_ID
REALM
SITE_ID
SITE_NAME
VRM_PASSWORD
VRM_USERNAME

# Triggering
Function is triggered by an Event Bridge Schedule, firing every 1 minute