import streamlit as st
from pptx import Presentation
from pptx.util import Inches, Pt
from langchain_ollama.chat_models import ChatOllama
import re

# -------------------------------
# LLM Configuration (Deepseek-r1:8b running locally)
# -------------------------------
llm = ChatOllama(
    model="deepseek-r1:8b",
    base_url="http://127.0.0.1:11434"  # Update with your LLM server details
)

# -------------------------------
# Function to clean LLM output and extract only the Markdown numbered list
# -------------------------------

def clean_toc_md(raw_toc):
    """
    Remove extraneous text (such as reasoning) that appears between  and  tags,
    and extract only the numbered list. It finds the first line that starts with "1." 
    and returns all content from that line onward.
    """
    # Remove all text between  and  (inclusive), using DOTALL to match newlines.
    cleaned_text = re.sub(r'.*?', '', raw_toc, flags=re.DOTALL | re.IGNORECASE)
    lines = cleaned_text.splitlines()
    start_index = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("1."):
            start_index = i
            break
    cleaned_lines = lines[start_index:]
    return "\n".join(cleaned_lines)


# -------------------------------
# Function to generate Table of Contents in Markdown format
# -------------------------------
def generate_toc(topic):
    prompt = (
        f"Generate text contents in PPT style , for a PowerPoint presentation, on the topic: {topic}. "
        f"Output only content relevant to {topic} along with titles, without any reasoning or commentary from LLM"
    )
    response = llm.invoke(prompt)
    toc_raw = response.content
    return toc_raw
    #print("Raw TOC from LLM:", toc_raw)  # Debug print
    #toc_md = clean_toc_md(toc_raw)
    #print("Cleaned TOC from LLM:", toc_md)
    #return toc_md

# -------------------------------
# Function to create PowerPoint slides from the Markdown TOC (Wide Format)
# -------------------------------
def create_ppt(topic, toc_md, ppt_name):
    ppt = Presentation()
    # Set slide dimensions to 16:9 wide format
    ppt.slide_width = Inches(13.33)
    ppt.slide_height = Inches(7.5)
    
    # Title Slide
    title_slide_layout = ppt.slide_layouts[0]
    slide = ppt.slides.add_slide(title_slide_layout)
    slide.shapes.title.text = topic

    # Process the TOC Markdown into lines
    toc_lines = toc_md.splitlines()
    lines_per_slide = 8  # Adjust as needed for clean formatting
    num_slides = (len(toc_lines) + lines_per_slide - 1) // lines_per_slide

    # Create one or more slides for the Table of Contents
    for i in range(num_slides):
        slide_layout = ppt.slide_layouts[1]  # Title and Content layout
        slide = ppt.slides.add_slide(slide_layout)
        slide.shapes.title.text = f"Title-{i}"
        start = i * lines_per_slide
        end = min((i + 1) * lines_per_slide, len(toc_lines))
        content_text = "\n".join(toc_lines[start:end])
        placeholder = slide.placeholders[1]
        placeholder.text = content_text
        
        # Adjust text formatting: set auto size if available and force font size to 26
        try:
            from pptx.enum.text import MSO_AUTO_SIZE
            placeholder.text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
        except Exception:
            pass
        for paragraph in placeholder.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(26)

    if not ppt_name.lower().endswith(".pptx"):
        ppt_name += ".pptx"
    ppt.save(ppt_name)
    return ppt_name

# -------------------------------
# Streamlit Interface
# -------------------------------
st.title("AI-Generated PowerPoint Creator")
st.subheader("Generate a professional, wide-format presentation from your topic")

# 1. Enter Topic: a text box for long topics.
topic = st.text_area("Enter Topic:", height=100, value="Describe the topic for PPT")

# 2. Generate Content
if st.button("Generate Content"):
    if topic.strip() == "":
        st.error("Please enter a topic first.")
    else:
        toc_md = generate_toc(topic)
        st.session_state.toc_md = toc_md
        st.success("Content generated.")

# Editable generated contents (Markdown Format)
if "toc_md" in st.session_state:
    toc_md_edit = st.text_area("Generate Content :", st.session_state.toc_md, height=2000)
    st.session_state.toc_md = toc_md_edit

# 3. Enter PPT Name: suggest a default based on the topic (editable).
default_ppt_name = "PPT_" + "_".join(topic.split()[:5]) if topic.strip() != "" else "Default_Presentation"
ppt_name = st.text_input("Enter PPT Name:", value=default_ppt_name)

# 4. Generate Presentation with Progress Bar
if st.button("Generate Presentation"):
    if topic.strip() == "":
        st.error("Please enter a topic.")
    elif "toc_md" not in st.session_state or st.session_state.toc_md.strip() == "":
        st.error("Please generate the Table of Contents first.")
    else:
        progress_bar = st.progress(0)
        progress_bar.progress(20)
        toc_md_final = st.session_state.toc_md
        progress_bar.progress(50)
        ppt_file_name = create_ppt(topic, toc_md_final, ppt_name)
        progress_bar.progress(100)
        st.success("Presentation generated successfully!")
        with open(ppt_file_name, "rb") as file:
            st.download_button(
                label=f"Download {ppt_file_name}",
                data=file,
                file_name=ppt_file_name,
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )