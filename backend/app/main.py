import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import auth, contacts, anniversaries, holidays, reminders
from app.jobs.reminder_job import start_scheduler

app = FastAPI(title="Eternal Moments API", version="0.1.0")


@app.on_event("startup")
def startup_event():
    start_scheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(contacts.router, prefix="/api/v1/contacts", tags=["contacts"])
app.include_router(anniversaries.router, prefix="/api/v1/anniversaries", tags=["anniversaries"])
app.include_router(holidays.router, prefix="/api/v1/holidays", tags=["holidays"])
app.include_router(reminders.router, prefix="/api/v1/reminders", tags=["reminders"])

# 静态文件：头像等上传文件
os.makedirs("uploads/avatars", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/health")
def health():
    return {"status": "ok"}
