from fastapi import FastAPI

from .routes import router

app = FastAPI(
    title="AgriMarketplace Logistics API",
    version="1.0.0",
)

app.include_router(router)


@app.get("/")
def root():
    return {"message": "Logistics API is running"}