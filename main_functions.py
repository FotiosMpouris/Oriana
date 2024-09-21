import os
from dotenv import load_dotenv
from groq import Groq
from together import Together
from exa_py import Exa
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from collections import defaultdict
import numpy as np
from datetime import datetime
import json

# Load environment variables and initialize clients
load_dotenv()
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
together_client = Together(api_key=st.secrets["TOGETHER_API_KEY"])
exa_client = Exa(api_key=st.secrets["EXA_API_KEY"])

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

    def get_recent_articles(self, subject, source, max_articles=10):
        try:
            result = exa_client.search_and_contents(
                f"Recent articles about {subject} from {source}",
                num_results=max_articles,
                use_autoprompt=True
            )
            return [{
                'title': item.title,
                'url': item.url,
                'content': item.text,
                'published_date': item.published_date,
                'source': source
            } for item in result.results]
        except Exception as e:
            st.error(f"Error searching {source}: {str(e)}")
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
        if not source:
            return f"No source selected. Please select a source to search."
        
        results = self.search_source(question, source)
        
        if not results:
            return f"No recent news stories found from the selected source ({source})."
    
        prompt = f"""Based on the following recent news from {source}:

        {'\n'.join([f"From {r['url']}:\n{r['content']}" for r in results])}

        Answer the following question: {question}

        If the information provided is not sufficient to answer the question, provide a summary of the recent news instead."""

        return self.investigative_journalist_agent(prompt)

    def get_top_stories_from_source(self, source_url, limit=5):
        try:
            result = exa_client.search_and_contents(
                f"Top stories from {source_url}",
                num_results=limit,
                use_autoprompt=True
            )
            return [{
                'title': item.title,
                'url': item.url,
                'published_date': item.published_date,
                'source': source_url
            } for item in result.results]
        except Exception as e:
            st.error(f"Error searching {source_url}: {str(e)}")
            return []

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

def scrape_certainteed(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find('h1').get_text() if soup.find('h1') else ""
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        headings = [h.get_text() for h in soup.find_all(['h2', 'h3', 'h4'])]
        list_items = [li.get_text() for li in soup.find_all('li')]

        page_content = f"Title: {title}\n\n"
        page_content += "Headings:\n" + "\n".join(headings) + "\n\n"
        page_content += "Content:\n" + "\n".join(paragraphs) + "\n\n"
        page_content += "List Items:\n" + "\n".join(list_items)

        max_content_length = 2000
        if len(page_content) > max_content_length:
            return page_content[:max_content_length] + "..."

        return page_content if page_content else "No relevant content found on this page."

    except requests.exceptions.RequestException as e:
        return f"An error occurred while trying to scrape the CertainTeed URL: {e}"

def scrape_specific_url(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        paragraphs = [p.get_text() for p in soup.find_all('p')]
        headings = [h.get_text() for h in soup.find_all(['h1', 'h2', 'h3'])]
        list_items = [li.get_text() for li in soup.find_all('li')]

        page_content = "\n".join(headings + paragraphs + list_items)

        max_content_length = 1000
        if len(page_content) > max_content_length:
            return page_content[:max_content_length] + "..."

        return page_content if page_content else "No relevant content found on this page. Please check the URL."

    except requests.exceptions.RequestException as e:
        return f"An error occurred while trying to scrape the URL: {e}"

def get_common_questions():
    default_questions = [
        "What are the top stories of the week?",
        "Are there any bills in front of the Senate?",
        "What are the common themes in the news?",
        "What are the top ten most important news stories?",
        "Name the news story that involves the most overall spending."
    ]
    
    try:
        response = together_client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": "Generate 5 common questions about news in the United States."},
                {"role": "user", "content": "Please provide 5 common questions about the U.S. Senate."}
            ],
            max_tokens=150,
        )
        generated_questions = response.choices[0].message.content.split('\n')
        return generated_questions if len(generated_questions) == 5 else default_questions
    except Exception as e:
        st.warning(f"Unable to generate questions using API: {str(e)}. Using default questions.")
        return default_questions

def search_news_stories(query):
    try:
        result = exa_client.search_and_contents(
            f"Recent news stories about: {query} from the past day",
            num_results=3,
            use_autoprompt=True
        )
        return '\n'.join([f"Result {i+1} ({item.published_date}): {item.title}\n{item.text[:200]}..." for i, item in enumerate(result.results)])
    except Exception as e:
        st.error(f"Error in search_news_stories: {str(e)}")
        return f"Unable to search for '{query}' due to an error."
