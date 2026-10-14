import azure.functions as func

from app import app as api_app

app = func.AsgiFunctionApp(
    app=api_app,
    http_auth_level=func.AuthLevel.FUNCTION,
)
