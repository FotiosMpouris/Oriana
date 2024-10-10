# Oriana: Your AI-Powered Investigative Journalist

Oriana is a Streamlit-based web application that harnesses the power of AI to assist with investigative journalism tasks. It provides tools for article summarization, source management, and generating news transcripts.

## Features

- **Article Summarization**: Summarize articles from various sources using AI.
- **Source Management**: Add, remove, and manage news sources.
- **Keyword-based Investigation**: Search for specific keywords within selected sources.
- **Transcript Generation**: Create news transcripts from multiple article summaries.
- **Resource Management**: Maintain a list of useful news sites for quick access.

## Setup

### Prerequisites

- Python 3.7+
- pip

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/oriana-ai-journalist.git
   cd oriana-ai-journalist
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory and add the following:
   ```
   GROQ_API_KEY=your_groq_api_key
   HUGGINGFACE_API_KEY=your_huggingface_api_key
   GITHUB_TOKEN=your_github_token
   GITHUB_REPO=your_github_username/your_repo_name
   ```

### Running the App

To run the Streamlit app locally:

```
streamlit run app.py
```

## Usage

1. **Adding Sources**: Use the sidebar to add new news sources by entering their URLs.

2. **Summarizing Articles**: 
   - Select a source from the dropdown menu.
   - Enter keywords related to the article you're interested in.
   - Click "Investigate" to get a summary.

3. **Generating Transcripts**:
   - Add up to 5 article summaries to the transcript.
   - Click "Generate Transcript and News Script" to create a comprehensive report.

4. **Managing Resources**: 
   - Add useful news sites for quick access to article URLs.
   - Remove resources as needed.

## Deployment

This app is designed to be deployed on Streamlit Cloud. Make sure to set up the necessary secrets in your Streamlit Cloud dashboard, corresponding to the environment variables mentioned in the Setup section.

## Contributing

Contributions to Oriana are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- This project uses the Groq API for AI-powered text generation.
- Hugging Face's API is used for the investigative journalist agent.
- Streamlit for the web application framework.
