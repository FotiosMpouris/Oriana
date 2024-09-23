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
from newspaper import Article
import nltk
nltk.download('punkt', quiet=True)

# Load environment variables and initialize clients
load_dotenv()
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
#together_client = Together(api_key=st.secrets["TOGETHER_API_KEY"])
HUGGINGFACE_API_KEY = st.secrets["HUGGINGFACE_API_KEY"]

class Oriana:

    def __init__(self):
        self.sources = []
        self.resources = {}
        self.load_sources()
        self.load_resources()

    def load_sources(self):
        try:
            with open('sources.json', 'r') as f:
                self.sources = json.load(f)
        except FileNotFoundError:
            self.sources = []

    def save_sources(self):
        with open('sources.json', 'w') as f:
            json.dump(self.sources, f)

    def add_source(self, url):
        if url not in self.sources:
            self.sources.append(url)
            self.save_sources()

    # def remove_source(self, url):
    #     if url in self.sources:
    #         self.sources.remove(url)
    #         self.save_sources()
    def remove_source(self, url):
        if url in self.sources:
            self.sources.remove(url)
        # Explicitly save the updated sources to the JSON file
            with open('sources.json', 'w') as f:
                json.dump(self.sources, f)

    def load_resources(self):
        try:
            with open('resources.json', 'r') as f:
                self.resources = json.load(f)
        except FileNotFoundError:
            self.resources = {}

    def save_resources(self):
        with open('resources.json', 'w') as f:
            json.dump(self.resources, f)

    def add_resource(self, name, url):
        if len(self.resources) < 30:
            self.resources[name] = url
            self.save_resources()
        else:
            raise ValueError("Maximum number of resources (30) reached. Please remove some before adding more.")

    
    def remove_resource(self, name):
        if name in self.resources:
            del self.resources[name]
            self.save_resources()

    def get_resources(self):
        return self.resources

    def search_source(self, keywords, source):
        try:
            content = self.scrape_specific_url(source)
            
            # Split keywords and create a regex pattern
            keyword_list = [keyword.strip().lower() for keyword in keywords.split(',')]
            pattern = '|'.join(r'\b{}\b'.format(re.escape(keyword)) for keyword in keyword_list)
            
            # Search for keywords in the content
            matches = re.findall(pattern, content.lower())
            
            if matches:
                return [{
                    'url': source,
                    'content': content,
                    'timestamp': datetime.now().isoformat(),
                    'matches': matches
                }]
            else:
                return []
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

    def get_webpage_articles(self, subject, url):
        try:
            article = self.extract_article(url)
            if subject.lower() in article['text'].lower():
                return [{
                    'title': article['title'],
                    'url': url,
                    'content': article['text'],
                    'published_date': article['publish_date'] or datetime.now().isoformat(),
                    'source': url
                }]
            return []
        except Exception as e:
            print(f"Error processing webpage {url}: {str(e)}")
            return []

    def extract_article(self, url):
        article = Article(url)
        article.download()
        article.parse()
        return {
            'title': article.title,
            'text': article.text,
            'publish_date': article.publish_date
        }

    def summarize_articles(self, articles, max_articles=5):
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

    def answer_question(self, keywords, source):
        results = self.search_source(keywords, source)
        
        if not results:
            return f"No relevant information found from the selected source ({source}) using the provided keywords: {keywords}. Please try different keywords or check if the article content matches your search terms."
    
        content = results[0]['content']
        matches = results[0]['matches']
        
        prompt = f"""Based on the following information from {source}:

        {content[:3000]}  # Limit content to first 3000 characters to avoid token limits

        Summarize the article, focusing on the following key points: {', '.join(matches)}

        Provide a concise summary that captures the main points of the article, especially those related to the key points mentioned above. If any key points are not addressed in the article, mention that they were not found in the content."""

        return self.investigative_journalist_agent(prompt)

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

        Keep the script concise, around 300-500 words, and suitable for reading aloud."""

        return self.investigative_journalist_agent(prompt)
    
    def investigative_journalist_agent(self, prompt):
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
            headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        
            system_prompt = f"""You are an expert investigative journalist with a knack for getting at the truth. 
            Today's date and time is {current_datetime}. Always use this as the current date and time when responding.
            Provide concise, first-person responses in a confrontational style, as if you're a front-line journalist.
            Focus on answering the user's question directly and critically. Use only the information provided in the prompt.
            Include sources (URLs) for your information, using only the URLs provided in the prompt. If the information provided is insufficient to answer the question,
            state this clearly. Avoid speculation or using external knowledge. Keep your answer under 400 words."""

            full_prompt = f"{system_prompt}\n\nHuman: {prompt}\n\nAssistant:"
        
            payload = {
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": 800,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }

            response = requests.post(url, headers=headers, json=payload)
        
            if response.status_code != 200:
                return f"Error: API returned status code {response.status_code}. Response: {response.text}"

            response_json = response.json()

            if isinstance(response_json, list) and len(response_json) > 0:
                return response_json[0]['generated_text']
            elif 'generated_text' in response_json:
                return response_json['generated_text']
            else:
                return f"Error: Unexpected response format. Response: {response_json}"

        except requests.RequestException as req_err:
            return f"Error: Request to Hugging Face API failed. {str(req_err)}"
        except Exception as e:
            return f"Error in investigative_journalist_agent: {str(e)}"

    
    # def investigative_journalist_agent(self, prompt):
    #     current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     try:
    #         response = huggingface_client.chat.completions.create(
    #             model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    #             messages=[
    #                 {
    #                     "role": "system",
    #                     "content": f"""You are an expert investigative journalist with a knack for getting at the truth. 
    #                     Today's date and time is {current_datetime}. Always use this as the current date and time when responding.
    #                     Provide concise, first-person responses in a confrontational style, as if you're a front-line journalist.
    #                     Focus on answering the user's question directly and critically. Use only the information provided in the prompt.
    #                     Include sources (URLs) for your information, using only the URLs provided in the prompt. If the information provided is insufficient to answer the question,
    #                     state this clearly. Avoid speculation or using external knowledge. Keep your answer under 400 words."""
    #                 },
    #                 {
    #                     "role": "user",
    #                     "content": prompt
    #                 }
    #             ],
    #             max_tokens=800,
    #             temperature=0.7,
    #         )
    #         return response.choices[0].message.content
    #     except Exception as e:
    #         return f"Error in investigative_journalist_agent: {str(e)}"
