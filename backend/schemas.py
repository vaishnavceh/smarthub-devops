from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from typing import Optional
class UserRegister(BaseModel):
    """What user sends when they register"""
    email: EmailStr  # Must be valid email format
    full_name: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "password": "securepassword123"
            }
        }

class UserLogin(BaseModel):
    """What user sends when they login"""
    email: str
    password: str

class TokenResponse(BaseModel):
    """What we send back after successful login"""
    access_token: str
    token_type: str = "bearer"  # Always "bearer"
    user_id: str
    email: str

class UserResponse(BaseModel):
    """User data we return (never include password!)"""
    id: str
    email: str
    full_name: str
    
    class Config:
        from_attributes = True  # Converts database model to Pydantic model\



class NoteCreate(BaseModel):
    """What user sends when creating a note"""
    title: str
    content: str

class NoteUpdate(BaseModel):
    """What user sends when updating a note"""
    title: Optional[str] = None
    content: Optional[str] = None

class NoteResponse(BaseModel):
    """What we return to user"""
    id: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentCreate(BaseModel):
    """Metadata when uploading a document"""
    title: str

class DocumentResponse(BaseModel):
    """What we return about documents"""
    id: str
    title: str
    filename: str
    file_size: int
    uploaded_at: datetime

    class Config:
        from_attributes = True