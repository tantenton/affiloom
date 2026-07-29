from fastapi import FastAPI

app = FastAPI(title="Affiloom Backend")


@app.get("/health")
def health():
    return {"status": "ok"}
