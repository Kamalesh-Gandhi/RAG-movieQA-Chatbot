# RAG/rag_pipeline.py

import streamlit as st
from langchain_groq import ChatGroq
from pinecone import Pinecone as PineconeClient
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
import time
import os
from dotenv import load_dotenv
import re # For sanitizing HTML

load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="🎬 MovieMax Q&A (Pastel Edition)", # Changed icon to movie relevant
    page_icon="🎬", # Changed icon to fit pastel theme
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HTML Sanitization ---
def sanitize_html(text):
    """Basic sanitization to prevent XSS from user input if directly embedded in HTML."""
    if not isinstance(text, str):
        text = str(text)
    text = text.replace("&", "&").replace("<", "<").replace(">", ">")
    return text

# --- Custom CSS (Pastel Theme) ---
st.markdown("""
<style>
    /* --- General Page & Font --- */
    body {
        font-family: 'Lato', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; /* Lato is a nice soft font */
        background-color: #F8F3EC; /* Soft Cream */
    }

    /* --- Main App Container --- */
    .stApp {
        background-color: #F8F3EC; /* Consistent with body */
    }

    /* --- Sidebar Styling --- */
    [data-testid="stSidebar"] {
        background-color: #E6EAEB; /* Light Blue-Gray */
        border-right: 1px solid #D1D8D8;
        padding: 20px 15px;
    }
    [data-testid="stSidebar"] h1, /* Sidebar main title */
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] .stMarkdown h1 { /* Affects the st.markdown("<h1>...") */
        color: #6C7A89; /* Muted Slate Blue for titles */
        text-align: center;
        font-size: 1.7rem;
        margin-bottom: 0.5rem;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] .stMarkdown { /* General text in sidebar */
        color: #4C596C; /* Darker Slate for readability */
    }
    [data-testid="stSidebar"] .stButton>button {
        border: 1px solid #B0C4DE;
        background-color: #DEEBF2; /* Lighter shade for buttons */
        color: #6C7A89; /* Muted text color for buttons */
        border-radius: 6px;
        width: 100%;
        margin-bottom: 8px;
        transition: background-color 0.2s ease-in-out, color 0.2s ease-in-out;
    }
    [data-testid="stSidebar"] .stButton>button:hover {
        background-color: #C1D5E0;
        color: #4C596C;
    }
    [data-testid="stSidebar"] .stMarkdown hr {
        border-color: #D1D8D8;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    /* --- Main Chat Area --- */
    .main .block-container {
        background-color: #FFFFFF; /* Pure white for main chat area */
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    .main > div.block-container {
        max-width: 100% !important;
    }

    /* --- Chat Message Styling --- */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 20px; /* Increased gap for better visual separation */
        padding-bottom: 80px;
    }
    .message-row {
        display: flex;
        align-items: flex-end;
    }
    .message-bubble {
        padding: 12px 18px; /* Slightly larger padding */
        border-radius: 20px; /* Slightly more rounded */
        max-width: 75%;
        word-wrap: break-word;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.08); /* Slightly more prominent shadow */
        font-size: 0.98rem; /* Slightly larger font */
        line-height: 1.6;
    }
    .message-avatar {
        font-size: 1.8rem; /* Avatar size */
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px; /* Slightly larger avatar */
        height: 40px;
        border-radius: 50%;
        color: #6C7A89; /* Muted avatar icon color */
    }

    /* Assistant (System) Messages - Aligned Left */
    .message-row.assistant {
        justify-content: flex-start;
    }
    .message-row.assistant .message-avatar {
        margin-right: 12px; /* Increased margin */
        background-color: #E0F2F7; /* Soft Cyan/Aqua avatar bg */
    }
    .message-row.assistant .message-bubble {
        background-color: #D4EDF7; /* Soft Cyan/Aqua for assistant */
        color: #3A738F; /* Darker, muted blue text */
        border-bottom-left-radius: 6px;
    }

    /* User Messages - Aligned Right */
    .message-row.user {
        justify-content: flex-end;
    }
    .message-row.user .message-avatar {
        margin-left: 12px; /* Increased margin */
        order: 1;
        background-color: #FFE6E6; /* Soft Rose/Pink avatar bg */
    }
    .message-row.user .message-bubble {
        background-color: #FFDCDC; /* Soft Rose/Pink for user */
        color: #9C5F5F; /* Muted Rose-Red text */
        order: 0;
        border-bottom-right-radius: 6px;
    }

    /* --- Expander (Context) Styling --- */
    .stExpander {
        border: 1px solid #CEDEE0 !important;
        border-radius: 8px !important;
        background-color: #F8FBFB !important; /* Light background for expander */
        margin-top: 10px; /* Add some space above expander */
    }
    .stExpander summary {
        color: #6C7A89 !important; /* Muted text for expander title */
        font-size: 0.9rem !important;
        padding: 10px 15px !important;
    }
    .stExpander summary:hover {
        color: #4C596C !important;
    }
    .stExpander div[data-testid="stExpanderDetails"] {
        background-color: #FFFFFF !important; /* Pure white content bg */
        color: #4C596C !important;
        padding: 12px 18px;
    }
    .stExpander div[data-testid="stExpanderDetails"] code {
        background-color: #EAF2F2 !important;
        color: #6C7A89 !important;
        border-radius: 4px;
        padding: 3px 6px;
        font-size: 0.85rem;
    }
    .stExpander div[data-testid="stExpanderDetails"] hr {
        border-color: #D1D8D8;
    }

    /* --- Main Area Titles --- */
    .main h2 { /* "Chat with MovieMax" title */
        color: #5D768A; /* Muted Steel Blue title */
        text-align: center;
        font-weight: 600;
        font-size: 2.1rem;
        margin-bottom: 1.8rem;
    }
    .main .stMarkdown {
        color: #4C596C; /* Default markdown text in main chat */
    }

    /* --- Chat Input --- */
    div[data-testid="stChatInput"] textarea {
        background-color: #FFFFFF !important;
        color: #4C596C !important;
        border: 1px solid #CEDEE0 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stChatInput"] button { /* Send button */
        background-color: #8FD8D3 !important; /* Pastel Teal send button */
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
    }
    div[data-testid="stChatInput"] button:hover {
        background-color: #7BC5BF !important; /* Darker shade of pastel teal */
    }

    /* Placeholder for 'Thinking...' */
    .thinking-placeholder {
        font-style: italic;
        color: #7D8F9A; /* Muted color */
        padding: 10px 0px;
    }

</style>
""", unsafe_allow_html=True)


