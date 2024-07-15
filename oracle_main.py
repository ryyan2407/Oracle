import streamlit as st
import requests
from bs4 import BeautifulSoup
from groq import Groq
from exa_py import Exa
import os
import re
from operator import itemgetter
import cohere
import time

co = cohere.Client(os.getenv("COHERE_API_KEY"))
exa = Exa(os.getenv('EXA_API_KEY'))

groq_api_keys = [
    os.getenv("GROQ_API_KEY_1"),
    os.getenv("GROQ_API_KEY_2"),
    os.getenv("GROQ_API_KEY_3")
]

current_key_index = 0
client = Groq(api_key=groq_api_keys[current_key_index])

def switch_groq_api_key():
    global current_key_index, client
    current_key_index = (current_key_index + 1) % len(groq_api_keys)
    client = Groq(api_key=groq_api_keys[current_key_index])
    print(f"Switched to API key {current_key_index + 1}")

def clean_summary(summary):
    cleaned = re.sub(r'^Here is a summary .*?:', '', summary, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    return cleaned

def scrape_website(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() 
        soup = BeautifulSoup(response.content, 'html.parser')
      
        for script in soup(["script", "style"]):
            script.decompose()
        

        text = soup.get_text()
   
        lines = (line.strip() for line in text.splitlines())
        
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    except requests.RequestException as e:
        print(f"Error scraping website {url}: {str(e)}")
        return ""
    
def get_relevant_websites(prompt, num_results=5):
    try:
        response = exa.search_and_contents(
            prompt,
            use_autoprompt=True,
            num_results=num_results,
            text=True,
            highlights=True
        )

        websites = []
        for result in response.results:
            full_content = scrape_website(result.url)
            website = {
                "url": result.url,
                "title": result.title,
                "full_content": full_content
            }
            websites.append(website)

        return websites

    except Exception as e:
        print(f"Error in getting relevant websites: {str(e)}")
        return []

    
def generate_summary(content, max_length=300):
    try:
        response = co.chat(
            model="command-r-plus",
            message=f"Summarize the following text in about {max_length} characters. Do not include any phrases like 'Here is a summary'. If the content is not relevant, just respond with 'IRRELEVANT':\n\n{content}"
        )
        summary = response.text.strip()
        
        summary = clean_summary(summary)
        
        if "summary of the text in about" in summary.lower():
            return "IRRELEVANT"
        
        if len(summary) < 20:
            return "IRRELEVANT"
        
        return summary
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return "IRRELEVANT"


def generate_llm_response(prompt, context, max_retries=3):
    global client
    for attempt in range(max_retries):
        try:
            full_prompt = f"Context: {context}\n\nQuestion: {prompt}\n\nAnswer:"
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an advanced AI assistant integrated into a web search and analysis application. Your role is to:
                        1. Analyze and understand the context provided from multiple web sources.
                        2. Answer user questions based on this context, providing accurate and relevant information.
                        3. Synthesize information from various sources to give comprehensive answers.
                        4. If the context doesn't contain enough information to fully answer the question, clearly state this and provide the best possible answer based on available information.
                        5. Maintain a neutral, informative tone and avoid speculation beyond the provided context.
                        6. If appropriate, suggest areas where the user might want to search for additional information.
                        7. Always prioritize accuracy over completeness when information is limited.
                        Remember, your knowledge is based solely on the context provided for each query."""
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                model="llama3-70b-8192",
                max_tokens=1000,
                temperature=0.7,
            )
            return chat_completion.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Error in generating LLM response (attempt {attempt + 1}): {str(e)}")
            if "rate_limit_exceeded" in str(e):
                switch_groq_api_key()
                time.sleep(2)
            elif attempt == max_retries - 1:
                return "Sorry, I couldn't generate a response due to an error."
    

def main():
    st.title("Oracle")

    user_prompt = st.text_input("Enter your search prompt:")

    if st.button("Search"):
        with st.spinner("Searching and processing..."):
            websites = get_relevant_websites(user_prompt, num_results=5)

            relevant_websites = []
            for website in websites:
                with st.spinner(f"Generating summary for {website['url']}..."):
                    summary = generate_summary(website['full_content'])
                if summary != "IRRELEVANT":
                    relevant_websites.append({
                        "url": website['url'],
                        "title": website['title'],
                        "summary": summary,
                        "relevance_score": len(summary)
                    })

            top_3_websites = sorted(relevant_websites, key=itemgetter('relevance_score'), reverse=True)[:3]

            # Create two columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Top 3 Relevant Websites:")
                for website in top_3_websites:
                    with st.expander(f"{website['title']}"):
                        st.write(f"[{website['title']}]({website['url']})")
                        st.write("Summary:")
                        st.write(website['summary'])
                        st.write("---")

            with col2:
                combined_content = "\n\n".join([website['summary'] for website in top_3_websites])
                with st.spinner("Generating AI response..."):
                    llm_response = generate_llm_response(user_prompt, combined_content)

                st.subheader("AI Response:")
                st.write(llm_response)
                
if __name__ == "__main__":
    main()