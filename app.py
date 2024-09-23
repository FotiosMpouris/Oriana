import streamlit as st
from main_functions import Oriana
import time
import logging
import base64
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

@st.cache_resource(hash_funcs={Oriana: lambda _: None})
def get_oriana_instance():
    return Oriana()

# Use this function to get the Oriana instance
oriana = get_oriana_instance()

# Function to load and encode the image
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Load logo
def load_image_path(image_name):
    for folder in ['images', 'assets']:
        path = os.path.join(folder, image_name)
        if os.path.exists(path):
            return path
    return None

logo_path = load_image_path("logo.png")

# Custom CSS for layout
st.markdown("""
    <style>
    .logo-title {
        display: flex;
        align-items: center;
    }
    .logo-title h1 {
        font-size: 3em;
        margin-right: 10px;
    }
    .logo-title img {
        height: 1em;
        width: auto;
    }
    .tagline {
        font-size: 1.5em;
        font-weight: normal;
    }
    </style>
    """, unsafe_allow_html=True)

# Display title with logo
if logo_path:
    logo_base64 = get_base64_of_bin_file(logo_path)
    st.markdown(f"""
        <div class="logo-title">
            <h1>Oriana</h1>
            <img src="data:image/png;base64,{logo_base64}" alt="Oriana logo">
        </div>
        <h3 class="tagline">Your AI-Powered Investigative Journalist</h3>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
        <h1 style='font-size: 3em;'>Oriana</h1>
        <h3 style='font-size: 1.5em; font-weight: normal;'>Your AI-Powered Investigative Journalist</h3>
        """, unsafe_allow_html=True)

# Sidebar content
st.sidebar.header("Add News Source")
new_source = st.sidebar.text_input("Enter a new source URL:")
if st.sidebar.button("Add Source"):
    try:
        oriana.add_source(new_source)
        st.sidebar.success(f"Added source: {new_source}")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Error adding source: {str(e)}")

# Display current sources
st.sidebar.header("Current Sources")
for source in oriana.sources:
    col1, col2 = st.sidebar.columns([3, 1])
    col1.write(source)
    if col2.button("X", key=f"remove_{source}"):
        if st.sidebar.button("Done with this?", key=f"confirm_{source}"):
            try:
                updated_sources = oriana.remove_source(source)
                st.sidebar.success(f"Removed source: {source}")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error removing source: {str(e)}")
                logging.error(f"Error removing source {source}: {str(e)}")

# Debug info
if st.sidebar.checkbox("Show Debug Info"):
    st.sidebar.write("Current sources:", oriana.sources)

# About Oriana in sidebar
st.sidebar.header("About Oriana")
with st.sidebar.expander("ℹ️ Learn More"):
    st.info("""
    Dive into the world of cutting-edge investigative journalism with Oriana, your tireless AI research companion. This innovative app harnesses the power of advanced artificial intelligence to sift through a vast array of sources, delivering the most relevant and insightful information tailored to your needs. Whether you're tracking a developing story, researching a complex topic, or simply staying informed, Oriana is your go-to digital assistant.

    With the tenacity of an elite squad of researchers powered by state-of-the-art AI, Oriana helps you ask the right questions, uncover hidden connections, and generate comprehensive transcripts. It's not just an app – it's your round-the-clock investigative partner, always ready to find, summarize, and organize the information you request.

    Let Oriana be your guide in the fast-paced world of information!
    """)

# Initialize session state
if 'selected_answers' not in st.session_state:
    st.session_state.selected_answers = []

# Function to display transcript counter
def display_transcript_counter():
    st.write(f"Current number of summaries in transcript: {len(st.session_state.selected_answers)}/5")
    st.write("Add up to 5 article summaries to transcript.")

# Section 1: Let Oriana Read and Summarize your Article
st.markdown("## Let Oriana Read and Summarize your Article")
st.markdown("---")  # Visual separator

selected_source = st.selectbox("Select source:", oriana.sources)

keywords = st.text_input("Add keywords or phrases about your article (separate multiple entries with commas):")
if keywords:
    with st.spinner("Investigating..."):
        answer = oriana.answer_question(keywords, selected_source)
    st.subheader("Article Summary")
    st.write(answer)
    
    # Add answer to transcript
    if st.button("Add to Transcript", key="add_summary_to_transcript"):
        if len(st.session_state.selected_answers) < 5:
            st.session_state.selected_answers.append(f"{selected_source}: {answer}")
            st.success("Summary added to transcript.")
            st.rerun()
        else:
            st.warning("You've reached the limit of 5 article summaries in the transcript.")