# --- LLM & Embeddings (Deferred Loading) ---
@st.cache_resource(show_spinner="🔄 Loading Groq & Embeddings...")
def load_models():
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        st.error("GROQ_API_KEY not found. Please set it in your .env file.")
        st.stop()
    llm = ChatGroq(groq_api_key=groq_api_key, model="gemma2-9b-it", temperature=0)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return llm, embeddings

@st.cache_resource(show_spinner="🔄 Connecting to Pinecone...")
def load_pinecone_retriever(_embeddings):
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    if not pinecone_api_key:
        st.sidebar.error("PINECONE_API_KEY missing.")
        st.error("Pinecone API Key is missing. Check .env.")
        return None
    try:
        pc = PineconeClient(api_key=pinecone_api_key)
        pinecone_index_obj = pc.Index(index_name)
        vectorstore = PineconeVectorStore(index=pinecone_index_obj, embedding=_embeddings, text_key="text")
        retriever = vectorstore.as_retriever(search_kwargs={'k': 3})
        st.sidebar.success(f"Connected to Pinecone: '{index_name}'")
        return retriever
    except Exception as e:
        st.sidebar.error("Pinecone connection error.")
        st.error(f"Error connecting to Pinecone: {e}")
        return None

if "models_loaded" not in st.session_state:
    with st.spinner("🔄 Initializing AI stack..."):
        llm, embeddings = load_models()
        retriever = load_pinecone_retriever(embeddings)
        st.session_state.llm = llm
        st.session_state.embeddings = embeddings
        st.session_state.retriever = retriever
        st.session_state.models_loaded = True
else:
    llm = st.session_state.llm
    embeddings = st.session_state.embeddings
    retriever = st.session_state.retriever

if retriever:
    prompt_template_str = """
    You are MovieMax, a friendly and helpful AI assistant for answering questions about movies using the provided context.
    Your goal is to provide accurate, concise answers in a gentle and pleasant tone.

    STRICTLY use only the information present in the '<context>' tags.
    If the answer is not found within the context, kindly state: "I'm sorry, I couldn't find that specific detail in our movie information right now."
    Do not make up answers, speculate, or provide information outside the given context.
    If the context is empty or irrelevant, state that you cannot answer based on the provided details.

    Format your answers clearly. For lists (like cast or genres), use bullet points.
    When referring to a movie title, you can make it bold if possible (e.g., **The Matrix**).

    <context>
    {context}
    </context>

    Question: {input}
    Answer:
    """
    prompt = ChatPromptTemplate.from_template(prompt_template_str)
    doc_chain = create_stuff_documents_chain(llm, prompt=prompt)
    retriever_chain = create_retrieval_chain(retriever=retriever, combine_docs_chain=doc_chain)
