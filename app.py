from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic_settings import BaseSettings
import openai
from docx import Document

# Settings from GitHub Secrets
class Settings(BaseSettings):
    openai_api_key: str
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.3

# Initialize FastAPI and settings
app = FastAPI()
settings = Settings()
openai.api_key = settings.openai_api_key

# Process the D&D transcript with OpenAI
def process_transcript(text: str) -> str:
    response = openai.ChatCompletion.create(
        model=settings.model_name,
        temperature=settings.temperature,
        messages=[
            {"role": "system", "content": "You are a D&D session summarizer. Extract key story events, character actions, and plot developments. Format with: Key Plot Points, Important NPCs, Character Actions, Locations, Quest Updates"},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

# Serve the HTML upload page
@app.get("/")
async def read_root():
    with open("index.html") as f:
        return HTMLResponse(content=f.read())

# Handle file upload and return summary
@app.post("/summarize/")
async def create_summary(file: UploadFile = File(...)):
    if not file.filename.endswith('.txt'):
        raise HTTPException(400, "Only .txt files allowed")
    
    # Read and process the file
    text = (await file.read()).decode('utf-8')
    summary = process_transcript(text)
    
    # Create and save the Word document
    doc = Document()
    doc.add_heading('D&D Session Summary', 0)
    doc.add_paragraph(summary)
    output_filename = f"summary_{file.filename.replace('.txt', '.docx')}"
    doc.save(output_filename)
    
    return FileResponse(output_filename)
