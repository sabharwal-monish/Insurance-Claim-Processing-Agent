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

def analyze_car_damage(image_path):
    """
    Sends a car incident photo to Groq's Llama Vision model.
    Extracts License Plate and assesses damage severity.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Analysis result or error message
    """
    # 1. Validate file exists
    if not os.path.exists(image_path):
        return "Error: Image file not found."
    
    # 2. Check file size (max 10MB)
    file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return f"Error: Image too large ({file_size_mb:.1f}MB). Maximum size is {MAX_FILE_SIZE_MB}MB."
    
    # 3. Validate image format
    try:
        with Image.open(image_path) as img:
            if img.format.upper() not in ALLOWED_FORMATS:
                return f"Error: Unsupported format '{img.format}'. Allowed: {', '.join(ALLOWED_FORMATS)}"
    except Exception as e:
        return f"Error: Invalid image file - {str(e)}"

    try:
        # 4. Encode image to base64
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        # 5. Call Groq Vision Model (Llama 4 Scout 17B Vision)
        print(f"🔍 Analyzing image with Groq Vision API...")
        
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
            timeout=30  # 30 second timeout
        )
        
        # 6. Extract and return the AI text content
        analysis_result = completion.choices[0].message.content
        print(f"✅ Analysis complete: {len(analysis_result)} characters")
        return analysis_result

    except Exception as e:
        error_msg = f"❌ Groq Vision Error: {type(e).__name__} - {str(e)}"
        print(error_msg)
        return f"Analysis failed: {str(e)}"
