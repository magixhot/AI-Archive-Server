from fastapi import FastAPI
from pydantic import BaseModel

from src.model_registry.api import register_model


app = FastAPI(
    title="AI Archive Queue Manager",
    version="0.2.0",
)


class ModelRequest(BaseModel):

    model_id: str

    family: str | None = None

    version: str | None = None



@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "queue-manager",
        "version": "0.2.0",
    }



@app.post("/models")
def add_model(
    request: ModelRequest,
):

    result = register_model(
        request.model_id,
        request.family,
        request.version,
    )

    return result