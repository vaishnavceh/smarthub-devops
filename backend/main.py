from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db, engine, Base
from models import User, Note
from schemas import UserRegister, UserLogin, TokenResponse, NoteCreate, NoteUpdate, NoteResponse
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

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok", "app": "SmartHub"}

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
    
    What happens:
    1. Find user by email
    2. Check password matches
    3. Create token
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
    
    Takes: JWT token in Authorization header
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

# ============ NOTES ENDPOINTS ============

def get_current_user_from_token(token: str, db: Session) -> User:
    """Helper function: Extract user from token"""
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

@app.post("/api/notes", response_model=NoteResponse)
def create_note(note_data: NoteCreate, token: str = None, db: Session = Depends(get_db)):
    """
    Create a new note for logged-in user
    
    Takes: title, content (+ JWT token)
    Returns: Created note with id, timestamps
    """
    # Get current user from token
    user = get_current_user_from_token(token, db)
    
    # Create new note
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
    
    # Query all notes belonging to this user
    notes = db.query(Note).filter(Note.user_id == user.id).all()
    
    return notes

@app.get("/api/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: str, token: str = None, db: Session = Depends(get_db)):
    """
    Get a single note by id
    
    Checks: Does note exist? Does it belong to current user?
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
    
    User can update only their own notes
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
    
    User can delete only their own notes
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