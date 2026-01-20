# AI Insurance Claim Agent (Vision Edition)

An intelligent insurance claim processing system leveraging state-of-the-art vision models and automated conversational flows.

## Core Stack
- **Dialogflow ES**: Conversational AI for user interaction and intent matching.
- **FastAPI**: High-performance Python backend for webhook processing and image handling.
- **Groq Vision (Llama 4 Scout)**: Advanced vision analysis using `meta-llama/llama-4-scout-17b-16e-instruct` for automated damage assessment.
- **Aiven MySQL**: Managed database for persistent storage of claim details and analysis reports.

## Features
- **Automated OCR**: Scans incident photos to extract license plate numbers (e.g., 'BATCAT').
- **Damage Severity Assessment**: Automatically classifies vehicle damage as **Low**, **Medium**, or **High**.
- **Technical Analysis**: Provides a concise technical description of the visible damage for internal review.
- **Persistent Logging**: Stores all analysis results and session data securely in Aiven MySQL with SSL encryption.

## How to Test
1. **Open Dialogflow Console**: Navigate to your configured agent.
2. **Start Interaction**: Type `Hi` or `I want to report a claim`.
3. **Provide Details**: Follow the prompts to provide your Name and Policy Number (e.g., `POL_AG_123`).
4. **Submit Photo**: When asked for details or a description, provide a public image URL of a car (e.g., `https://example.com/damaged_car.jpg`).
5. **Review Analysis**: The agent will process the image via Groq and return the damage severity and description.
6. **Verify DB**: Check the `insurance_sessions` table in Aiven MySQL to see the saved `damage_report`.

---
*Created for Advanced Agentic Coding - 2026*