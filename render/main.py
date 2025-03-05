from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# SQLite Database Configuration
DATABASE_URL = "sqlite:///./user.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define Contact Table
class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    message = Column(String)

# Create Table
Base.metadata.create_all(bind=engine)

# Pydantic Model for Data Validation
class ContactSchema(BaseModel):
    name: str
    email: str
    message: str

# API to store contact form data
@app.post("/submit")
async def submit_form(contact: ContactSchema):
    db = SessionLocal()
    try:
        new_contact = Contact(name=contact.name, email=contact.email, message=contact.message)
        db.add(new_contact)
        db.commit()
        return {"message": "✅ Form submitted successfully!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

# API to retrieve all stored contacts (for Admin only)
@app.get("/contacts")
async def get_contacts():
    db = SessionLocal()
    contacts = db.query(Contact).all()
    db.close()
    return contacts
