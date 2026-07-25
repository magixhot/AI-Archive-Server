from fastapi import FastAPI


app = FastAPI(
    title="AI Archive Queue Manager",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "queue-manager",
        "version": "0.1.0",
    }


@app.get("/")
def root():
    return {
        "service": "queue-manager",
        "message": "AI Archive Server is running",
    }