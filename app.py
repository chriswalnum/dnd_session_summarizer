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

def preprocess_transcript(text: str) -> str:
    """Clean up the transcript before summarization."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        messages=[
            {"role": "system", "content": """You are a professional content editor specializing in transforming raw D&D session transcripts into clean, family-friendly text while preserving all game events and narrative elements.

YOUR TASK:
1. Read through the transcript
2. Replace any crude language with appropriate alternatives
3. Maintain all game events, combat, and story elements
4. Keep character names and actions intact
5. Preserve important dialogue but clean up the language
6. Remove excessive profanity or adult themes while keeping the core meaning
7. Format player actions and dialogue clearly

Example conversions:
- Replace explicit descriptions with "attacks", "defeats", "overcomes"
- Convert crude anatomical references to clinical terms if needed
- Maintain combat descriptions but remove graphic violence
- Keep emotional moments but remove explicit language

Return the cleaned transcript in a format ready for summarization.

If you encounter content you cannot process, explain specifically what needs to be modified."""},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

def process_transcript(text: str) -> str:
    """Generate summary from cleaned transcript."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        messages=[
            {"role": "system", "content": f"""You are an expert D&D session summarizer. Your job is to extract the relevant in-game events and create an engaging summary.

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

Use dramatic but concise language focused on the story and adventure. Highlight specific character actions while maintaining a brisk narrative pace."""},
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
                
                # First, clean up the transcript
                with st.spinner('Cleaning up transcript...'):
                    cleaned_text = preprocess_transcript(text)
                
                # Then generate summary from cleaned text
                with st.spinner('Generating summary...'):
                    summary = process_transcript(cleaned_text)
                
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