# Display transcript counter in Section 1
display_transcript_counter()

# Generate Transcript and News Script (as a subcategory)
st.markdown("### Generate Transcript and News Script")
if st.button("Generate Transcript and News Script"):
    if st.session_state.selected_answers:
        with st.spinner("Generating transcript and news script..."):
            transcript = oriana.generate_news_transcript(st.session_state.selected_answers)
        st.subheader("Generated Transcript and News Script:")
        st.text_area("Transcript", transcript, height=300)
        st.download_button(
            label="Download Transcript and News Script",
            data=transcript,
            file_name="oriana_transcript_and_script.txt",
            mime="text/plain"
        )
    else:
        st.warning("Please add some article summaries to the transcript first.")

# Section 2: Summarize your article(s)
st.markdown("## Summarize your article(s)")
st.markdown("---")  # Visual separator

article_urls = st.text_area("Enter Article/Document URL(s) (one per line, up to 5):")

if st.button("Summarize Articles"):
    with st.spinner("Summarizing articles..."):
        try:
            urls = [url.strip() for url in article_urls.split('\n') if url.strip()][:5]  # Limit to 5 URLs
            summarized_articles = []
            for url in urls:
                article = oriana.get_webpage_articles("", url)  # Empty string as we're not searching for a specific subject
                if article:
                    summary = oriana.summarize_articles(article)[0]
                    summarized_articles.append(summary)
            
            if not summarized_articles:
                st.warning("No articles found. Please check your URLs and try again.")
            else:
                st.session_state.summarized_articles = summarized_articles
                st.rerun()
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if 'summarized_articles' in st.session_state:
    st.subheader(f"Summarized Articles")
    for i, article in enumerate(st.session_state.summarized_articles):
        st.write(f"### [{article['title']}]({article['url']})")
        st.write(f"**Published:** {article['published_date']} | **Source:** {article['source']}")
        st.write(f"**Summary:** {article['summary']}")
        if st.button(f"Add to Transcript: {article['title'][:30]}...", key=f"add_to_transcript_{i}"):
            if len(st.session_state.selected_answers) < 5:
                st.session_state.selected_answers.append(f"{article['source']}: {article['summary']}")
                st.success(f"Summary of '{article['title']}' added to transcript.")
                st.rerun()
            else:
                st.warning("You've reached the limit of 5 article summaries in the transcript.")
        st.write("---")

# Display transcript counter in Section 2
display_transcript_counter()

# Section 3: Additional Resources
st.markdown("## Additional Resources")
st.markdown("---")  # Visual separator

st.write("Add useful news sites for quick access to article URLs:")

new_resource = st.text_input("Enter a new resource URL:")
new_resource_name = st.text_input("Enter a name for this resource:")
if st.button("Add Resource"):
    try:
        oriana.add_resource(new_resource_name, new_resource)
        st.success(f"Added resource: {new_resource_name}")
    except Exception as e:
        st.error(f"Error adding resource: {str(e)}")

st.subheader("Current Resources")
resources = oriana.get_resources()
for name, url in resources.items():
    col1, col2, col3 = st.columns([2, 2, 1])
    col1.write(name)
    col2.write(url)
    if col3.button("Remove", key=f"remove_resource_{name}"):
        if st.button(f"Confirm removal of {name}", key=f"confirm_resource_{name}"):
            try:
                oriana.remove_resource(name)
                st.success(f"Removed resource: {name}")
                st.rerun()
            except Exception as e:
                st.error(f"Error removing resource: {str(e)}")

st.write("Use these resources to find article URLs for summarization.")

# import streamlit as st
# from main_functions import Oriana
# import time
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)

# @st.cache_resource(hash_funcs={Oriana: lambda _: None})
# def get_oriana_instance():
#     return Oriana()

# # Use this function to get the Oriana instance
# oriana = get_oriana_instance()

# # Custom title with larger font and smaller tagline
# st.markdown("""
#     <h1 style='font-size: 3em;'>Oriana</h1>
#     <h3 style='font-size: 1.5em; font-weight: normal;'>Your AI-Powered Investigative Journalist</h3>
#     """, unsafe_allow_html=True)

