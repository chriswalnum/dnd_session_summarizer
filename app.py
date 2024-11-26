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

def chunk_text(text: str, chunk_size: int = 12000) -> list[str]:
    """Split text into chunks that won't exceed token limits"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        # Rough estimate: 1 word ≈ 1.5 tokens on average
        word_length = len(word) * 1.5
        if current_length + word_length > chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = word_length
        else:
            current_chunk.append(word)
            current_length += word_length
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks

def sanitize_text(text: str) -> str:
    """Step 1: Clean up vulgar content with chunk processing"""
    chunks = chunk_text(text)
    cleaned_chunks = []
    
    # Create a progress bar for chunk processing
    total_chunks = len(chunks)
    if total_chunks > 1:
        st.write(f"Processing {total_chunks} chunks of text...")
        progress_bar = st.progress(0)
    
    for i, chunk in enumerate(chunks):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.3,
            messages=[
                {"role": "system", "content": """You are a content sanitizer for D&D session transcripts. Your job is to:
1. Replace vulgar language with clean alternatives
2. Convert explicit descriptions to family-friendly versions
3. Maintain all game events and actions
4. Preserve character names and key details
5. Keep the narrative flow intact

Example transformations:
- Swear words → "curses", "exclaims", "shouts"
- Graphic violence → "defeats", "overcomes", "strikes"
- Adult themes → general descriptions of events
- Crude jokes → "[friendly banter]"

Return the cleaned text only, without any explanations or markers."""},
                {"role": "user", "content": chunk}
            ]
        )
        cleaned_chunks.append(response.choices[0].message.content)
        
        # Update progress bar if multiple chunks
        if total_chunks > 1:
            progress_bar.progress((i + 1) / total_chunks)
    
    if total_chunks > 1:
        st.write("Chunk processing complete!")
    
    return ' '.join(cleaned_chunks)

def generate_summary(text: str) -> str:
    """Step 2: Create initial summary from sanitized text"""
    # Split into chunks if needed
    chunks = chunk_text(text, chunk_size=8000)  # Smaller chunks for summary
    summaries = []
    
    for chunk in chunks:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=TEMPERATURE,
            messages=[
                {"role": "system", "content": f"""You are a D&D session summarizer. Create a professional summary of the game events.

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
- Available options/next steps"""},
                {"role": "user", "content": chunk}
            ]
        )
        summaries.append(response.choices[0].message.content)
    
    # If we had multiple chunks, combine them
    if len(summaries) > 1:
        combined_summary = "\n\n".join(summaries)
        # Create a final unified summary
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=TEMPERATURE,
            messages=[
                {"role": "system", "content": "You are a D&D session summarizer. Combine these multiple summaries into one coherent summary, removing any redundancy while maintaining all important events and details."},
                {"role": "user", "content": combined_summary}
            ]
        )
        return response.choices[0].message.content
    else:
        return summaries[0]

def polish_summary(text: str) -> str:
    """Step 3: Final polish to ensure professional tone"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0.3,
        messages=[
            {"role": "system", "content": """You are an editor reviewing D&D session summaries. Your task is to:
1. Ensure completely professional language
2. Maintain clear and engaging narrative flow
3. Keep all game events and character actions
4. Format the text consistently
5. Verify section headers are properly placed

Make minimal changes - focus only on language and tone while preserving all content.
Return the polished summary without any explanations."""},
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
        try:
            # Read and decode the file
            text = uploaded_file.read().decode('utf-8')
            
            # Step 1: Sanitize content
            with st.spinner('Cleaning up transcript...'):
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
