from fastapi.openapi.utils import get_openapi


def configure_public_api_openapi(public_app):
    """
    Configure OpenAPI schema for the public API with API key security.
    
    This function sets up:
    - Correct server URLs for the mounted public API
    - API key authentication via X-API-Key header
    - Global security requirement for all endpoints
    """
    def custom_openapi():
        if public_app.openapi_schema:
            return public_app.openapi_schema
        
        openapi_schema = get_openapi(
            title="Voice Chef Public API",
            version="1.0.0",
            routes=public_app.routes,
        )
        
        # Set the servers so Swagger knows where to send requests
        openapi_schema["servers"] = [
            {"url": "/api/public", "description": "Public API"},
            {"url": "http://localhost/api/public", "description": "Local development"}
        ]
        
        # Add API key security scheme
        openapi_schema["components"]["securitySchemes"] = {
            "api_key": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API Key for accessing public endpoints"
            }
        }
        
        # Apply security requirement globally
        openapi_schema["security"] = [{"api_key": []}]
        
        public_app.openapi_schema = openapi_schema
        return public_app.openapi_schema
    
    public_app.openapi = custom_openapi
