from fastapi import FastAPI
from .routes import rag

app = FastAPI()


@app.get("/")
def root():
    
    return {"message" : "Welcome to biometric rag agent"}

app.include_router(rag.router)