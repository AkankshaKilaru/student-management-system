from pydantic import BaseModel, Field

# ================= STUDENT =================
class StudentCreate(BaseModel):
    name: str = Field(..., min_length=2)
    course: str = Field(..., min_length=2)
    marks: int = Field(..., ge=0, le=100)
    hallticket: str
    attendance: int

class StudentResponse(BaseModel):
    id: int
    name: str
    course: str
    marks: int
    hallticket: str
    attendance: int

    class Config:
        from_attributes = True


# ================= USER =================
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=4)
    role: str = "user"