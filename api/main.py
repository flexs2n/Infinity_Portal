"""
FastAPI main application - Trust-First Wealth Management Evidence API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import instruments, ticker, export

# Create FastAPI app
app = FastAPI(
    title="Wealth Management Evidence API",
    description="Evidence-based stock movement analysis using static social media datasets",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(instruments.router)
app.include_router(ticker.router)
app.include_router(export.router)


@app.get("/")
def root():
    """API root endpoint"""
    return {
        "name": "Wealth Management Evidence API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "instruments": "/instruments",
            "ticker_series": "/ticker/{ticker}/series",
            "ticker_events": "/ticker/{ticker}/events",
            "event_detail": "/ticker/{ticker}/event/{event_id}",
            "export": "/export (POST)"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
