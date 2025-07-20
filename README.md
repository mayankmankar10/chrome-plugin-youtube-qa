# YouTube Q&A Chrome Extension

A Chrome extension that allows you to ask questions about YouTube videos using AI. The extension extracts video transcripts and uses OpenAI's GPT-4 to provide intelligent answers based on the video content.

## Features

- 🎥 **YouTube Video Analysis**: Extract and analyze transcripts from any YouTube video
- 🤖 **AI-Powered Q&A**: Get intelligent answers using OpenAI's GPT-4 model
- 🔍 **Smart Context Retrieval**: Uses FAISS vector search and contextual compression for relevant answers
- 🌐 **Chrome Extension**: Easy-to-use popup interface for quick questions
- ⚡ **Fast API Backend**: FastAPI server with efficient transcript processing

## How It Works

1. **Transcript Extraction**: Uses the YouTube Transcript API to get video transcripts
2. **Text Processing**: Splits transcripts into chunks for better processing
3. **Vector Search**: Creates embeddings and stores them in a FAISS vector database
4. **Contextual Retrieval**: Uses advanced retrieval techniques to find relevant content
5. **AI Generation**: Leverages GPT-4 to generate accurate, contextual answers

## Project Structure

```
chrome-plugin-youtube-qa/
├── extensions/           # Chrome extension files
│   ├── manifest.json    # Extension configuration
│   ├── popup.html      # Extension popup interface
│   ├── popup.js        # Extension JavaScript logic
│   └── icon.png        # Extension icon
├── main.py             # FastAPI backend server
├── requirements.txt    # Python dependencies
├── style.css          # Additional styles (if needed)
└── venv/              # Python virtual environment
```

## Prerequisites

- Python 3.8 or higher
- Chrome browser
- OpenAI API key

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd chrome-plugin-youtube-qa
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure OpenAI API Key

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

You can get an API key from [OpenAI's platform](https://platform.openai.com/api-keys).

### 4. Start the Backend Server

```bash
python main.py
```

The server will start on `http://localhost:8000`.

### 5. Install Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked" and select the `extensions/` folder
4. The extension icon should appear in your Chrome toolbar

## Usage

### Using the Chrome Extension

1. Navigate to any YouTube video
2. Click the extension icon in your Chrome toolbar
3. Paste the YouTube video URL (or it will use the current page)
4. Type your question about the video content
5. Click "Ask" to get an AI-generated answer

### Example Questions

- "What are the main points discussed in this video?"
- "Can you summarize the key takeaways?"
- "What does the speaker say about [specific topic]?"
- "What are the steps mentioned for [process]?"

## API Endpoints

### POST `/ask`

Ask a question about a YouTube video.

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "question": "What is this video about?"
}
```

**Response:**
```json
{
  "answer": "The video discusses..."
}
```

## Technical Details

### Backend Architecture

- **FastAPI**: Modern, fast web framework for building APIs
- **LangChain**: Framework for developing applications with LLMs
- **FAISS**: Library for efficient similarity search and clustering
- **YouTube Transcript API**: Extracts transcripts from YouTube videos
- **OpenAI GPT-4**: Advanced language model for generating responses

### Key Components

1. **Transcript Processing**: Automatically extracts and processes video transcripts
2. **Vector Embeddings**: Creates semantic embeddings using OpenAI's text-embedding-3-small
3. **Contextual Compression**: Uses LLMChainExtractor for intelligent context selection
4. **Query Rewriting**: Improves question clarity before processing
5. **MMR Retrieval**: Uses Maximum Marginal Relevance for diverse context selection

## Dependencies

- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `langchain`: LLM framework
- `langchain-openai`: OpenAI integration
- `youtube-transcript-api`: YouTube transcript extraction
- `faiss-cpu`: Vector similarity search
- `python-dotenv`: Environment variable management

## Troubleshooting

### Common Issues

1. **"Server not reachable" error**
   - Make sure the backend server is running on `http://localhost:8000`
   - Check that the virtual environment is activated

2. **"No transcript available" error**
   - Some videos may not have available transcripts
   - Try videos with English subtitles or auto-generated captions

3. **API key errors**
   - Verify your OpenAI API key is correctly set in the `.env` file
   - Ensure you have sufficient API credits

4. **Extension not loading**
   - Check that Developer mode is enabled in Chrome extensions
   - Verify the `extensions/` folder path is correct

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the GPT-4 API
- LangChain for the excellent LLM framework
- YouTube Transcript API for transcript extraction
- FAISS for efficient vector search capabilities 