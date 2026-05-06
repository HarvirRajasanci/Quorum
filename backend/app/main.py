from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Quorum Backend",
    version="0.1.0",
    description="FastAPI backend for the investment debate system.",
)

# Hackathon setting:
# Allow all origins so the React frontend can call the backend from its dev server.
# Tighten this after the demo if the project becomes production-facing.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    """
    Simple health check for frontend/backend integration.
    """
    return {"status": "ok"}