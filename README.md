# Oracle - AI-Powered Web Search and Analysis

Oracle is an advanced web application that combines web searching capabilities with AI-powered analysis to provide users with relevant information and intelligent responses to their queries.

## Features

- **Intelligent Web Search**: Searches the web for relevant content based on user queries.
- **Content Summarization**: Automatically generates concise summaries of web content.
- **AI-Powered Analysis**: Utilizes advanced language models to analyze search results and generate comprehensive responses.
- **User-Friendly Interface**: Built with Streamlit for an intuitive and responsive user experience.
- **Multi-API Integration**: Leverages multiple AI services (Groq, Cohere, Exa) for robust functionality.

## Prerequisites

Before you begin, ensure you have met the following requirements:
- Python 3.7+
- pip (Python package manager)

## Installation

1. Clone the repository:
   git clone https://github.com/yourusername/oracle.git
   cd oracle
2. Create a virtual environment:
   python -m venv oracle_env
3. Install the required packages:
   pip install -r requirements.txt

## Configuration

You need to set up API keys for the services used by Oracle. Create a `.env` file in the project root and add your API keys:

EXA_API_KEY=your_exa_api_key
GROQ_API_KEY=your_groq_api_key
COHERE_API_KEY=your_cohere_api_key

## Usage

To run the Oracle application:

1. Ensure your virtual environment is activated.
2. Run the Streamlit app:
   streamlit run oracle_main.py
3. Open your web browser and go to the URL provided by Streamlit (usually `http://localhost:8501`).
4. Enter your search query in the input field and click "Search".
5. Oracle will display relevant website summaries and an AI-generated response based on the search results.

## Acknowledgements

- [Streamlit](https://streamlit.io/) for the web application framework
- [Groq](https://groq.com/) for AI language processing
- [Cohere](https://cohere.ai/) for AI-powered text generation
- [Exa](https://exa.ai/) for web search capabilities
