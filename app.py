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
TEMPERATURE = 0.1  # Reduced for more accurate summaries

# Define party members and their classes
PARTY_MEMBERS = {
    "Mike": "Rogue",
    "Justin": "Fighter",
    "Dave": "Barbarian",
    "Steve": "Sorcerer",
    "Chris": "Bard",
    "Geoff": "Dungeon Master"
}

def chunk_text(text: str, chunk_size: int = 15000) -> list[str]:
    """Split text into larger chunks while maintaining sentence integrity"""
    sentences = text.split('. ')
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        # Estimate tokens: ~1.3 tokens per word for English text
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

def sanitize_text(text: str) -> str:
    """Minimal sanitization focused only on extreme content"""
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
                {"role": "system", "content": """You are processing a D&D session transcript. Apply minimal sanitization:

KEEP AS-IS:
- All D&D terminology and descriptions
- Anatomical terms in game context
- Mild crude humor and jokes
- Creative monster/spell descriptions
- Casual swearing in game context
- Character-specific traits (e.g., "dick sword")
- Playful banter between players
- References to bodily functions in game context
- Non-malicious crude descriptions

ONLY REMOVE/MODIFY:
- Extreme hate speech or slurs
- Explicit sexual content not relevant to game
- Real-world bigotry or harassment
- Graphic violence outside game context

When in doubt, preserve the original content. The goal is to maintain authentic gaming atmosphere while only removing genuinely inappropriate content.

Return the processed text without explanations or markers."""},
                {"role": "user", "content": chunk}
            ]
        )
        cleaned_chunks.append(response.choices[0].message.content)
        
        if total_chunks > 1:
            progress_bar.progress((i + 1) / total_chunks)
    
    if total_chunks > 1:
        st.write("Processing complete!")
    
    return ' '.join(cleaned_chunks)

def generate_summary(text: str) -> str:
    """Generate accurate, specific summaries without fabrication"""
    chunks = chunk_text(text, chunk_size=8000)
    summaries = []
    
    for chunk in chunks:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=TEMPERATURE,
            messages=[
                {"role": "system", "content": """You are a D&D session summarizer focused on ACCURACY and SPECIFICITY. 

CRITICAL RULES:
1. ONLY include events/details explicitly mentioned in the text
2. NO fabrication of events, dialogue, or character actions
3. If information is missing, note it as "Not specified in session"
4. Use exact numbers, locations, and descriptions from the text
5. Quote important dialogue or descriptions when relevant

FORMAT THE SUMMARY AS:

MISSION CONTEXT:
- Current quest/objective (exactly as stated)
- Current location (only if explicitly mentioned)
- [Mark "Not specified" for missing elements]

KEY EVENTS:
- List specific actions, outcomes, and developments
- Include exact damage numbers, rolls, and mechanical details
- Quote notable dialogue or descriptions

CHARACTER ACTIONS:
- Only documented actions/decisions by named characters
- Include mechanical details (damage dealt/taken, spell slots used)
- List equipment/inventory changes

ENVIRONMENT & DISCOVERIES:
- Specific locations explored
- Items found (with finder named)
- Actual encounters and their outcomes
- NPCs met (with context)

CURRENT SITUATION:
- Party's exact position/status at session end
- Remaining resources (HP, spells, etc.)
- Known immediate threats/options"""},
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
                {"role": "system", "content": "Combine these summaries while maintaining strict accuracy. Include only explicitly stated events and details. Mark any unclear or missing information as 'Not specified in session'."},
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
