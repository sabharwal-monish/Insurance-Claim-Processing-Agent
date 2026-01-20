from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse
from uuid import uuid4
from app.db_helper import get_db_connection
from app.langchain_helper import chat_with_groq
import os
import re
from .image_processor import analyze_car_damage

router = APIRouter()

# --- Helpers ---

REQUIRED_FIELDS = ["date_time_of_incident", "policy_number", "vehicle_info", "incident_description", "claimant_name"]

def send_claim_summary(session_id, analysis_text):
    """Generates the final report log."""
    # Log to terminal (Replace with actual SMTP logic if needed)
    print(f"📧 EMAIL REPORT GENERATED for Session {session_id}")
    print(f"Analysis: {analysis_text}")

def clean_extract(keys, param_dict):
    """Safely extracts strings from Dialogflow's mixed-type parameters."""
    for k in keys:
        val = param_dict.get(k)
        if val:
            if isinstance(val, dict):
                val = next(iter(val.values()))
            if isinstance(val, list):
                val = val[0] if len(val) > 0 else None
            if val and str(val).strip() not in ["", "[]"]:
                return str(val).strip()
    return None

# --- Routes ---

@router.get("/upload-image/{session_id}")
async def upload_page(session_id: str):
    html = f"""
    <html><body style='font-family: sans-serif; text-align: center; padding: 50px;'>
        <h3>Upload Damage Photo</h3>
        <p>Session ID: {session_id}</p>
        <form action='/upload-image/{session_id}' method='post' enctype='multipart/form-data'>
            <input type='file' name='file' accept='image/*' required><br><br>
            <input type='submit' value='Upload Photo' style='padding: 10px 20px;'>
        </form>
    </body></html>
    """
    return HTMLResponse(content=html)

@router.post("/upload-image/{session_id}")
async def process_upload(session_id: str, file: UploadFile = File(...)):
    conn = None
    try:
        # 1. Save file using absolute path
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        UPLOAD_DIR = os.path.join(BASE_DIR, "app", "data", "uploads")
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        path = os.path.join(UPLOAD_DIR, f"{session_id}_{file.filename}")
        with open(path, "wb") as f:
            f.write(await file.read())
        
        # 2. Vision Analysis
        print(f"--- 🔍 Starting Analysis for Session: {session_id} ---")
        damage_report = analyze_car_damage(path)
        
        # 3. Trigger Report
        send_claim_summary(session_id, damage_report)
        
        # 4. Update DB
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE insurance_sessions SET photo_uploaded = TRUE WHERE session_id = %s", (session_id,))
            conn.commit()
        
        return HTMLResponse(content=f"""
            <html><body style='font-family: Arial; text-align: center; padding: 100px;'>
                <h1 style='color: green;'>Upload Successful! ✅</h1>
                <p><strong>AI Analysis:</strong> {damage_report}</p>
                <p>You can now close this tab and return to the chat.</p>
            </body></html>
        """)

    except Exception as e:
        print(f"❌ Error in process_upload: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if conn and conn.open:
            conn.close()

@router.post("/webhook")
async def dialogflow_webhook(request: Request):
    conn = None
    try:
        payload = await request.json()
        session_path = payload.get('session', '')
        session_id = session_path.split('/')[-1] if session_path else str(uuid4())
        
        query_result = payload.get('queryResult', {})
        user_input = query_result.get('queryText', '')
        intent_name = query_result.get('intent', {}).get('displayName', '')
        parameters = query_result.get('parameters', {})

        conn = get_db_connection()
        if conn is None:
            return {"fulfillmentText": "Database connection error. Please try again later."}
            
        cursor = conn.cursor()

        # Ensure Session Exists
        cursor.execute("SELECT * FROM insurance_sessions WHERE session_id = %s", (session_id,))
        existing_row = cursor.fetchone()
        if not existing_row:
            cursor.execute("INSERT INTO insurance_sessions (session_id) VALUES (%s)", (session_id,))
            conn.commit()
            existing_row = {f: None for f in REQUIRED_FIELDS}

        # Parameter Extraction
        new_data = {}
        if intent_name == "provide_policy_number":
            extracted = clean_extract(["policy_number", "number"], parameters)
            if not extracted:
                match = re.search(r'([A-Z0-9-]{4,15})', user_input.upper())
                extracted = match.group(0) if match else None
            new_data["policy_number"] = extracted
        elif intent_name == "provide_date_time":
            new_data["date_time_of_incident"] = clean_extract(["date", "date-time", "time"], parameters)
        elif intent_name == "provide_vehicle_info":
            new_data["vehicle_info"] = clean_extract(["vehicle_info", "any"], parameters)
        elif intent_name == "provide_name":
            new_data["claimant_name"] = clean_extract(["claimant_name", "person", "name"], parameters)
        elif intent_name == "describe_incident":
            new_data["incident_description"] = user_input

        # Database Update
        updates = [f"{field} = %s" for field, val in new_data.items() if val]
        vals = [val for val in new_data.values() if val]
        if updates:
            sql = f"UPDATE insurance_sessions SET {', '.join(updates)} WHERE session_id = %s"
            vals.append(session_id)
            cursor.execute(sql, tuple(vals))
            conn.commit()

        # Fetch State
        cursor.execute("SELECT * FROM insurance_sessions WHERE session_id = %s", (session_id,))
        full_session = cursor.fetchone()

        # Check Completion
        is_complete = all(full_session.get(f) for f in REQUIRED_FIELDS)
        
        if is_complete:
            # Detect Public URL (Render) or fallback to localhost
            base_url = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")
            upload_url = f"{base_url}/upload-image/{session_id}"
            
            final_text = (f"Thank you, {full_session.get('claimant_name')}. I have all your details. "
                          f"Please finish by uploading photos here: {upload_url}. Goodbye!")
            
            return {
                "fulfillmentText": final_text,
                "endInteraction": True
            }

        # Not complete? Get next question from AI
        ai_reply = chat_with_groq(user_input, full_session)
        return {"fulfillmentText": ai_reply}

    except Exception as e:
        print(f"❌ Webhook Error: {e}")
        import traceback
        traceback.print_exc()
        return {"fulfillmentText": "I'm having a technical issue. Can we try that again?"}
    finally:
        if conn and conn.open:
            conn.close()