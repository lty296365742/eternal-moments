from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, contacts, anniversaries, holidays, reminders

app = FastAPI(title="Eternal Moments API", version="0.1.0")

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


@app.get("/health")
def health():
    return {"status": "ok"}
