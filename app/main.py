from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import router as webhook_router
from app.db_helper import get_db_connection
import os

app = FastAPI(
    title="Insurance Claim Processing Agent",
    description="Backend for Dialogflow NLU and Groq Vision analysis.",
    version="1.0.0"
)

# 1. Setup CORS
# In production, replace ["*"] with your actual frontend/Dialogflow URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Static File Mounting (Claim Photos)
UPLOAD_DIR = "data/uploads"
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
        "system_time": os.popen("date /t").read().strip(), # Quick server-side time check
        "docs": "/docs"
    }

# 5. DB Connectivity Check (Optimized with Dependency)
@app.get("/check-db", tags=["Health"])
async def check_db():
    """
    Checks if the Aiven MySQL cloud instance is reachable.
    """
    try:
        conn = get_db_connection()
        if conn and conn.is_connected():
            # Get a quick count or server info to prove it's live
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
    # Start the server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)