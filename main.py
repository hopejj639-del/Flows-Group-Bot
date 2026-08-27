# Filename: main.py
import uvicorn
import os
import logging
from app.api.server import app

if __name__ == "__main__":
    # Render assigns a dynamic port via the PORT environment variable.
    # We fallback to 8000 for local development.
    port = int(os.environ.get("PORT", 8000))
    
    logging.info(f"Starting Uvicorn server on port {port}...")
    
    # Run the FastAPI application using Uvicorn
    uvicorn.run(
        "app.api.server:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        proxy_headers=True, # Crucial for apps running behind cloud proxies like Render
        forwarded_allow_ips="*"
    )