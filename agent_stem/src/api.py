from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
