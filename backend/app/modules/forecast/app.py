from fastapi import FastAPI

from .routes import router

app = FastAPI(
    title="AgriMarketplace Forecast API",
    version="1.0.0",
)

app.include_router(router)


@app.get("/")
def root():
    return {"message": "Forecast API is running"}