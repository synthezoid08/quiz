from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI

from app.core.config import settings

CHROMA_PERSIST_DIR = "./chroma_db"


def get_llm():
    if settings.USE_OLLAMA:
        return Ollama(
            base_url=settings.OLLAMA_BASE_URL, model="llama3"
        )
    return ChatOpenAI(
        api_key=settings.OPENAI_API_KEY, model="gpt-4-turbo"
    )


def get_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def get_vector_store():
    return Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=get_embeddings()
    )


def process_document(file_path: str, note_id: int, user_id: int):
    """Ingest a document: load, chunk, embed, and store."""
    # 1. Ingestion
    if file_path.endswith('.pdf'):
        loader = PyMuPDFLoader(file_path)
    else:
        loader = TextLoader(file_path)

    docs = loader.load()

    # 2. Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200
    )
    splits = text_splitter.split_documents(docs)

    # Add metadata
    for split in splits:
        split.metadata['note_id'] = note_id
        split.metadata['user_id'] = user_id

    # 3. Embedding and Storage
    vector_store = get_vector_store()
    vector_store.add_documents(splits)
    return len(splits)


def generate_quiz_from_note(note_id: int, difficulty: str):
    """Generate a quiz from a note's embedded content."""
    # TODO: Connect with LangChain prompts to generate JSON quiz output
    return {
        "status": "success",
        "message": "Quiz generation scaffolding completed."
    }


def ask_ai_tutor(user_id: int, query: str):
    """Answer a student's question using RAG over their notes."""
    # TODO: Connect with LangChain QA chain
    return {
        "status": "success",
        "answer": "This is a scaffolded AI Tutor response."
    }
