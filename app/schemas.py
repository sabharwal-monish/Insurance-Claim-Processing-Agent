# Pydantic Schemas
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Schema for the Dialogflow Webhook Request
class DialogflowRequest(BaseModel):
    responseId: str
    queryResult: Dict[str, Any]
    session: str

# Schema for the JSON we send back to Dialogflow
class DialogflowResponse(BaseModel):
    fulfillmentMessages: list