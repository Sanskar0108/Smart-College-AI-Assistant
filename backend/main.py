import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.core.config import PROJECT_NAME, CORS_ORIGINS
from backend.routes import documents, ai, settings
from backend.schemas.responses import ApiResponse

app = FastAPI(title=PROJECT_NAME, version="1.0.0")

# 1. CORS Configuration (Explicit local-dev configurations)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 2. Consistent Error Envelope Wrappers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Format standard HTTP exceptions into consistent failure responses.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Format unhandled exceptions into consistent failure responses.
    """
    error_detail = str(exc) or exc.__class__.__name__ or "Unknown Internal Error"
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": f"Internal Server Error: {error_detail}"
        }
    )

# 3. Health Check route
@app.get("/api/health", response_model=ApiResponse[dict])
def health_check():
    """
    Simplistic system health check.
    """
    return ApiResponse(
        success=True,
        message="System healthy",
        data={
            "status": "ok",
            "version": "1.0.0"
        }
    )

# 4. Register API routers (API registered FIRST)
app.include_router(documents.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(settings.router, prefix="/api")

# 5. Serve static files (Frontend mounted LAST)
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
frontend_path = os.path.join(root_dir, "frontend")

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    print(f"Warning: Static frontend directory not found at: {frontend_path}. API routes are active.")

if __name__ == "__main__":
    import uvicorn
    # Allow running directly via python main.py
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
