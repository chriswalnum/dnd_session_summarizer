# Version 1.2.1
import streamlit as st
import openai
from docx import Document
from io import BytesIO
import re
from typing import Set, List

# [Previous imports and configs remain the same until sanitization class]

class DnDSanitizer:
    def __init__(self):
        self.dnd_allowlist = {
            'attack', 'damage', 'kill', 'dead', 'death', 'blood', 
            'dragon', 'demon', 'devil', 'hell', 'undead', 'zombie',
            'corpse', 'body', 'wound', 'ritual', 'curse'
        }
        self.profanity_set = self._load_profanity_list()
        
    def _load_profanity_list(self) -> Set[str]:
        # Replace with your preferred profanity list
        return {'badword1', 'badword2'}  # Placeholder
        
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

def sanitize_text(text: str) -> str:
    """Minimal sanitization focused only on extreme content"""
    sanitizer = DnDSanitizer()
    chunks = chunk_text(text)
    cleaned_chunks = []
    
    total_chunks = len(chunks)
    if total_chunks > 1:
        st.write(f"Processing {total_chunks} chunks of text...")
        progress_bar = st.progress(0)
    
    for i, chunk in enumerate(chunks):
        # Pre-filter with local sanitizer
        pre_cleaned = sanitizer.sanitize(chunk)
        
        # Use OpenAI for final check
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.3,
            messages=[
                {"role": "system", "content": """You are processing a D&D session transcript. Apply minimal sanitization:

KEEP AS-IS:
- All D&D terminology and descriptions
- Anatomical terms in game context
- Mild crude humor and jokes
- Creative monster/spell descriptions
- Casual swearing in game context
- Character-specific traits
- Playful banter between players
- References to bodily functions in game context
- Non-malicious crude descriptions

ONLY REMOVE/MODIFY:
- Extreme hate speech or slurs
- Explicit sexual content not relevant to game
- Real-world bigotry or harassment
- Graphic violence outside game context

When in doubt, preserve the original content."""},
                {"role": "user", "content": pre_cleaned}
            ]
        )
        cleaned_chunks.append(response.choices[0].message.content)
        
        if total_chunks > 1:
            progress_bar.progress((i + 1) / total_chunks)
    
    if total_chunks > 1:
        st.write("Processing complete!")
    
    return ' '.join(cleaned_chunks)

# [Rest of the code remains the same]

def generate_summary(text: str) -> str:
    """Generate engaging, accurate summaries that capture D&D flavor"""
    chunks = chunk_text(text, chunk_size=8000)
    summaries = []
    
    for chunk in chunks:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=TEMPERATURE,
            messages=[
                {"role": "system", "content": """You are an experienced D&D Dungeon Master creating engaging session summaries.

WRITE IN AN ENTERTAINING D&D STYLE:
- Use vivid D&D-appropriate language and terminology
- Include memorable character moments and banter
- Capture the spirit of the game while staying factual
- Embrace the humor and unique elements of the session
- Keep character-specific quirks and traits
- Include mechanical details within the narrative

FORMAT THE SUMMARY AS:

QUEST STATUS:
- Current objectives and progress
- Recent major developments
- Party's immediate goals

BATTLE REPORT:
- Detailed combat encounters with specific numbers
- Tactical decisions and their outcomes
- Spells cast and abilities used
- Damage dealt and received
- Enemy types and quantities

PARTY HIGHLIGHTS:
[For each character present, include their notable actions with specific details]
- Combat achievements
- Role-playing moments
- Character-specific abilities used
- Equipment/resource usage

EXPLORATION & DISCOVERIES:
- Areas investigated
- Traps encountered and outcomes
- Items found
- Information gained
- NPCs encountered

CURRENT STATUS:
- Party's position and condition
- Available resources
- Immediate threats
- Known options ahead

Maintain the actual events and numbers while making the narrative engaging and D&D-appropriate."""},
                {"role": "user", "content": chunk}
            ]
        )
        summaries.append(response.choices[0].message.content)
    
    if len(summaries) > 1:
        combined_summary = "\n\n".join(summaries)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=TEMPERATURE,
            messages=[
                {"role": "system", "content": """Combine these summaries into one cohesive narrative that maintains accuracy. Keep:
- All specific details and numbers
- Unique character elements and party dynamics
- Mechanical information within the story
- D&D-appropriate language and terminology
- The humor and spirit of the session"""},
                {"role": "user", "content": combined_summary}
            ]
        )
        return response.choices[0].message.content
    
    return summaries[0]

def polish_summary(text: str) -> str:
    """Final polish to ensure professional formatting while preserving content"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0.3,
        messages=[
            {"role": "system", "content": """You are editing a D&D session summary. Your task is to:
1. Ensure consistent formatting
2. Maintain all specific details and numbers
3. Preserve gaming terminology and character references
4. Keep exact damage values and mechanical information
5. Format section headers clearly

Make minimal content changes - focus on formatting and readability.
Return the polished summary without any explanations."""},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

def create_docx(summary: str) -> BytesIO:
    """Create a Word document from the summary"""
    doc = Document()
    doc.add_heading('D&D Session Summary', 0)
    doc.add_paragraph(summary)
    
    docx_file = BytesIO()
    doc.save(docx_file)
    docx_file.seek(0)
    return docx_file

# File uploader
uploaded_file = st.file_uploader("Upload your D&D session transcript", type=['txt'])

if uploaded_file:
    # Add a generate button
    if st.button('Generate Summary'):
        try:
            # Read and decode the file
            text = uploaded_file.read().decode('utf-8')
            
            # Step 1: Sanitize content
            with st.spinner('Processing transcript...'):
                cleaned_text = sanitize_text(text)
            
            # Step 2: Generate summary
            with st.spinner('Generating summary...'):
                raw_summary = generate_summary(cleaned_text)
            
            # Step 3: Polish summary
            with st.spinner('Polishing summary...'):
                final_summary = polish_summary(raw_summary)
            
            # Create the Word document
            docx_file = create_docx(final_summary)
            
            # Show preview of summary
            st.subheader("Summary Preview:")
            st.write(final_summary)
            
            # Download button
            st.download_button(
                label="Download Summary as DOCX",
                data=docx_file,
                file_name=f"summary_{uploaded_file.name.replace('.txt', '.docx')}",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
        except Exception as e:
            st.error("An error occurred during processing.")
            st.error(f"Error details: {str(e)}")
