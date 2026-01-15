import os

# Define the structure
folders = [
    "app",
    "app/routers",
    "app/services",
    "data/uploads",
    "data/sample_inputs",
    "sql",
    "tests",
    "research"
]

files = {
    "app/__init__.py": "",
    "app/main.py": "# FastAPI entry point\nfrom fastapi import FastAPI\napp = FastAPI()",
    "app/routes.py": "# API endpoints",
    "app/db_helper.py": "# SQLAlchemy & MySQL logic",
    "app/models.py": "# SQLAlchemy Models",
    "app/schemas.py": "# Pydantic Schemas",
    "app/image_processor.py": "# Groq Vision logic",
    "app/langchain_helper.py": "# LangChain + Groq Text logic",
    "app/utils.py": "# Helper functions",
    "app/config.py": "# Environment config",
    "sql/schema.sql": "-- SQL table creation script",
    ".env": "GROQ_API_KEY=your_key_here\nDB_HOST=localhost\nDB_USER=root\nDB_PASSWORD=password\nDB_NAME=insurance_db",
    "requirements.txt": "# Add your dependencies here",
    "README.md": "# Insurance Claim Chatbot"
}

def create_structure():
    print("🚀 Starting project scaffolding...")
    
    # Create folders
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"📁 Created folder: {folder}")

    # Create files
    for file_path, content in files.items():
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write(content)
            print(f"📄 Created file: {file_path}")
    
    print("\n✅ Project structure ready! You can now start coding.")

if __name__ == "__main__":
    create_structure()