# # Sidebar content
# st.sidebar.header("Add News Source")
# new_source = st.sidebar.text_input("Enter a new source URL:")
# if st.sidebar.button("Add Source"):
#     try:
#         oriana.add_source(new_source)
#         st.sidebar.success(f"Added source: {new_source}")
#         st.rerun()
#     except Exception as e:
#         st.sidebar.error(f"Error adding source: {str(e)}")

# # Display current sources
# st.sidebar.header("Current Sources")
# for source in oriana.sources:
#     col1, col2 = st.sidebar.columns([3, 1])
#     col1.write(source)
#     if col2.button("X", key=f"remove_{source}"):
#         if st.sidebar.button("Done with this?", key=f"confirm_{source}"):
#             try:
#                 updated_sources = oriana.remove_source(source)
#                 st.sidebar.success(f"Removed source: {source}")
#                 st.rerun()
#             except Exception as e:
#                 st.sidebar.error(f"Error removing source: {str(e)}")
#                 logging.error(f"Error removing source {source}: {str(e)}")

# # Debug info
# if st.sidebar.checkbox("Show Debug Info"):
#     st.sidebar.write("Current sources:", oriana.sources)

# # About Oriana in sidebar
# st.sidebar.header("About Oriana")
# with st.sidebar.expander("ℹ️ Learn More"):
#     st.info("""
#     Dive into the world of cutting-edge investigative journalism with Oriana, your tireless AI research companion. This innovative app harnesses the power of advanced artificial intelligence to sift through a vast array of sources, delivering the most relevant and insightful information tailored to your needs. Whether you're tracking a developing story, researching a complex topic, or simply staying informed, Oriana is your go-to digital assistant.

#     With the tenacity of an elite squad of researchers powered by state-of-the-art AI, Oriana helps you ask the right questions, uncover hidden connections, and generate comprehensive transcripts. It's not just an app – it's your round-the-clock investigative partner, always ready to find, summarize, and organize the information you request.

#     Let Oriana be your guide in the fast-paced world of information!
#     """)

# # Initialize session state
# if 'selected_answers' not in st.session_state:
#     st.session_state.selected_answers = []

# # Function to display transcript counter
# def display_transcript_counter():
#     st.write(f"Current number of summaries in transcript: {len(st.session_state.selected_answers)}/5")
#     st.write("Add up to 5 article summaries to transcript.")

# # Section 1: Let Oriana Read and Summarize your Article
# st.markdown("## Let Oriana Read and Summarize your Article")
# st.markdown("---")  # Visual separator

# selected_source = st.selectbox("Select source:", oriana.sources)

# keywords = st.text_input("Add keywords or phrases about your article (separate multiple entries with commas):")
# if keywords:
#     with st.spinner("Investigating..."):
#         answer = oriana.answer_question(keywords, selected_source)
#     st.subheader("Article Summary")
#     st.write(answer)
    
#     # Add answer to transcript
#     if st.button("Add to Transcript", key="add_summary_to_transcript"):
#         if len(st.session_state.selected_answers) < 5:
#             st.session_state.selected_answers.append(f"{selected_source}: {answer}")
#             st.success("Summary added to transcript.")
#             st.rerun()
#         else:
#             st.warning("You've reached the limit of 5 article summaries in the transcript.")

# # Display transcript counter in Section 1
# display_transcript_counter()

# # Generate Transcript and News Script (as a subcategory)
# st.markdown("### Generate Transcript and News Script")
# if st.button("Generate Transcript and News Script"):
#     if st.session_state.selected_answers:
#         with st.spinner("Generating transcript and news script..."):
#             transcript = oriana.generate_news_transcript(st.session_state.selected_answers)
#         st.subheader("Generated Transcript and News Script:")
#         st.text_area("Transcript", transcript, height=300)
#         st.download_button(
#             label="Download Transcript and News Script",
#             data=transcript,
#             file_name="oriana_transcript_and_script.txt",
#             mime="text/plain"
#         )
#     else:
#         st.warning("Please add some article summaries to the transcript first.")

# # Section 2: Summarize your article(s)
# st.markdown("## Summarize your article(s)")
# st.markdown("---")  # Visual separator

# article_urls = st.text_area("Enter Article/Document URL(s) (one per line, up to 5):")

