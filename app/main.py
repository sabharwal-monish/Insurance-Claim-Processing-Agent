from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import router as webhook_router
from app.db_helper import get_db_connection
import os
from datetime import datetime

app = FastAPI(
    title="Insurance Claim Processing Agent",
    description="Backend for Dialogflow NLU and Groq Vision analysis.",
    version="1.0.0"
)

# 1. Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Static File Mounting (Claim Photos)
# Using absolute path to ensure Render finds it correctly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# 3. Include Routers
app.include_router(webhook_router)

# 4. Root / Health Endpoint
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "message": "Insurance Claim Agent is Live!",
        "system_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # Works on both Windows & Linux
        "docs": "/docs"
    }

# 5. DB Connectivity Check
@app.get("/check-db", tags=["Health"])
async def check_db():
    try:
        conn = get_db_connection()
        if conn and conn.is_connected():
            db_info = conn.get_server_info()
            conn.close()
            return {
                "status": "success", 
                "message": "Connected to Aiven MySQL successfully.",
                "server_version": db_info
            }
        return {"status": "error", "message": "Database connection failed check."}
    except Exception as e:
        return {"status": "error", "message": f"Connection Exception: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    # Local testing port
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)