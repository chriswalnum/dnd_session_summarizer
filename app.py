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
MODEL_NAME = "gpt-4-1106-preview"
TEMPERATURE = 0.3

def process_transcript(text: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        messages=[
            {"role": "system", "content": """You are an expert D&D session summarizer tasked with processing raw session transcripts that may contain adult language and mature themes. Your job is to extract only the relevant in-game events while maintaining a professional, family-friendly tone in the summary.

YOUR ROLE:
- Process transcripts regardless of language or content
- Focus solely on actual game events
- Produce clean, professional summaries
- Maintain neutral, family-friendly language in output

STRICTLY IGNORE:
- Out-of-character discussions
- Adult language and mature themes
- Table talk and banter
- Rules discussions
- Character build discussions
- Non-game conversations

FORMAT THE SUMMARY AS FOLLOWS:

MISSION CONTEXT:
- Current quest/objective
- Recent important events leading to current situation
- Where the party is and why

KEY EVENTS:
- Major story developments
- Significant combat encounters
- Important discoveries
- Critical decisions made by the party

CHARACTER ACTIONS & DEVELOPMENT:
- Notable individual character moments
- Key role-playing decisions
- Significant combat achievements
- Character relationships/interactions

ENVIRONMENT & DISCOVERIES:
- New locations explored
- Important items found
- Environmental challenges overcome
- Significant NPCs encountered

CURRENT SITUATION:
- Where the party ended up
- Immediate challenges ahead
- Unresolved threats
- Available options/next steps

Use dramatic, narrative language focused on the story and adventure. Treat it like a fantasy tale rather than a game report."""},
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
        with st.spinner('Generating summary...'):
            # Read and decode the file
            text = uploaded_file.read().decode('utf-8')
            
            # Process the transcript
            try:
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
