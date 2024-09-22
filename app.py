import streamlit as st
from main_functions import Oriana

# Initialize Oriana
oriana = Oriana()

# Custom title with larger font and smaller tagline
st.markdown("""
    <h1 style='font-size: 3em;'>Oriana</h1>
    <h3 style='font-size: 1.5em; font-weight: normal;'>Your AI-Powered Investigative Journalist</h3>
    """, unsafe_allow_html=True)

# Sidebar content
st.sidebar.header("Add News Source")
new_source = st.sidebar.text_input("Enter a new source URL:")
if st.sidebar.button("Add Source"):
    oriana.add_source(new_source)
    st.sidebar.success(f"Added source: {new_source}")

# Display current sources
st.sidebar.header("Current Sources")
for source in oriana.sources:
    st.sidebar.text(source)

# About Oriana in sidebar
st.sidebar.header("About Oriana")
with st.sidebar.expander("ℹ️ Learn More"):
    st.info("""
    Dive into the world of cutting-edge investigative journalism with Oriana, your tireless AI research companion. This innovative app harnesses the power of advanced artificial intelligence to sift through a vast array of sources, delivering the most relevant and insightful information tailored to your needs. Whether you're tracking a developing story, researching a complex topic, or simply staying informed, Oriana is your go-to digital assistant.

    With the tenacity of an elite squad of researchers powered by state-of-the-art AI, Oriana helps you ask the right questions, uncover hidden connections, and generate comprehensive transcripts. It's not just an app – it's your round-the-clock investigative partner, always ready to find, summarize, and organize the information you request.

    Let Oriana be your guide in the fast-paced world of information!
    """)

# Initialize session state to store the general transcript and selected answers
if 'general_transcript' not in st.session_state:
    st.session_state.general_transcript = ""
if 'selected_answers' not in st.session_state:
    st.session_state.selected_answers = []

# Let Oriana Read and Summarize your Article
st.header("Let Oriana Read and Summarize your Article")
selected_source = st.selectbox("Select source:", oriana.sources)

keywords = st.text_input("Add keywords or phrases about your article (separate multiple entries with commas):")
if keywords:
    with st.spinner("Investigating..."):
        answer = oriana.answer_question(keywords, selected_source)
    st.subheader("Article Summary")
    st.write(answer)
    
    # Add answer to transcript
    if st.button("Add to Transcript"):
        if len(st.session_state.selected_answers) < 5:
            st.session_state.selected_answers.append(f"{selected_source}: {answer}")
            st.success("Summary added to transcript.")
        else:
            st.warning("You've reached the limit of 5 article summaries in the transcript.")
    
    # Display transcript counter
    st.write(f"Current number of summaries in transcript: {len(st.session_state.selected_answers)}/5")
    st.write("Add up to 5 article summaries to transcript.")

# Generate Transcript and News Script
st.header("Generate Transcript and News Script")
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

st.header("Summarize your article")
article_urls = st.text_area("Enter news source URLs (one per line, up to 5):")

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
                st.subheader(f"Summarized Articles")
                for article in summarized_articles:
                    st.write(f"### [{article['title']}]({article['url']})")
                    st.write(f"**Published:** {article['published_date']} | **Source:** {article['source']}")
                    st.write(f"**Summary:** {article['summary']}")
                    st.write("---")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Additional Resources
st.header("Additional Resources")
st.write("Add useful news sites for quick access to article URLs:")

new_resource = st.text_input("Enter a new resource URL:")
new_resource_name = st.text_input("Enter a name for this resource:")
if st.button("Add Resource"):
    oriana.add_resource(new_resource_name, new_resource)
    st.success(f"Added resource: {new_resource_name}")

st.subheader("Current Resources")
resources = oriana.get_resources()
for name, url in resources.items():
    col1, col2, col3 = st.columns([2, 2, 1])
    col1.write(name)
    col2.write(url)
    if col3.button("Remove", key=f"remove_resource_{name}"):
        if st.button(f"Confirm removal of {name}", key=f"confirm_resource_{name}"):
            oriana.remove_resource(name)
            st.success(f"Removed resource: {name}")
            st.experimental_rerun()

st.write("Use these resources to find article URLs for summarization.")

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

# keywords = st.text_input("Add keywords about your article:")
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
# max_articles = st.slider("Maximum number of articles to summarize", min_value=1, max_value=5, value=5)

# if st.button("Summarize Articles"):
#     with st.spinner("Summarizing articles..."):
#         try:
#             urls = [url.strip() for url in article_urls.split('\n') if url.strip()][:max_articles]
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
# st.sidebar.header("Manage News Sources")
# new_source = st.sidebar.text_input("Enter a new source URL:")
# if st.sidebar.button("Add Source"):
#     oriana.add_source(new_source)
#     st.sidebar.success(f"Added source: {new_source}")

