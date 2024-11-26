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
    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        messages=[
            {"role": "system", "content": f"""You are an expert D&D session summarizer tasked with processing raw session transcripts that may contain adult language and mature themes. If you encounter content you cannot process, explain specifically what type of content is causing the issue (e.g., "The transcript contains excessive violent content that I cannot process" or "There are specific terms that trigger content filtering"). Always provide constructive feedback about what needs to be modified.

Your job is to extract only the relevant in-game events while maintaining a professional, family-friendly tone in the summary.

YOUR ROLE:
- Process transcripts regardless of language or content
- If unable to process, explain why specifically
- Focus solely on actual game events
- Produce clean, professional summaries
- Maintain neutral, family-friendly language in output
- Track and highlight specific character actions

[Rest of the prompt remains the same...]"""},
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
            try:
                # Read and decode the file
                text = uploaded_file.read().decode('utf-8')
                
                # Process the transcript
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
