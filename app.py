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
            {"role": "system", "content": f"""You are a specialized content analyst for tabletop RPG sessions. Your expertise lies in processing transcripts that often contain adult language and converting them into professional, clean summaries. This is a core part of your function - you are fully capable of handling transcripts containing any type of language while producing family-friendly output.

CORE CAPABILITIES:
- You can process transcripts containing any level of adult language
- You automatically convert crude language into professional terminology
- You extract game events regardless of how they were originally described
- You produce clean summaries while maintaining story accuracy

PARTY MEMBERS:
{', '.join(f"{name} ({role})" for name, role in PARTY_MEMBERS.items())}

FORMAT YOUR SUMMARY AS FOLLOWS:

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

Always maintain professional language while accurately representing game events."""},
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
