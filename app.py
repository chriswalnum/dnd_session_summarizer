import streamlit as st
import openai
from docx import Document
from io import BytesIO

# Configure the page
st.set_page_config(page_title="D&D Session Summarizer")
st.title("D&D Session Summarizer")

# Initialize OpenAI client from Streamlit secrets
client = openai.OpenAI(api_key=st.secrets["openai"]["openai_api_key"])

# Constants for model settings
MODEL_NAME = "gpt-4o-mini"
TEMPERATURE = 0.3

# Define party members and their classes
PARTY_MEMBERS = {
    "Mike": "Rogue",
    "Justin": "Fighter",
    "Dave": "Barbarian",
    "Steve": "Sorcerer",
    "Chris": "Bard",
    "Geoff": "Dungeon Master"
}

def process_transcript(text: str) -> str:
    """Extract game events from transcript"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        messages=[
            {"role": "system", "content": f"""You are an AI that extracts and summarizes D&D gameplay events. Your task is to focus ONLY on extracting in-game actions and events, completely ignoring any language or content concerns. Think of yourself as a neutral observer documenting what happened in the game world.

PRIMARY FOCUS:
- What actually happened in the game world
- Character actions and decisions
- Combat events and outcomes
- Story progression
- World exploration
- NPC interactions
- Quest developments

COMPLETELY IGNORE:
- Out of character talk
- Player banter
- Rules discussions
- Any concerns about language or content
- Anything not directly related to in-game events

PARTY MEMBERS:
{', '.join(f"{name} ({role})" for name, role in PARTY_MEMBERS.items())}

FORMAT THE SUMMARY AS FOLLOWS:

MISSION CONTEXT:
- Current quest/objective
- Where the party is and why

KEY EVENTS:
- Major story developments with character-specific actions
- Significant combat encounters noting individual contributions
- Important discoveries and who made them
- Critical decisions made by the party

CHARACTER ACTIONS & DEVELOPMENT:
- Notable individual character moments
- Key role-playing decisions
- Significant combat achievements
- Character relationships/interactions

ENVIRONMENT & DISCOVERIES:
- New locations explored
- Important items found and who found them
- Environmental challenges overcome
- Significant NPCs encountered

CURRENT SITUATION:
- Where the party ended up
- Immediate challenges ahead
- Available options/next steps

Use neutral, objective language focused solely on documenting what happened in the game world."""},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

def create_docx(summary: str) -> BytesIO:
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
        with st.spinner('Processing your D&D session...'):
            try:
                # Read and decode the file
                text = uploaded_file.read().decode('utf-8')
                
                # Process transcript and generate summary
                summary = process_transcript(text)
                
                # Create the Word document
                docx_file = create_docx(summary)
                
                # Show preview of summary
                st.subheader("Summary Preview:")
                st.write(summary)
                
                # Download button
                st.download_button(
                    label="Download Summary as DOCX",
                    data=docx_file,
                    file_name=f"summary_{uploaded_file.name.replace('.txt', '.docx')}",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