# # Display current sources with remove option
# st.sidebar.header("Current Sources")
# for source in oriana.sources:
#     col1, col2 = st.sidebar.columns([3, 1])
#     col1.text(source)
#     if col2.button("Remove", key=f"remove_{source}"):
#         confirm = st.sidebar.button(f"Confirm removal of {source}")
#         if confirm:
#             oriana.remove_source(source)
#             st.sidebar.success(f"Removed source: {source}")
#             st.experimental_rerun()

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

# keywords = st.text_input("Add keywords about your article:")
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
# max_articles = st.slider("Maximum number of articles to summarize", min_value=1, max_value=5, value=5)

# if st.button("Summarize Articles"):
#     with st.spinner("Summarizing articles..."):
#         try:
#             urls = [url.strip() for url in article_urls.split('\n') if url.strip()][:max_articles]
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
#         confirm = st.button(f"Confirm removal of {name}")
#         if confirm:
#             oriana.remove_resource(name)
#             st.success(f"Removed resource: {name}")
#             st.experimental_rerun()

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

# keywords = st.text_input("Add keywords about your article:")
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
# max_articles = st.slider("Maximum number of articles to summarize", min_value=1, max_value=5, value=5)

# if st.button("Summarize Articles"):
#     with st.spinner("Summarizing articles..."):
#         try:
#             urls = [url.strip() for url in article_urls.split('\n') if url.strip()][:max_articles]
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
# st.write("Here are some helpful links for more information:")
# st.write("- [News Source](https://www.c-span.org/)")
# st.write("- [Relevant News Coverage](https://www.latinorebels.com/)")
# st.write("- [News Analysis Guide](https://www.jeffsachs.org/)")

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

# # Interactive Q&A
# st.header("Ask Questions About the News")
# selected_source = st.selectbox("Select source:", oriana.sources)

# user_question = st.text_input("Ask any question about recent news:")
# if user_question and user_question.lower() != 'exit':
#     with st.spinner("Investigating..."):
#         answer = oriana.answer_question(user_question, selected_source)
#     st.subheader("Expert Answer")
#     st.write(answer)
    
#     # Add answer to transcript
#     if st.button("Add to Transcript"):
#         st.session_state.selected_answers.append(answer)
#         st.success("Answer added to transcript.")
    
#     st.write("Feel free to ask more questions in the existing question box.")
# elif user_question.lower() == 'exit':
#     st.write("Thank you for using Oriana!")

# # Generate Transcript
# st.header("Generate Transcript")
# if st.button("Generate Transcript"):
#     if st.session_state.selected_answers:
#         with st.spinner("Generating transcript..."):
#             transcript = oriana.generate_news_transcript(st.session_state.selected_answers)
#         st.subheader("Generated Transcript:")
#         st.text_area("Transcript", transcript, height=300)
#         st.download_button(
#             label="Download Transcript",
#             data=transcript,
#             file_name="oriana_transcript.txt",
#             mime="text/plain"
#         )
#     else:
#         st.warning("Please add some answers to the transcript first.")

# st.header("Search Recent Articles")
# search_subject = st.text_input("Enter a subject to search for recent articles:")
# search_source = st.text_input("Enter news source URL (RSS feed or website):")
# max_articles = st.slider("Maximum number of articles to summarize", min_value=1, max_value=10, value=5)

# if st.button("Search and Summarize Recent Articles"):
#     with st.spinner("Searching for and summarizing recent articles..."):
#         try:
#             recent_articles = oriana.get_recent_articles(search_subject, search_source)
            
#             if not recent_articles:
#                 st.warning("No articles found. Try different search terms or sources.")
#             else:
#                 summarized_articles = oriana.summarize_articles(recent_articles, max_articles)
                
#                 st.subheader(f"Recent Articles about '{search_subject}' (Summarized)")
#                 for article in summarized_articles:
#                     st.write(f"### [{article['title']}]({article['url']})")
#                     st.write(f"**Published:** {article['published_date']} | **Source:** {article['source']}")
#                     st.write(f"**Summary:** {article['summary']}")
#                     st.write("---")
#         except Exception as e:
#             st.error(f"An error occurred: {str(e)}")

# # Search Top Stories
# st.header("Search Top Stories")
# search_source_top = st.selectbox("Select news source for top stories:", oriana.sources)
# if st.button("Search Top Stories"):
#     with st.spinner("Searching for top stories..."):
#         top_stories = oriana.get_top_stories_from_source(search_source_top)
#     st.subheader("Top Stories")
#     for story in top_stories:
#         st.write(f"- [{story['title']}]({story['url']}) (Published: {story['published_date']}) (Source: {story['source']})")

# # Additional Resources
# st.header("Additional Resources")
# st.write("Here are some helpful links for more information:")
# st.write("- [News Source](https://www.c-span.org/)")
# st.write("- [Relevant News Coverage](https://www.latinorebels.com/)")
# st.write("- [News Analysis Guide](https://www.jeffsachs.org/)")

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

