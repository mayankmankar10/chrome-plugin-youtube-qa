from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import logging

# Suppress the specific warning from the Google API client
logging.getLogger('google.auth.transport.requests').setLevel(logging.ERROR)


# Load environment variables from .env file
load_dotenv()

from youtube_transcript_api._errors import NoTranscriptFound
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import YoutubeLoader

# Init FastAPI app
app = FastAPI()

# Allow Chrome extension access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to ["chrome-extension://YOUR_ID"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for incoming request
class QARequest(BaseModel):
    url: str
    question: str

# Core LLM model
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

# Prompt
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a helpful assistant. Answer the user's question based on the context from the YouTube video transcript provided below.

Provide a clear and concise answer. If the context doesn't contain the answer, say that you couldn't find the answer in the transcript.

--- BEGIN CONTEXT ---
{context}
--- END CONTEXT ---

Question: {question}
"""
)

# Util
def extract_video_id(url: str):
    """Extract YouTube video ID from a full URL."""
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return None  # Return None if ID can't be extracted

@app.post("/ask")
async def ask_question(payload: QARequest):
    try:
        video_id = extract_video_id(payload.url)
        if not video_id:
            return JSONResponse(content={"error": "Invalid YouTube URL provided."}, status_code=400)

        # 1. Get transcript using LangChain's loader
        loader = YoutubeLoader(video_id=video_id)
        transcript_docs = loader.load()

        if not transcript_docs:
            return JSONResponse(content={"error": "Could not load transcript."}, status_code=404)

        # 2. Split
        splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        chunks = splitter.split_documents(transcript_docs)

        # 3. Embed + store
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = FAISS.from_documents(chunks, embeddings)

        # 4. Retriever
        retriever = vector_store.as_retriever()

        # 5. Create RAG chain
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        # 6. Invoke chain and get response
        final_response = rag_chain.invoke(payload.question)
        return JSONResponse(content={"answer": final_response})

    except NoTranscriptFound:
        return JSONResponse(content={"error": "No English transcript found for this video."}, status_code=404)
    except Exception as e:
        # Log the exception for debugging
        print(f"An unexpected error occurred: {e}")
        return JSONResponse(content={"error": "An internal server error occurred."}, status_code=500)
