from fastapi import FastAPI, HTTPException

from src.model_registry.api import (
    list_models,
    find_model,
    list_families,
)


app = FastAPI(
    title="AI Archive API",
    version="0.1.0",
)


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "archive-api",
        "version": "0.1.0",
    }



@app.get("/models")
def models():

    return list_models()



@app.get("/models/{model_id:path}")
def model(
    model_id: str,
):

    result = find_model(
        model_id
    )


    if result is None:

        raise HTTPException(
            status_code=404,
            detail=f"Model not found: {model_id}",
        )


    return result



@app.get("/families")
def families():

    return list_families()