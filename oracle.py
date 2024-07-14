import streamlit as st
import requests
from bs4 import BeautifulSoup
from groq import Groq
from exa_py import Exa
import os
import re

exa = Exa(os.getenv('EXA_API_KEY'))

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

def clean_summary(summary):
    cleaned = re.sub(r'^Here is a summary .*?:', '', summary, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    return cleaned

def get_relevant_websites(prompt, num_results=3):
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
    
def generate_summary(content, max_length=150):
    try:
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides concise summaries. Summarize the content directly without any introductory phrases."},
                {"role": "user", "content": f"Summarize the following text in about {max_length} characters. Do not include any phrases like 'Here is a summary'. If the content is not relevant, just respond with 'IRRELEVANT':\n\n{content}"}
            ],
            max_tokens=100,
            temperature=0.7
        )
        summary = response.choices[0].message.content.strip()
        
       
        summary = clean_summary(summary)
        
        if "summary of the text in about" in summary.lower():
            return "IRRELEVANT"
   
        if len(summary) < 20: 
            return "IRRELEVANT"
        
        return summary
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return "IRRELEVANT"

def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
 
    return soup.get_text()

def generate_llm_response(prompt, context):
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

        response = chat_completion.choices[0].message.content
        return response.strip()

    except Exception as e:
        print(f"Error in generating LLM response: {str(e)}")
        return "Sorry, I couldn't generate a response due to an error."


def main():
    st.title("Web Search and AI Response App")

    user_prompt = st.text_input("Enter your search prompt:")

    if st.button("Search"):
        with st.spinner("Searching and processing..."):
            websites = get_relevant_websites(user_prompt)

            st.subheader("Relevant Websites:")
            for website in websites:
                st.write(f"[{website['title']}]({website['url']})")
                with st.spinner("Generating summary..."):
                    summary = generate_summary(website['full_content'])
                st.write("Summary:")
                st.write(summary)
                st.write("---")

            combined_content = "\n\n".join([website['full_content'] for website in websites])

       
            with st.spinner("Generating AI response..."):
                llm_response = generate_llm_response(user_prompt, combined_content)

            st.subheader("AI Response:")
            st.write(llm_response)


if __name__ == "__main__":
    main()