# if st.button("Summarize Articles"):
#     with st.spinner("Summarizing articles..."):
#         try:
#             urls = [url.strip() for url in article_urls.split('\n') if url.strip()][:5]  # Limit to 5 URLs
#             summarized_articles = []
#             for url in urls:
#                 article = oriana.get_webpage_articles("", url)  # Empty string as we're not searching for a specific subject
#                 if article:
#                     summary = oriana.summarize_articles(article)[0]
#                     summarized_articles.append(summary)
            
#             if not summarized_articles:
#                 st.warning("No articles found. Please check your URLs and try again.")
#             else:
#                 st.session_state.summarized_articles = summarized_articles
#                 st.rerun()
#         except Exception as e:
#             st.error(f"An error occurred: {str(e)}")

# if 'summarized_articles' in st.session_state:
#     st.subheader(f"Summarized Articles")
#     for i, article in enumerate(st.session_state.summarized_articles):
#         st.write(f"### [{article['title']}]({article['url']})")
#         st.write(f"**Published:** {article['published_date']} | **Source:** {article['source']}")
#         st.write(f"**Summary:** {article['summary']}")
#         if st.button(f"Add to Transcript: {article['title'][:30]}...", key=f"add_to_transcript_{i}"):
#             if len(st.session_state.selected_answers) < 5:
#                 st.session_state.selected_answers.append(f"{article['source']}: {article['summary']}")
#                 st.success(f"Summary of '{article['title']}' added to transcript.")
#                 st.rerun()
#             else:
#                 st.warning("You've reached the limit of 5 article summaries in the transcript.")
#         st.write("---")

# # Display transcript counter in Section 2
# display_transcript_counter()

# # Section 3: Additional Resources
# st.markdown("## Additional Resources")
# st.markdown("---")  # Visual separator

# st.write("Add useful news sites for quick access to article URLs:")

# new_resource = st.text_input("Enter a new resource URL:")
# new_resource_name = st.text_input("Enter a name for this resource:")
# if st.button("Add Resource"):
#     try:
#         oriana.add_resource(new_resource_name, new_resource)
#         st.success(f"Added resource: {new_resource_name}")
#     except Exception as e:
#         st.error(f"Error adding resource: {str(e)}")

# st.subheader("Current Resources")
# resources = oriana.get_resources()
# for name, url in resources.items():
#     col1, col2, col3 = st.columns([2, 2, 1])
#     col1.write(name)
#     col2.write(url)
#     if col3.button("Remove", key=f"remove_resource_{name}"):
#         if st.button(f"Confirm removal of {name}", key=f"confirm_resource_{name}"):
#             try:
#                 oriana.remove_resource(name)
#                 st.success(f"Removed resource: {name}")
#                 st.rerun()
#             except Exception as e:
#                 st.error(f"Error removing resource: {str(e)}")

# st.write("Use these resources to find article URLs for summarization.")


# import streamlit as st
# from main_functions import Oriana
# import time
# import json
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)

# @st.cache_resource(hash_funcs={Oriana: lambda _: None})
# def get_oriana_instance():
#     return Oriana()

# # Use this function to get the Oriana instance
# oriana = get_oriana_instance()

# # Custom title with larger font and smaller tagline
# # st.markdown("""
# #     <h1 style='font-size: 3em;'>Oriana</h1>
# #     <h3 style='font-size: 1.5em; font-weight: normal;'>Your AI-Powered Investigative Journalist</h3>
# #     """, unsafe_allow_html=True)
# st.markdown("""
#     <h1 style='font-size: 3em;'>Oriana</h1>
#     <h3 style='font-size: 1.5em; font-weight: normal;'>Your AI-Powered Investigative Journalist</h3>
#     """, unsafe_allow_html=True)

# # Sidebar content
# # st.sidebar.header("Add News Source")
# # new_source = st.sidebar.text_input("Enter a new source URL:")
# # if st.sidebar.button("Add Source"):
# #     oriana.add_source(new_source)
# #     st.sidebar.success(f"Added source: {new_source}")
# st.sidebar.header("Add News Source")
# new_source = st.sidebar.text_input("Enter a new source URL:")
# if st.sidebar.button("Add Source"):
#     oriana.add_source(new_source)
#     st.sidebar.success(f"Added source: {new_source}")
#     st.rerun()

