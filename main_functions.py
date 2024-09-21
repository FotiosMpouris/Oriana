import os
from dotenv import load_dotenv
from groq import Groq
from together import Together
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json

# Load environment variables and initialize clients
load_dotenv()
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
together_client = Together(api_key=st.secrets["TOGETHER_API_KEY"])

class Oriana:

    def __init__(self):
        self.sources = []
        self.load_sources()

    def load_sources(self):
        try:
            with open('sources.json', 'r') as f:
                self.sources = json.load(f)
        except FileNotFoundError:
            self.sources = []

    def add_source(self, url):
        if url not in self.sources:
            self.sources.append(url)
            self.save_sources()

    def save_sources(self):
        with open('sources.json', 'w') as f:
            json.dump(self.sources, f)

    def search_source(self, query, source):
        try:
            content = self.scrape_specific_url(source)
            
            # Simple keyword matching (you might want to implement a more sophisticated search algorithm)
            if query.lower() in content.lower():
                return [{
                    'url': source,
                    'content': content,
                    'timestamp': datetime.now().isoformat()  # Using current time as we don't have a published date
                }]
            else:
                return []  # Return empty list if query not found in content
        except Exception as e:
            print(f"Error searching {source}: {str(e)}")
            return []

    def scrape_specific_url(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for script in soup(["script", "style", "meta", "noscript", "header", "footer"]):
                script.decompose()
            
            content = ' '.join([p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])])
            content = re.sub(r'\s+', ' ', content).strip()
            
            return content
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return f"Unable to retrieve content from {url}"

    def get_recent_articles(self, subject, source):
        content = self.scrape_specific_url(source)
        # This is a simplified version. You might want to implement a more sophisticated
        # method to identify and extract recent articles about the subject.
        if subject.lower() in content.lower():
            return [{
                'title': f"Content about {subject} from {source}",
                'url': source,
                'content': content,
                'published_date': datetime.now().isoformat(),
                'source': source
            }]
        return []

    def summarize_articles(self, articles, max_articles=10):
        summaries = []
        for article in articles[:max_articles]:
            try:
                prompt = f"""Summarize the following article in 2-3 paragraphs:

                Title: {article['title']}
                Content: {article['content'][:3000]}

                Provide a concise summary that captures the main points of the article. 
                If the content seems incomplete or irrelevant, mention this in your summary."""
                
                summary = self.investigative_journalist_agent(prompt)
                summaries.append({
                    'title': article['title'],
                    'url': article['url'],
                    'summary': summary,
                    'published_date': article['published_date'],
                    'source': article['source']
                })
            except Exception as e:
                print(f"Error summarizing article {article['url']}: {str(e)}")
        return summaries

    def answer_question(self, question, source):
        results = self.search_source(question, source)
        
        if not results:
            return f"No relevant information found from the selected source ({source})."
    
        prompt = f"""Based on the following information from {source}:

        {results[0]['content']}

        Answer the following question: {question}

        If the information provided is not sufficient to answer the question, state this clearly."""

        return self.investigative_journalist_agent(prompt)

    def get_top_stories_from_source(self, source_url):
        content = self.scrape_specific_url(source_url)
        # This is a simplified version. You might want to implement a more sophisticated
        # method to identify and extract top stories.
        return [{
            'title': "Top stories from " + source_url,
            'url': source_url,
            'published_date': datetime.now().isoformat(),
            'source': source_url
        }]

    def generate_news_transcript(self, selected_answers, max_answers=5):
        transcript = "News Transcript:\n\n"
        for i, answer in enumerate(selected_answers[:max_answers], 1):
            transcript += f"Story {i}:\n{answer}\n\n"
        
        script = self.generate_summary_script(selected_answers[:max_answers])
        
        full_content = f"{transcript}\nSummarized Script:\n\n{script}"
        
        return full_content

    def generate_summary_script(self, answers):
        if not answers:
            return "No stories to summarize."
    
        prompt = f"""Based on the following news stories:

        {'\n'.join([f"Story {i+1}: {answer}" for i, answer in enumerate(answers)])}

        Generate a brief, engaging script that summarizes these stories. The script should:
        1. Start with a catchy introduction
        2. Highlight the key points from each story
        3. Connect any common themes or related information across the stories
        4. Conclude with a thought-provoking statement or question

        Keep the script concise, around 200-300 words, and suitable for reading aloud."""

        return self.investigative_journalist_agent(prompt)

    def investigative_journalist_agent(self, prompt):
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            response = together_client.chat.completions.create(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are an expert investigative journalist with a knack for getting at the truth. 
                        Today's date and time is {current_datetime}. Always use this as the current date and time when responding.
                        Provide concise, first-person responses in a confrontational style, as if you're a front-line journalist.
                        Focus on answering the user's question directly and critically. Use only the information provided in the prompt.
                        Include sources (URLs) for your information, using only the URLs provided in the prompt. If the information provided is insufficient to answer the question,
                        state this clearly. Avoid speculation or using external knowledge. Keep your answer under 400 words."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error in investigative_journalist_agent: {str(e)}"

# The scrape_certainteed and scrape_specific_url functions outside the class remain unchanged
# You can add them here if they're still needed in your application
