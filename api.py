
import os
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="CKYY Bot API",
    version="1.0.0"
)

API_KEY = os.getenv("BACKEND_API_KEY", "")


@app.get("/")
def home():
    return {
        "name": "CKYY Bot API",
        "status": "online"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/info")
def info():
    return {
        "name": "CKYY Bot",
        "version": "1.0.0",
        "features": [
            "Menu Telegram",
            "Kalkulator",
            "Info Bot",
            "Status API"
        ]
    }


class Calculation(BaseModel):
    a: float = Field(ge=-1e12, le=1e12)
    b: float = Field(ge=-1e12, le=1e12)
    op: str


@app.post("/calculate")
def calculate(
    data: Calculation,
    x_api_key: str = Header(default="")
):
    if not API_KEY or x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    if data.op == "+":
        result = data.a + data.b
    elif data.op == "-":
        result = data.a - data.b
    elif data.op == "*":
        result = data.a * data.b
    elif data.op == "/":
        if data.b == 0:
            raise HTTPException(
                status_code=400,
                detail="Tidak bisa dibagi nol"
            )
        result = data.a / data.b
    else:
        raise HTTPException(
            status_code=400,
            detail="Operator tidak valid"
        )

    return {"result": result}
  