# # Display current sources
# # st.sidebar.header("Current Sources")
# # for source in oriana.sources:
# #     st.sidebar.text(source)
# st.sidebar.header("Current Sources")
# for source in oriana.sources:
#     col1, col2 = st.sidebar.columns([3, 1])
#     col1.write(source)
#     if col2.button("X", key=f"remove_{source}"):
#         if st.sidebar.button("Done with this?", key=f"confirm_{source}"):
#             try:
#                 updated_sources = oriana.remove_source(source)
#                 st.sidebar.success(f"Removed source: {source}")
#                 st.session_state.oriana_sources = updated_sources  # Update session state
#                 time.sleep(1)
#                 st.rerun()
#             except Exception as e:
#                 st.sidebar.error(f"Error removing source: {str(e)}")
#                 logging.error(f"Error removing source {source}: {str(e)}")

# # Use session state to display sources
# if 'oriana_sources' not in st.session_state:
#     st.session_state.oriana_sources = oriana.sources

# st.sidebar.write("Current sources:", st.session_state.oriana_sources)
# if st.sidebar.checkbox("Show Debug Info"):
#     st.sidebar.write("Current sources:", oriana.sources)
#     st.sidebar.write("Sources file content:")
#     try:
#         with open('sources.json', 'r') as f:
#             st.sidebar.json(json.load(f))
#     except FileNotFoundError:
#         st.sidebar.write("sources.json file not found.")
#     except json.JSONDecodeError:
#         st.sidebar.write("sources.json is empty or not valid JSON.")


# # About Oriana in sidebar
# st.sidebar.header("About Oriana")
# with st.sidebar.expander("ℹ️ Learn More"):
#     st.info("""
#     Dive into the world of cutting-edge investigative journalism with Oriana, your tireless AI research companion. This innovative app harnesses the power of advanced artificial intelligence to sift through a vast array of sources, delivering the most relevant and insightful information tailored to your needs. Whether you're tracking a developing story, researching a complex topic, or simply staying informed, Oriana is your go-to digital assistant.

#     With the tenacity of an elite squad of researchers powered by state-of-the-art AI, Oriana helps you ask the right questions, uncover hidden connections, and generate comprehensive transcripts. It's not just an app – it's your round-the-clock investigative partner, always ready to find, summarize, and organize the information you request.

#     Let Oriana be your guide in the fast-paced world of information!
#     """)

# # Initialize session state
# if 'selected_answers' not in st.session_state:
#     st.session_state.selected_answers = []

# # Function to display transcript counter
# def display_transcript_counter():
#     st.write(f"Current number of summaries in transcript: {len(st.session_state.selected_answers)}/5")
#     st.write("Add up to 5 article summaries to transcript.")

# # Section 1: Let Oriana Read and Summarize your Article
# st.markdown("## Let Oriana Read and Summarize your Article")
# st.markdown("---")  # Visual separator

# selected_source = st.selectbox("Select source:", oriana.sources)

# keywords = st.text_input("Add keywords or phrases about your article (separate multiple entries with commas):")
# if keywords:
#     with st.spinner("Investigating..."):
#         answer = oriana.answer_question(keywords, selected_source)
#     st.subheader("Article Summary")
#     st.write(answer)
    
#     # Add answer to transcript
#     if st.button("Add to Transcript", key="add_summary_to_transcript"):
#         if len(st.session_state.selected_answers) < 5:
#             st.session_state.selected_answers.append(f"{selected_source}: {answer}")
#             st.success("Summary added to transcript.")
#             st.rerun()
#         else:
#             st.warning("You've reached the limit of 5 article summaries in the transcript.")

# # Display transcript counter in Section 1
# display_transcript_counter()

# # Generate Transcript and News Script (as a subcategory)
# st.markdown("### Generate Transcript and News Script")
# if st.button("Generate Transcript and News Script"):
#     if st.session_state.selected_answers:
#         with st.spinner("Generating transcript and news script..."):
#             transcript = oriana.generate_news_transcript(st.session_state.selected_answers)
#         st.subheader("Generated Transcript and News Script:")
#         st.text_area("Transcript", transcript, height=300)
#         st.download_button(
#             label="Download Transcript and News Script",
#             data=transcript,
#             file_name="oriana_transcript_and_script.txt",
#             mime="text/plain"
#         )
#     else:
#         st.warning("Please add some article summaries to the transcript first.")

