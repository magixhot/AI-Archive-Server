from fastapi import FastAPI

from pydantic import BaseModel

from src.model_registry.api import (
    register_model,
    list_models,
    find_model,
    list_families,
)


app = FastAPI(
    title="AI Archive Queue Manager",
    version="0.3.0",
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
        "version": "0.3.0",
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



@app.get("/models")
def get_models():

    return list_models()



@app.get("/models/{model_id:path}")
def get_model(
    model_id: str,
):

    model = find_model(
        model_id
    )

    if model is None:

        return {
            "error": "Model not found",
            "model_id": model_id,
        }

    return model



@app.get("/families")
def get_model_families():

    return list_families()