else:
    retriever_chain = None

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h1>🎬 MovieMax Q&A</h1>", unsafe_allow_html=True) # Title uses h1 style from CSS
    st.markdown("---")
    st.markdown(
        "Welcome! Ask me anything about our movie database. "
        "I use a RAG system with Groq and Pinecone to find answers."
    ) # General text uses sidebar text color
    st.markdown("---")

    st.subheader("💡 Example Questions:") # Subheader uses sidebar text color by default from stMarkdown
    example_questions = [
        "What is the plot of The Matrix?",
        "Who directed Inception?",
        "Which actors star in Pulp Fiction?",
        "Tell me about the awards for The Godfather.",
        "List some comedy movies."
    ]
    for i, q in enumerate(example_questions):
        if st.button(q, key=f"example_{i}"): # Buttons use sidebar button style
            st.session_state.user_question_input = q

    st.markdown("---")
    st.caption("Connection Status:") # Caption uses sidebar text color
    # Status is shown by load_pinecone_retriever

# --- Initialize Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hi there! I'm MovieMax. 🎬 How can I help you with movie info today?",
        "avatar": "🤖" # Changed initial message emoji
    }]

# --- Main Chat Interface ---
st.markdown("<h2>Chat with MovieMax 🤖👤</h2>", unsafe_allow_html=True) # Uses .main h2 style

st.markdown("<div class='chat-container' id='chat-container'>", unsafe_allow_html=True)

for message in st.session_state.messages:
    role_class = "user" if message["role"] == "user" else "assistant"
    avatar_html = message.get("avatar_icon", "👤" if message["role"] == "user" else "🤖")

    sanitized_content = sanitize_html(message["content"])

    if message["role"] == "user":
        st.markdown(f"""
            <div class="message-row user">
                <div class="message-bubble user">{sanitized_content}</div>
                <div class="message-avatar">{avatar_html}</div>
            </div>""", unsafe_allow_html=True)
    else: # Assistant
        st.markdown(f"""
            <div class="message-row assistant">
                <div class="message-avatar">{avatar_html}</div>
                <div class="message-bubble assistant">{sanitized_content}</div>
            </div>""", unsafe_allow_html=True)

        if "context" in message and message["context"]:
            with st.expander("🔍 Show Context & Details", expanded=False): # Uses expander styles
                if "response_time" in message:
                    st.caption(f"⏱️ Response time: {message['response_time']} seconds") # Uses default caption style with main text color
                for i, doc in enumerate(message["context"]):
                    st.markdown(f"**Retrieved Document {i+1}:**") # Uses main text color
                    st.code(doc.page_content, language="text") # Uses expander code style
                    if i < len(message["context"]) - 1: st.markdown("---") # Uses expander hr style

thinking_placeholder_container = st.empty()
st.markdown("</div>", unsafe_allow_html=True)


# --- User Input ---
# if 'user_question_input' not in st.session_state:
#     st.session_state.user_question_input = ""

user_question = st.chat_input("Ask your movie question here...", key="user_question_input") # Uses chat_input styles

if user_question:
    sanitized_user_question = sanitize_html(user_question)
    st.session_state.messages.append({"role": "user", "content": sanitized_user_question, "avatar_icon": "👤"})

    if retriever_chain:
        with thinking_placeholder_container:
            st.markdown(f"""
                <div class="message-row assistant">
                    <div class="message-avatar">🤖</div>
                    <div class="message-bubble assistant thinking-placeholder">🎬 Thinking...</div>
                </div>""", unsafe_allow_html=True)

        start_time = time.process_time()
        try:
            response = retriever_chain.invoke({"input": user_question})
            end_time = time.process_time()
            answer = response.get('answer', "Sorry, I couldn't formulate an answer.")
            retrieved_context = response.get('context', [])

            sanitized_answer = sanitize_html(answer)
            st.session_state.messages.append({
                "role": "assistant",
                "content": sanitized_answer,
                "avatar_icon": "🤖",
                "context": retrieved_context,
                "response_time": round(end_time - start_time, 2)
            })

        except Exception as e:
            error_message = f"An error occurred: {e}"
            sanitized_error_message = sanitize_html(error_message)
            st.session_state.messages.append({
                "role": "assistant",
                "content": sanitized_error_message,
                "avatar_icon": "🤖",
                "context": []
            })
        finally:
            thinking_placeholder_container.empty()
            st.rerun()
    else:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "I'm currently unable to connect to the movie database. Please check settings.",
            "avatar_icon": "🤖"
        })
        st.rerun()