# # Section 2: Summarize your article(s)
# st.markdown("## Summarize your article(s)")
# st.markdown("---")  # Visual separator

# #article_urls = st.text_area("Enter news source URLs (one per line, up to 5):")
# article_urls = st.text_area("Enter Article/Document URL(s) (one per line, up to 5):")

# if st.button("Summarize Articles"):
#     with st.spinner("Summarizing articles..."):
#         try:
#             urls = [url.strip() for url in article_urls.split('\n') if url.strip()][:5]  # Limit to 5 URLs
#             summarized_articles = []
#             for url in urls:
#                 article = oriana.get_webpage_articles("", url)  # Empty string as we're not searching for a specific subject
#                 if article:
#                     summary = oriana.summarize_articles(article)[0]
#                     summarized_articles.append(summary)
            
#             if not summarized_articles:
#                 st.warning("No articles found. Please check your URLs and try again.")
#             else:
#                 st.session_state.summarized_articles = summarized_articles
#                 st.rerun()
#         except Exception as e:
#             st.error(f"An error occurred: {str(e)}")

# if 'summarized_articles' in st.session_state:
#     st.subheader(f"Summarized Articles")
#     for i, article in enumerate(st.session_state.summarized_articles):
#         st.write(f"### [{article['title']}]({article['url']})")
#         st.write(f"**Published:** {article['published_date']} | **Source:** {article['source']}")
#         st.write(f"**Summary:** {article['summary']}")
#         if st.button(f"Add to Transcript: {article['title'][:30]}...", key=f"add_to_transcript_{i}"):
#             if len(st.session_state.selected_answers) < 5:
#                 st.session_state.selected_answers.append(f"{article['source']}: {article['summary']}")
#                 st.success(f"Summary of '{article['title']}' added to transcript.")
#                 st.rerun()
#             else:
#                 st.warning("You've reached the limit of 5 article summaries in the transcript.")
#         st.write("---")

# # Display transcript counter in Section 2
# display_transcript_counter()

# # Section 3: Additional Resources
# st.markdown("## Additional Resources")
# st.markdown("---")  # Visual separator

# st.write("Add useful news sites for quick access to article URLs:")

# new_resource = st.text_input("Enter a new resource URL:")
# new_resource_name = st.text_input("Enter a name for this resource:")
# if st.button("Add Resource"):
#     oriana.add_resource(new_resource_name, new_resource)
#     st.success(f"Added resource: {new_resource_name}")

# st.subheader("Current Resources")
# resources = oriana.get_resources()
# for name, url in resources.items():
#     col1, col2, col3 = st.columns([2, 2, 1])
#     col1.write(name)
#     col2.write(url)
#     if col3.button("Remove", key=f"remove_resource_{name}"):
#         if st.button(f"Confirm removal of {name}", key=f"confirm_resource_{name}"):
#             oriana.remove_resource(name)
#             st.success(f"Removed resource: {name}")
#             st.rerun()

# st.write("Use these resources to find article URLs for summarization.")

# import streamlit as st
# from main_functions import Oriana

# # Initialize Oriana
# oriana = Oriana()

# # Custom title with larger font and smaller tagline
# st.markdown("""
#     <h1 style='font-size: 3em;'>Oriana</h1>
#     <h3 style='font-size: 1.5em; font-weight: normal;'>Your AI-Powered Investigative Journalist</h3>
#     """, unsafe_allow_html=True)

# # Sidebar content
# st.sidebar.header("Add News Source")
# new_source = st.sidebar.text_input("Enter a new source URL:")
# if st.sidebar.button("Add Source"):
#     oriana.add_source(new_source)
#     st.sidebar.success(f"Added source: {new_source}")

# # Display current sources
# st.sidebar.header("Current Sources")
# for source in oriana.sources:
#     st.sidebar.text(source)

# # About Oriana in sidebar
# st.sidebar.header("About Oriana")
# with st.sidebar.expander("ℹ️ Learn More"):
#     st.info("""
#     Dive into the world of cutting-edge investigative journalism with Oriana, your tireless AI research companion. This innovative app harnesses the power of advanced artificial intelligence to sift through a vast array of sources, delivering the most relevant and insightful information tailored to your needs. Whether you're tracking a developing story, researching a complex topic, or simply staying informed, Oriana is your go-to digital assistant.

