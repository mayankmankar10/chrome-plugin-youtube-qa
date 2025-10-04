from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from youtube_transcript_api import YouTubeTranscriptApi
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers import ContextualCompressionRetriever
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.retrievers.document_compressors import LLMChainExtractor

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
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)

# Prompt
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a helpful assistant summarizing and explaining content from a YouTube video transcript.
Answer the user's question based on the context provided below.

Respond clearly and concisely in your own words generalise the answer more in your own words along with the transcripts. Do not repeat the transcript verbatim unless necessary.
Use examples or paraphrasing to explain complex ideas. Stay grounded in the video content.

--- BEGIN TRANSCRIPT CONTEXT ---
{context}
--- END TRANSCRIPT CONTEXT ---

Question: {question}
"""
)

# Rewrite Chain
rewrite_prompt = PromptTemplate.from_template(
    "Rewrite the following query to be more specific and clearer:\n{query}"
)
rewrite_chain = rewrite_prompt | llm | StrOutputParser()

# Util
def extract_video_id(url: str):
    """Extract YouTube video ID from a full URL."""
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return url  # fallback (assumes raw video ID)

@app.post("/ask")
async def ask_question(payload: QARequest):
    try:
        # 1. Get transcript
        video_id = extract_video_id(payload.url)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
        transcript = " ".join(chunk["text"] for chunk in transcript_list)

        # 2. Split
        splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=500)
        chunks = splitter.create_documents([transcript])

        # 3. Embed + store
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = FAISS.from_documents(chunks, embeddings)

        # 4. Retrieval with compression
        base_retriever = vector_store.as_retriever(
            search_type="mmr", search_kwargs={"k": 8, "fetch_k": 20}
        )
        compressor = LLMChainExtractor.from_llm(llm)
        retriever = ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=base_retriever
        )

        # 5. Rewrite query
        rewritten = rewrite_chain.invoke({"query": payload.question})

        # 6. Retrieve docs
        docs = retriever.invoke(rewritten)
        context = "\n\n".join(doc.page_content for doc in docs)

        # 7. Final prompt & response
        filled_prompt = prompt.format(context=context, question=rewritten)
        
        final_response = llm.invoke(filled_prompt)
        return JSONResponse(content={"answer": final_response.content})
  
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
