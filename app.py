from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic_settings import BaseSettings
from typing import List, Dict
import openai
import os
from docx import Document
import re

class Settings(BaseSettings):
    openai_api_key: str
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.3
    
    class Config:
        env_file = ".env"

app = FastAPI()
settings = Settings()
openai.api_key = settings.openai_api_key

def process_transcript(text: str) -> str:
    response = openai.ChatCompletion.create(
        model=settings.model_name,
        temperature=settings.temperature,
        messages=[
            {"role": "system", "content": """You are a D&D session summarizer. Extract key story events, 
            character actions, and plot developments. Ignore out-of-character discussion. Format the summary with:
            - Key Plot Points
            - Important NPCs Encountered
            - Character Decisions & Actions
            - Locations Visited
            - Quest Updates"""},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

@app.post("/summarize/")
async def create_summary(file: UploadFile = File(...)):
    if not file.filename.endswith('.txt'):
        raise HTTPException(400, "Only .txt files allowed")
    
    content = await file.read()
    text = content.decode('utf-8')
    
    summary = process_transcript(text)
    
    doc = Document()
    doc.add_heading('D&D Session Summary', 0)
    doc.add_paragraph(summary)
    
    output_filename = f"summary_{file.filename.replace('.txt', '.docx')}"
    doc.save(output_filename)
    
    return FileResponse(output_filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
