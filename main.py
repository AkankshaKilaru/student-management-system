from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from database import SessionLocal
import models
import models, schemas
from database import engine, SessionLocal
from jose import JWTError

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Config
SECRET_KEY = "secret123"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Password utils
def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

# Token
def create_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=30)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Get current user

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Admin check
def require_admin(user = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user

# ================= AUTH =================

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_pw = hash_password(user.password)

    new_user = models.User(
        username=user.username,
        password=hashed_pw,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    return {"message": "User registered"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    print("Entered:", form_data.username, form_data.password)
    print("DB user:", user.username if user else None)
    print("Stored hash:", user.password if user else None)

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_token({
        "sub": user.username,
        "role": user.role
    })

    return {"access_token": token, "token_type": "bearer"}

# ================= STUDENT APIs =================

# Create (any logged-in user)
@app.post("/students/", response_model=schemas.StudentResponse)
def create_student(student: schemas.StudentCreate,
                   db: Session = Depends(get_db),
                   user = Depends(get_current_user)):
    new_student = models.Student(**student.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

# Read (any logged-in user)
@app.get("/students/", response_model=list[schemas.StudentResponse])
def get_students(db: Session = Depends(get_db),
                 user = Depends(get_current_user)):
    return db.query(models.Student).all()

# Update (admin only)
@app.put("/students/{id}", response_model=schemas.StudentResponse)
def update_student(id: int, data: schemas.StudentCreate,
                   db: Session = Depends(get_db),
                   user = Depends(require_admin)):
    student = db.query(models.Student).filter(models.Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Not found")

    student.name = data.name
    student.course = data.course
    student.marks = data.marks

    db.commit()
    db.refresh(student)
    return student

# Delete (admin only)
@app.delete("/students/{id}")
def delete_student(id: int,
                   db: Session = Depends(get_db),
                   user = Depends(require_admin)):
    student = db.query(models.Student).filter(models.Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(student)
    db.commit()
    return {"message": "Deleted"}
def create_admin():
    db = SessionLocal()

    print("Creating admin...")  # 🔥 debug

    admin = models.User(
        username="admin",
        password=hash_password("admin123"),
        role="admin"
    )

    db.add(admin)
    db.commit()
    db.close()

    print("Admin created!")  # 🔥 debug
#create_admin()