#     With the tenacity of an elite squad of researchers powered by state-of-the-art AI, Oriana helps you ask the right questions, uncover hidden connections, and generate comprehensive transcripts. It's not just an app – it's your round-the-clock investigative partner, always ready to find, summarize, and organize the information you request.

#     Let Oriana be your guide in the fast-paced world of information!
#     """)

# # Initialize session state to store the general transcript and selected answers
# if 'general_transcript' not in st.session_state:
#     st.session_state.general_transcript = ""
# if 'selected_answers' not in st.session_state:
#     st.session_state.selected_answers = []

# # Let Oriana Read and Summarize your Article
# st.header("Let Oriana Read and Summarize your Article")
# selected_source = st.selectbox("Select source:", oriana.sources)

# keywords = st.text_input("Add keywords or phrases about your article (separate multiple entries with commas):")
# if keywords:
#     with st.spinner("Investigating..."):
#         answer = oriana.answer_question(keywords, selected_source)
#     st.subheader("Article Summary")
#     st.write(answer)
    
#     # Add answer to transcript
#     if st.button("Add to Transcript"):
#         if len(st.session_state.selected_answers) < 5:
#             st.session_state.selected_answers.append(f"{selected_source}: {answer}")
#             st.success("Summary added to transcript.")
#         else:
#             st.warning("You've reached the limit of 5 article summaries in the transcript.")
    
#     # Display transcript counter
#     st.write(f"Current number of summaries in transcript: {len(st.session_state.selected_answers)}/5")
#     st.write("Add up to 5 article summaries to transcript.")

# # Generate Transcript and News Script
# st.header("Generate Transcript and News Script")
# if st.button("Generate Transcript and News Script"):
#     if st.session_state.selected_answers:
#         with st.spinner("Generating transcript and news script..."):
#             transcript = oriana.generate_news_transcript(st.session_state.selected_answers)
#         st.subheader("Generated Transcript and News Script:")
#         st.text_area("Transcript", transcript, height=300)
#         st.download_button(
#             label="Download Transcript and News Script",
#             data=transcript,
#             file_name="oriana_transcript_and_script.txt",
#             mime="text/plain"
#         )
#     else:
#         st.warning("Please add some article summaries to the transcript first.")

# st.header("Summarize your article")
# article_urls = st.text_area("Enter news source URLs (one per line, up to 5):")

# if st.button("Summarize Articles"):
#     with st.spinner("Summarizing articles..."):
#         try:
#             urls = [url.strip() for url in article_urls.split('\n') if url.strip()][:5]  # Limit to 5 URLs
#             summarized_articles = []
#             for url in urls:
#                 article = oriana.get_webpage_articles("", url)  # Empty string as we're not searching for a specific subject
#                 if article:
#                     summary = oriana.summarize_articles(article)[0]
#                     summarized_articles.append(summary)
            
#             if not summarized_articles:
#                 st.warning("No articles found. Please check your URLs and try again.")
#             else:
#                 st.subheader(f"Summarized Articles")
#                 for article in summarized_articles:
#                     st.write(f"### [{article['title']}]({article['url']})")
#                     st.write(f"**Published:** {article['published_date']} | **Source:** {article['source']}")
#                     st.write(f"**Summary:** {article['summary']}")
#                     st.write("---")
#         except Exception as e:
#             st.error(f"An error occurred: {str(e)}")

# # Additional Resources
# st.header("Additional Resources")
# st.write("Add useful news sites for quick access to article URLs:")

# new_resource = st.text_input("Enter a new resource URL:")
# new_resource_name = st.text_input("Enter a name for this resource:")
# if st.button("Add Resource"):
#     oriana.add_resource(new_resource_name, new_resource)
#     st.success(f"Added resource: {new_resource_name}")

# st.subheader("Current Resources")
# resources = oriana.get_resources()
# for name, url in resources.items():
#     col1, col2, col3 = st.columns([2, 2, 1])
#     col1.write(name)
#     col2.write(url)
#     if col3.button("Remove", key=f"remove_resource_{name}"):
#         if st.button(f"Confirm removal of {name}", key=f"confirm_resource_{name}"):
#             oriana.remove_resource(name)
#             st.success(f"Removed resource: {name}")
#             st.experimental_rerun()

# st.write("Use these resources to find article URLs for summarization.")