# # Interactive Q&A
# st.header("Ask Questions About the News")
# selected_source = st.selectbox("Select source:", oriana.sources)

# user_question = st.text_input("Ask any question about recent news:")
# if user_question and user_question.lower() != 'exit':
#     with st.spinner("Investigating..."):
#         answer = oriana.answer_question(user_question, selected_source)
#     st.subheader("Expert Answer")
#     st.write(answer)
    
#     # Add answer to transcript
#     if st.button("Add to Transcript"):
#         st.session_state.selected_answers.append(answer)
#         st.success("Answer added to transcript.")
    
#     st.write("Feel free to ask more questions in the existing question box.")
# elif user_question.lower() == 'exit':
#     st.write("Thank you for using Oriana!")

# # Generate Transcript
# st.header("Generate Transcript")
# if st.button("Generate Transcript"):
#     if st.session_state.selected_answers:
#         with st.spinner("Generating transcript..."):
#             transcript = oriana.generate_news_transcript(st.session_state.selected_answers)
#         st.subheader("Generated Transcript:")
#         st.text_area("Transcript", transcript, height=300)
#         st.download_button(
#             label="Download Transcript",
#             data=transcript,
#             file_name="oriana_transcript.txt",
#             mime="text/plain"
#         )
#     else:
#         st.warning("Please add some answers to the transcript first.")
# st.header("Search Recent Articles")
# search_subject = st.text_input("Enter a subject to search for recent articles:")
# search_source_type = st.radio("Select source type:", ["RSS Feed", "Website"])

# if search_source_type == "RSS Feed":
#     search_source = st.text_input("Enter RSS feed URL (must end with .xml):")
# else:
#     search_source = st.selectbox("Select news source for recent articles:", oriana.sources)

# max_articles = st.slider("Maximum number of articles to summarize", min_value=1, max_value=10, value=5)

# if st.button("Search and Summarize Recent Articles"):
#     with st.spinner("Searching for and summarizing recent articles..."):
#         try:
#             recent_articles = oriana.get_recent_articles(search_subject, search_source)
            
#             if not recent_articles:
#                 st.warning("No articles found. Try different search terms or sources.")
#             else:
#                 summarized_articles = oriana.summarize_articles(recent_articles, max_articles)
                
#                 st.subheader(f"Recent Articles about '{search_subject}' (Summarized)")
#                 for article in summarized_articles:
#                     st.write(f"### [{article['title']}]({article['url']})")
#                     st.write(f"**Published:** {article['published_date']} | **Source:** {article['source']}")
#                     st.write(f"**Summary:** {article['summary']}")
#                     st.write("---")
#         except Exception as e:
#             st.error(f"An error occurred: {str(e)}")
# # st.header("Search Recent Articles")
# # search_subject = st.text_input("Enter a subject to search for recent articles:")
# # search_source = st.selectbox("Select news source for recent articles:", oriana.sources)
# # max_articles = st.slider("Maximum number of articles to summarize", min_value=1, max_value=10, value=5)

# # if st.button("Search and Summarize Recent Articles"):
# #     with st.spinner("Searching for and summarizing recent articles..."):
# #         try:
# #             recent_articles = oriana.get_recent_articles(search_subject, search_source)
            
# #             if not recent_articles:
# #                 st.warning("No articles found. Try different search terms or sources.")
# #             else:
# #                 summarized_articles = oriana.summarize_articles(recent_articles, max_articles)
                
# #                 st.subheader(f"Recent Articles about '{search_subject}' (Summarized)")
# #                 for article in summarized_articles:
# #                     st.write(f"### [{article['title']}]({article['url']})")
# #                     st.write(f"**Published:** {article['published_date']} | **Source:** {article['source']}")
# #                     st.write(f"**Summary:** {article['summary']}")
# #                     st.write("---")
# #         except Exception as e:
# #             st.error(f"An error occurred: {str(e)}")

# # Search Top Stories
# st.header("Search Top Stories")
# search_source_top = st.selectbox("Select news source for top stories:", oriana.sources)
# if st.button("Search Top Stories"):
#     with st.spinner("Searching for top stories..."):
#         top_stories = oriana.get_top_stories_from_source(search_source_top)
#     st.subheader("Top Stories")
#     for story in top_stories:
#         st.write(f"- [{story['title']}]({story['url']}) (Published: {story['published_date']}) (Source: {story['source']})")

# # Additional Resources
# st.header("Additional Resources")
# st.write("Here are some helpful links for more information:")
# st.write("- [News Source](https://www.c-span.org/)")
# st.write("- [Relevant News Coverage](https://www.latinorebels.com/)")
# st.write("- [News Analysis Guide](https://www.jeffsachs.org/)")
