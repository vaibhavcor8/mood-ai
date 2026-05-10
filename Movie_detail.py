import streamlit as st
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

# Load model
model = ChatMistralAI(model="mistral-small-2506")

# Prompt Template
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an advanced information extraction assistant.

Your job is to carefully analyze the given paragraph and extract all important and useful information in a clean, readable format.

Extract:
- Movie Title
- Genre
- Release Year
- Director
- Cast
- Plot
- Setting / Location
- Themes
- Soundtrack / Music
- Ratings
- Important Highlights
- Keywords
- Quick Summary

Rules:
- Keep output clean and structured
- Use headings and bullet points
- If something is missing write 'Not Mentioned'
- Do not hallucinate information
"""
    ),
    (
        "human",
        """
Extract information from the paragraph:

{paragraph}
"""
    )
])

# Streamlit UI
st.title("Movie Information Extractor")

paragraph = st.text_area("Enter Paragraph")

if st.button("Extract Information"):

    final_prompt = prompt.invoke({
        "paragraph": paragraph
    })

    response = model.invoke(final_prompt)

    st.write(response.content)