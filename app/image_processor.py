import base64
import os
from groq import Groq
from dotenv import load_dotenv
from PIL import Image

# Load environment variables (API Key)
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Configuration
MAX_FILE_SIZE_MB = 10
ALLOWED_FORMATS = {'JPEG', 'JPG', 'PNG', 'WEBP'}

def analyze_car_damage(image_input):
    """
    Sends a car incident photo to Groq's Llama Vision model.
    Supports either a local file path or a public image URL.
    """
    is_url = image_input.startswith("http://") or image_input.startswith("https://")
    
    if not is_url and not os.path.exists(image_input):
        return "Error: Image file not found."
    
    try:
        if is_url:
            image_url_content = image_input
            print(f"🔍 Analyzing image URL with Groq Vision API...")
        else:
            # Check file size (max 10MB)
            file_size_mb = os.path.getsize(image_input) / (1024 * 1024)
            if file_size_mb > MAX_FILE_SIZE_MB:
                return f"Error: Image too large ({file_size_mb:.1f}MB). Maximum size is {MAX_FILE_SIZE_MB}MB."
            
            # Validate image format
            with Image.open(image_input) as img:
                if img.format.upper() not in ALLOWED_FORMATS:
                    return f"Error: Unsupported format '{img.format}'. Allowed: {', '.join(ALLOWED_FORMATS)}"
            
            # Encode image to base64
            with open(image_input, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            image_url_content = f"data:image/jpeg;base64,{encoded_image}"
            print(f"🔍 Analyzing local image with Groq Vision API...")
        
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct", # Updated to 2026 stable Llama 4 Vision model
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
                                "url": image_url_content,
                            },
                        },
                    ],
                }
            ],
            temperature=0.1,
            max_tokens=512,
            timeout=30
        )
        
        # Log the full response for debugging
        print(f"DEBUG: Groq Response Status: {completion.id if hasattr(completion, 'id') else 'N/A'}")
        
        analysis_result = completion.choices[0].message.content
        print(f"✅ Analysis complete: {len(analysis_result)} characters")
        print(f"Groq Analysis Result Snippet: {analysis_result[:100]}...")
        return analysis_result

    except Exception as e:
        # Check for specific Groq API errors
        status_code = getattr(e, 'status_code', 'N/A')
        error_msg = f"❌ Groq Vision Error (Status: {status_code}): {type(e).__name__} - {str(e)}"
        print(error_msg)
        return f"Analysis failed (Status: {status_code}): {str(e)}"


