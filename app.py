# Version 1.2.2
# Changes:
# - Simplified stats tracking
# - Improved contextual accuracy
# - Integrated sanitizer into main app

import streamlit as st
import openai
from docx import Document
from io import BytesIO
import re
from typing import Dict, List, Set

class DnDSanitizer:
    def __init__(self):
        self.dnd_allowlist = {
            'dragon', 'demon', 'devil', 'undead', 'zombie', 'kobold', 'orc',
            'spell', 'magic', 'curse', 'ritual', 'enchant',
            'blood', 'corpse', 'wound', 'kill', 'dead', 'death'
        }
        self.profanity_set = self._load_profanity_list()
        
    def _load_profanity_list(self) -> Set[str]:
        return {'badword1', 'badword2'}
        
    def sanitize(self, text: str) -> str:
        words = text.split()
        sanitized_words = []
        
        for word in words:
            clean_word = word.lower().strip('.,!?')
            if clean_word in self.profanity_set and clean_word not in self.dnd_allowlist:
                sanitized_words.append('[REMOVED]')
            else:
                sanitized_words.append(word)
                
        return ' '.join(sanitized_words)

def chunk_text(text: str, chunk_size: int = 8000) -> list[str]:
    sentences = text.split('. ')
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(sentence.split()) * 1.3
        
        if current_length + sentence_length > chunk_size:
            chunks.append('. '.join(current_chunk) + '.')
            current_chunk = [sentence]
            current_length = sentence_length
        else:
            current_chunk.append(sentence)
            current_length += sentence_length
    
    if current_chunk:
        chunks.append('. '.join(current_chunk) + '.')
    
    return chunks

def generate_summary(text: str, client: openai.OpenAI) -> str:
    chunks = chunk_text(text)
    summaries = []
    
    total_chunks = len(chunks)
    if total_chunks > 1:
        st.write(f"Processing {total_chunks} chunks of text...")
        progress_bar = st.progress(0)
        
    for i, chunk in enumerate(chunks):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            messages=[
                {"role": "system", "content": """Generate a D&D session summary focusing on key events and narrative:
- Include major combat encounters and their outcomes
- Describe significant character actions and decisions
- Note important discoveries or plot developments
- Focus on game-relevant events and interactions
- Maintain narrative accuracy without exact number tracking"""},
                {"role": "user", "content": chunk}
            ]
        )
        summaries.append(response.choices[0].message.content)
        
        if total_chunks > 1:
            progress_bar.progress((i + 1) / total_chunks)
    
    if total_chunks > 1:
        st.write("Processing complete!")
        combined = "\n\n".join(summaries)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            messages=[
                {"role": "system", "content": "Combine these summaries into one cohesive narrative focusing on key events and outcomes."},
                {"role": "user", "content": combined}
            ]
        )
        return response.choices[0].message.content
    
    return summaries[0]

def create_docx(summary: str) -> BytesIO:
    doc = Document()
    doc.add_heading('D&D Session Summary', 0)
    doc.add_paragraph(summary)
    
    docx_file = BytesIO()
    doc.save(docx_file)
    docx_file.seek(0)
    return docx_file

# Configure Streamlit page
st.set_page_config(page_title="D&D Session Summarizer")
st.title("D&D Session Summarizer")

# Initialize OpenAI client
client = openai.OpenAI(api_key=st.secrets["openai"]["openai_api_key"])

# Initialize party configuration
PARTY_MEMBERS = {
    "Mike": "Rogue",
    "Justin": "Fighter",
    "Dave": "Barbarian",
    "Steve": "Sorcerer",
    "Chris": "Bard",
    "Geoff": "Dungeon Master"
}

# File uploader
uploaded_file = st.file_uploader("Upload your D&D session transcript", type=['txt'])

if uploaded_file:
    if st.button('Generate Summary'):
        try:
            text = uploaded_file.read().decode('utf-8')
            
            with st.spinner('Processing transcript...'):
                sanitizer = DnDSanitizer()
                cleaned_text = sanitizer.sanitize(text)
                summary = generate_summary(cleaned_text, client)
            
            st.subheader("Summary:")
            st.write(summary)
            
            docx_file = create_docx(summary)
            st.download_button(
                label="Download Summary as DOCX",
                data=docx_file,
                file_name=f"summary_{uploaded_file.name.replace('.txt', '.docx')}",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
