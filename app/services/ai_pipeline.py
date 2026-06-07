from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.core.config import settings

FAISS_INDEX_DIR = "./faiss_index"


def get_llm():
    if settings.USE_OLLAMA:
        return Ollama(
            base_url=settings.OLLAMA_BASE_URL, model="llama3"
        )
    return ChatOpenAI(
        api_key=settings.OPENAI_API_KEY, model="gpt-4-turbo"
    )


def get_embeddings():
    if settings.USE_OLLAMA:
        return OllamaEmbeddings(base_url=settings.OLLAMA_BASE_URL, model="llama3")
    return OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY, model="text-embedding-3-small")


def get_vector_store():
    import os
    if os.path.exists(FAISS_INDEX_DIR) and os.path.exists(os.path.join(FAISS_INDEX_DIR, "index.faiss")):
        return FAISS.load_local(FAISS_INDEX_DIR, get_embeddings(), allow_dangerous_deserialization=True)
    return None


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
    if vector_store:
        vector_store.add_documents(splits)
    else:
        vector_store = FAISS.from_documents(splits, get_embeddings())
    vector_store.save_local(FAISS_INDEX_DIR)
    
    return len(splits)


def generate_quiz_from_note(note_id: int, difficulty: str):
    """Generate a quiz from a note's embedded content."""
    import json
    vector_store = get_vector_store()
    if not vector_store:
        return []
        
    # Get documents for this note
    docs = []
    for doc_id, doc in vector_store.docstore._dict.items():
        if doc.metadata.get('note_id') == note_id:
            docs.append(doc)
            
    if not docs:
        return []
        
    # Combine some text (limit to avoid token overflow)
    context = "\n\n".join([doc.page_content for doc in docs[:10]])
    
    prompt = f"""You are an expert educator. Generate a multiple choice quiz based on the provided text.
Difficulty level: {difficulty}.
Return EXACTLY a JSON array of 5 question objects.
Each object must have:
- "question_type": "MCQ"
- "content": the question text
- "options": an object with keys "A", "B", "C", "D" and their string values
- "correct_answer": the correct key ("A", "B", "C", or "D")
- "explanation": explanation for the correct answer

Text:
{context}

Output ONLY valid JSON."""

    llm = get_llm()
    try:
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, 'content') else response
        content = content.replace("```json", "").replace("```", "").strip()
        quiz_data = json.loads(content)
        return quiz_data
    except Exception as e:
        print(f"Error generating quiz: {e}")
        return []


def ask_ai_tutor(user_id: int, query: str):
    """Answer a student's question using RAG over their notes."""
    from langchain.chains import create_retrieval_chain
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain_core.prompts import ChatPromptTemplate
    
    vector_store = get_vector_store()
    if not vector_store:
        return {
            "status": "error",
            "answer": "No notes found in your study material."
        }
        
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    prompt = ChatPromptTemplate.from_template(
        "You are an AI Tutor for AdaptQuiz. Answer the student's question clearly and concisely based ONLY on the provided context. If you don't know the answer, say that you don't know based on the provided material.\n\nContext: {context}\n\nQuestion: {input}\n\nAnswer:"
    )
    
    document_chain = create_stuff_documents_chain(get_llm(), prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    try:
        response = retrieval_chain.invoke({"input": query})
        return {
            "status": "success",
            "answer": response["answer"]
        }
    except Exception as e:
        return {
            "status": "error",
            "answer": f"Error generating answer: {str(e)}"
        }
