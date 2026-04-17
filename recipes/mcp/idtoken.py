"""ID token credential acquisition — isinstance dispatch.

Mirrors GcpTokenProvider._wrap_for_id_token from pyful-agents.
Supports impersonated (local dev), compute engine (GCE/GKE),
and metadata/SA key (Cloud Run / AE) credential types.
"""

import google.auth
import google.auth.transport.requests
from google.auth import compute_engine, impersonated_credentials
from google.oauth2 import id_token


def acquire_id_token_credentials(audience: str):
    """Acquire ID token credentials for the given audience.

    Local dev: gcloud auth application-default login --impersonate-service-account=SA
    GCP (Cloud Run / AE): compute engine metadata server.
    """
    creds, _ = google.auth.default()
    if isinstance(creds, impersonated_credentials.Credentials):
        return impersonated_credentials.IDTokenCredentials(
            creds, target_audience=audience, include_email=True,
        )
    elif isinstance(creds, compute_engine.Credentials):
        return compute_engine.IDTokenCredentials(
            google.auth.transport.requests.Request(),
            target_audience=audience,
        )
    else:
        return id_token.fetch_id_token_credentials(audience=audience)
