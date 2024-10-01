import os
import pandas as pd
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Please set your GOOGLE_API_KEY in the .env file.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# Function to get Excel text
@st.cache_data
def get_excel_text(file_path):
    df = pd.read_excel(file_path)
    return df.to_string()

# Function to analyze the image
@st.cache_data
def analyze_image(_img):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = """
    Analyze the image of a product (cosmetics, food items, or medicine) and provide the following information:
    Briefly describe the product based on what you see and ask the user what they want you to do.
    Do not make any health claims or recommendations in this analysis.
    """
    response = model.generate_content([prompt, _img])
    return response.text

# Function to handle user input
def user_input(user_question, excel_data, image_analysis):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Analyze the ingredients of the product based on the given context and image analysis. 
    Provide a recommendation on whether the user should consume or apply the product.
    
    Excel Data Context:
    {excel_data}
    
    Image Analysis:
    {image_analysis}
    
    Human: {user_question}
    AI: Let's analyze this step by step:
    1. Ingredients mentioned in the image and context:
    2. Effects of these ingredients on the human body:
    3. Potential benefits:
    4. Potential risks:
    5. Recommendation:
    Answer these in under 300 words

    Please provide a detailed explanation for your recommendation.
    """
    response = model.generate_content(prompt)
    return response.text

# Streamlit application
def main():
    st.set_page_config("Ingredient Analysis Assistant")
    st.title("Ingredient Analysis Assistant")

    # Load Excel data
    excel_file_path = "Food_data.xlsx"
    if not os.path.exists(excel_file_path):
        st.error(f"Error: {excel_file_path} not found. Please make sure the file exists in the same directory as this script.")
        st.stop()

    excel_data = get_excel_text(excel_file_path)

    # Image upload
    uploaded_image = st.file_uploader("Upload an Image of the Product", type=["jpg", "jpeg", "png"])
    
    if uploaded_image is not None:
        img = Image.open(uploaded_image)
        st.image(img, caption="Uploaded Image", use_column_width=True)
        
        with st.spinner("Analyzing image..."):
            image_analysis = analyze_image(img)
            st.subheader("Image Analysis")
            st.write(image_analysis)

        # User question input
        user_question = st.text_input("Ask a question about the product:")

        if user_question:
            with st.spinner("Analyzing..."):
                response = user_input(user_question, excel_data, image_analysis)
                st.subheader("Analysis Result")
                st.write(response)

if __name__ == "__main__":
    main()