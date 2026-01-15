import base64
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables (API Key)
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_car_damage(image_path):
    """
    Sends a car incident photo to Groq's Llama 3.2 Vision model.
    Extracts License Plate and assesses damage severity.
    """
    if not os.path.exists(image_path):
        return "Error: Image file not found."

    try:
        # 1. Encode image to base64
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        # 2. Call Groq Vision Model (Llama 3.2 11B Vision)
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct", 
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": (
                                "Analyze this vehicle incident photo for an insurance claim. "
                                "1. Extract the License Plate number if visible. "
                                "2. Rate the damage severity as Low, Medium, or High. "
                                "3. Provide a concise technical description of the visible damage."
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}",
                            },
                        },
                    ],
                }
            ],
            temperature=0.1,
            max_tokens=512,
        )
        # 3. Extract and return the AI text content
        analysis_result = completion.choices[0].message.content
        return analysis_result

    except Exception as e:
        print(f"❌ Groq Vision Error: {e}")
        return f"Analysis failed: {str(e)}"