import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    request_timeout=4.0,
    temperature=0
)

def chat_with_groq(user_message: str, claim_data: dict):
    try:
        status = {
            "Policy Number": claim_data.get('policy_number'),
            "Incident Date": claim_data.get('date_time_of_incident'),
            "Vehicle Info": claim_data.get('vehicle_info'),
            "Description": claim_data.get('incident_description'),
            "Claimant Name": claim_data.get('claimant_name') # <--- Add this
        }

        missing_items = [k for k, v in status.items() if not v]

        system_content = f"""You are a professional insurance claim assistant. 

CURRENT PROGRESS:
{chr(10).join([f"- {k}: {v}" for k, v in status.items() if v])}

STILL NEEDED: {', '.join(missing_items)}

RULES:
1. Acknowledge what the user just said.
2. Ask for exactly ONE missing item.
3. Keep it under 2 sentences. No small talk."""

        messages = [SystemMessage(content=system_content), HumanMessage(content=user_message)]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return "I've noted that. Could you please provide your policy number?"