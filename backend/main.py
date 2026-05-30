from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

fake_users = {
    "admin": "password123"
}

@app.get("/health")
def health():
    return {"status": "ok", "app": "SmartHub"}

@app.post("/api/login")
def login(data: LoginRequest):
    if data.username in fake_users and fake_users[data.username] == data.password:
        return {"success": True, "token": "fake-jwt-token", "username": data.username}
    return {"success": False, "message": "Invalid credentials"}

@app.get("/api/notes")
def get_notes():
    return {"notes": [
        {"id": 1, "title": "First Note", "content": "Hello from SmartHub backend!"},
        {"id": 2, "title": "Docker Note", "content": "Running inside Docker container"},
        {"id": 3, "title": "Internship", "content": "Cixio TKM internship 2026"}
    ]}