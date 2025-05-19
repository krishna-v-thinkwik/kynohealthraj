import streamlit as st
import google.generativeai as genai
from playwright.sync_api import sync_playwright
import sys
import asyncio
import subprocess
import sys

# Run playwright install only once
try:
    subprocess.run(["playwright", "install", "chromium"], check=True)
except Exception as e:
    print("Failed to install playwright browsers:", e)

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
 
# Configure Gemini
GEMINI_API_KEY = "AIzaSyDoDT6-pFN_Bq3WLoDczx1zeKcMZrhlmvA"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')
 
def scrape_kynohealth():
    urls = [
        "https://www.kynohealth.com/",
        "https://www.kynohealth.com/provide-services",
        "https://www.kynohealth.com/about-us",
        "https://www.kynohealth.com/blog",
        "https://www.kynohealth.com/contact-us",
        "https://www.kynohealth.com/book-doctor/step-1",
        "https://www.kynohealth.com/terms-conditions",
        "https://www.kynohealth.com/return-policy",
        "https://www.kynohealth.com/return-policy",
    ]
 
    all_text = ""
 
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
 
            for url in urls:
                page.goto(url, wait_until="networkidle", timeout=15000)
 
                for button_text in ["View All", "Read More", "See More"]:
                    try:
                        page.locator(f"text={button_text}").first.click(timeout=3000)
                    except:
                        pass
 
                page_text = page.inner_text("body")
                all_text += f"\n\n--- Page: {url} ---\n\n" + page_text
 
            browser.close()
 
        return all_text
 
    except Exception as e:
        st.error(f"Scraping error: {str(e)}")
        return None
 
def ask_gemini(question, context):
    prompt = f"""
Context from KynoHealth website:
{context}
 
Question: {question}
 
Answer based on the context above. If the answer isn't in the context, say You've stumped me this time 😅 — can we explore it together?.
"""
 
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"
 
def main():
    st.title("KynoHealth Chatbot")
 
    # Scrape data once per run, cache manually using session state
    if 'kyno_data' not in st.session_state:
        with st.spinner("Scraping KynoHealth website and specified pages..."):
            st.session_state.kyno_data = scrape_kynohealth()
 
    st.write("Ask questions about KynoHealth:")
    question = st.text_input("Your question:", key="question")
 
    if question:
        if st.session_state.kyno_data:
            answer = ask_gemini(question, st.session_state.kyno_data)
            st.write("Answer:", answer)
        else:
            st.error("Failed to load website data")
 
if __name__ == "__main__":
    main()
