from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from pathlib import Path
import os

from database import get_db, engine, Base
from models import User, Note, Document
from schemas import (
    UserRegister, UserLogin, TokenResponse,
    NoteCreate, NoteUpdate, NoteResponse,
    DocumentCreate, DocumentResponse
)
from security import hash_password, verify_password, create_access_token, verify_token

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartHub API", version="1.0.0")

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ HEALTH CHECK ============

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok", "app": "SmartHub"}

# ============ AUTHENTICATION ENDPOINTS ============

@app.post("/api/register", response_model=TokenResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register new user
    
    Takes: email, full_name, password
    Returns: JWT token (user is immediately logged in)
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password before storing
    hashed_pwd = hash_password(user_data.password)
    
    # Create new user in database
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_pwd
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create token for this user
    access_token = create_access_token(
        user_id=new_user.id,
        expires_delta=timedelta(days=7)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": new_user.id,
        "email": new_user.email
    }

@app.post("/api/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login existing user
    
    Takes: email, password
    Returns: JWT token
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    # Check if user exists AND password is correct
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create token
    access_token = create_access_token(
        user_id=user.id,
        expires_delta=timedelta(days=7)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email
    }

@app.get("/api/me")
def get_current_user(token: str = None, db: Session = Depends(get_db)):
    """
    Get current logged-in user's info
    
    Takes: JWT token
    Returns: User data
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided"
        )
    
    # Extract user_id from token
    user_id = verify_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name
    }

# ============ HELPER FUNCTION ============

def get_current_user_from_token(token: str, db: Session) -> User:
    """Extract user from JWT token"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided"
        )
    
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

# ============ NOTES ENDPOINTS ============

@app.post("/api/notes", response_model=NoteResponse)
def create_note(note_data: NoteCreate, token: str = None, db: Session = Depends(get_db)):
    """
    Create a new note
    
    Takes: title, content (+ JWT token)
    Returns: Created note with id, timestamps
    """
    user = get_current_user_from_token(token, db)
    
    new_note = Note(
        user_id=user.id,
        title=note_data.title,
        content=note_data.content
    )
    
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    
    return new_note

@app.get("/api/notes", response_model=list[NoteResponse])
def list_notes(token: str = None, db: Session = Depends(get_db)):
    """
    Get all notes for logged-in user
    
    Takes: JWT token
    Returns: List of user's notes
    """
    user = get_current_user_from_token(token, db)
    
    notes = db.query(Note).filter(Note.user_id == user.id).all()
    
    return notes

@app.get("/api/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: str, token: str = None, db: Session = Depends(get_db)):
    """
    Get a single note by id
    """
    user = get_current_user_from_token(token, db)
    
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == user.id
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    return note

@app.put("/api/notes/{note_id}", response_model=NoteResponse)
def update_note(note_id: str, note_data: NoteUpdate, token: str = None, db: Session = Depends(get_db)):
    """
    Update a note
    """
    user = get_current_user_from_token(token, db)
    
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == user.id
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Update only fields that were provided
    if note_data.title is not None:
        note.title = note_data.title
    if note_data.content is not None:
        note.content = note_data.content
    
    db.commit()
    db.refresh(note)
    
    return note

@app.delete("/api/notes/{note_id}")
def delete_note(note_id: str, token: str = None, db: Session = Depends(get_db)):
    """
    Delete a note
    """
    user = get_current_user_from_token(token, db)
    
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == user.id
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    db.delete(note)
    db.commit()
    
    return {"message": "Note deleted successfully"}

# ============ DOCUMENTS ENDPOINTS ============

# Directory to store uploaded files
UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/api/documents/upload", response_model=DocumentResponse)
def upload_document(file: UploadFile = File(...), token: str = None, db: Session = Depends(get_db)):
    """
    Upload a document/file
    
    Takes: file (binary), JWT token
    Returns: Document metadata with id
    """
    user = get_current_user_from_token(token, db)
    
    # Check file size (max 10MB)
    MAX_SIZE = 10 * 1024 * 1024
    file_size = 0
    
    # Save file to disk
    file_path = UPLOAD_DIR / f"{user.id}_{file.filename}"
    
    try:
        with open(file_path, "wb") as f:
            for chunk in file.file:
                file_size += len(chunk)
                if file_size > MAX_SIZE:
                    os.remove(file_path)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File too large (max 10MB)"
                    )
                f.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=str(e))
    
    # Save document record to database
    document = Document(
        user_id=user.id,
        title=file.filename,
        filename=file.filename,
        file_path=str(file_path),
        file_size=file_size
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return document

@app.get("/api/documents", response_model=list[DocumentResponse])
def list_documents(token: str = None, db: Session = Depends(get_db)):
    """
    List all documents uploaded by user
    
    Takes: JWT token
    Returns: List of user's documents
    """
    user = get_current_user_from_token(token, db)
    
    documents = db.query(Document).filter(Document.user_id == user.id).all()
    
    return documents

@app.get("/api/documents/{document_id}")
def download_document(document_id: str, token: str = None, db: Session = Depends(get_db)):
    """
    Download a document
    
    Returns the file as binary data
    """
    user = get_current_user_from_token(token, db)
    
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    file_path = Path(document.file_path)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    # Return file as download
    return FileResponse(
        path=file_path,
        filename=document.filename,
        media_type='application/octet-stream'
    )