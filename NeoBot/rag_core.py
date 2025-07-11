import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_core.runnables import RunnableParallel


USE_OLLAMA = True
from langchain_community.llms import Ollama

load_dotenv()


VECTORSTORE_PATH = "./chroma_db_neobot" # Relative path inside NeoBot
EMBEDDING_MODEL = "paraphrase-multilingual-mpnet-base-v2"
# --- LLM Configuration ---
OLLAMA_MODEL = "mistral"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash-latest"

# --- Prompt Configuration (Keep language variable) ---
PROMPT_TEMPLATE = """You are NeoBot, a helpful AI assistant.
Your task is to answer the user's question based *only* on the following context provided.
Be polite and directly answer the question.
If the context doesn't contain the answer, state that you don't have that information in your knowledge base.
**Important:** Respond in the same language as the user's question (English or Vietnamese).

Context:
{context}

Question: {question}

Helpful Answer ({language}):
"""
# --- ---

_components = {} # Simple cache for loaded components

def _load_llm():
    # ... (Keep _load_llm function exactly the same as before) ...
    """Loads the configured Large Language Model."""
    llm = None
    if USE_OLLAMA:
        print(f"Attempting to load Ollama model: {OLLAMA_MODEL}")
        try:
            llm = Ollama(model=OLLAMA_MODEL)
            llm.invoke("Connectivity test.") # Check if Ollama is reachable
            print("Ollama loaded successfully.")
        except Exception as e:
            print(f"ERROR: Failed to load or connect to Ollama. Is it running? Model: {OLLAMA_MODEL}. Error: {e}")
            return None
    else:
        # Using Google Gemini
        print(f"Attempting to load Google Gemini model: {GEMINI_MODEL}")
        if not GOOGLE_API_KEY:
            print("ERROR: GOOGLE_API_KEY not found. Create a .env file with GOOGLE_API_KEY=YOUR_KEY")
            return None
        try:
            # Ensure correct import if USE_OLLAMA is False
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, google_api_key=GOOGLE_API_KEY,
                                         temperature=0.3, convert_system_message_to_human=True)
            print("Google Gemini loaded successfully.")
        except NameError:
             print("ERROR: langchain_google_genai not imported correctly. Check USE_OLLAMA setting.")
             return None
        except Exception as e:
            print(f"ERROR: Failed to load Google Gemini model: {e}")
            return None
    return llm


# --- NEW Function to format retrieved documents ---
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)



def _initialize_rag_chain():
    print("Initializing RAG components (LCEL Revised)...")
    vectorstore_abs_path = os.path.abspath(VECTORSTORE_PATH)
    if not os.path.exists(VECTORSTORE_PATH):
        print(f"ERROR: Vector store not found at '{vectorstore_abs_path}'. Run index_data.py first.")
        return None

    try:
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)
    except Exception as e:
        print(f"Error loading embedding model: {e}")
        return None

    try:
        print(f"Loading vector store from: {vectorstore_abs_path}")
        vectorstore = Chroma(persist_directory=VECTORSTORE_PATH, embedding_function=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        print("Vector store loaded.")
    except Exception as e:
        print(f"Error loading vector store: {e}")
        return None

    llm = _load_llm()
    if llm is None: return None

    prompt = PromptTemplate(template=PROMPT_TEMPLATE, input_variables=["context", "question", "language"])

    setup_and_retrieval = RunnableParallel(
        context=lambda inputs: (retriever | format_docs).invoke(inputs["question"]),
        question=lambda inputs: inputs["question"],
        language=lambda inputs: inputs["language"]
    )

    core_rag_logic = (
        prompt
        | llm
        | StrOutputParser()
    )

    rag_chain = setup_and_retrieval | core_rag_logic

    print("LCEL RAG chain created successfully (Revised Structure).")
    return rag_chain

# --- Keep the rest of the rag_core.py file (including the other functions like
# format_docs, _load_llm, get_rag_chain, query_rag, and the __main__ block)
# exactly the same as in the previous LCEL version. ---


def get_rag_chain():
    """Gets the initialized RAG chain, loading if necessary."""
    if "rag_chain" not in _components or _components["rag_chain"] is None:
         print("No cached RAG chain found, initializing...")
         _components["rag_chain"] = _initialize_rag_chain()
    return _components["rag_chain"]

def query_rag(question: str) -> dict:
    print(f"\nProcessing query: '{question}'")
    rag_chain = get_rag_chain()
    if rag_chain is None:
        return {"answer": None, "source_documents": [], "error": "RAG chain is not available."}

    try:
        language = "Vietnamese" if any(c in 'áàảãạăắằẳẵặâấầẩẫậđéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ' for c in question.lower()) else "English"
        print(f"Detected language (heuristic): {language}")

        inputs_for_chain = {"question": question, "language": language}

        print("Invoking LCEL RAG chain...")
        answer = rag_chain.invoke(inputs_for_chain)
        print("LCEL RAG chain invocation complete.")

        error_msg = None
        if not answer:
            print("Warning: LLM returned an empty answer.")
            error_msg = "LLM returned an empty answer."
        return {"answer": answer.strip(), "source_documents": [], "error": error_msg}

    except Exception as e:
        print(f"Error during LCEL RAG query processing: {e}")
        # import traceback
        # traceback.print_exc()
        _components["rag_chain"] = None # Invalidate cache
        return {"answer": None, "source_documents": [], "error": f"An processing error occurred: {e}"}

# --- Direct Execution Example (for testing this script) ---
if __name__ == "__main__":
    print("\n--- Testing rag_core.py with LCEL directly ---")

    # Ensure Ollama is running OR you have GOOGLE_API_KEY set in a .env file

    test_questions = [
        "Who are you?",
        "Bạn là ai?"
    ]

    # Initialize once before testing
    print("Pre-initializing LCEL RAG chain for testing...")
    get_rag_chain()
    print("-" * 30)

    for q in test_questions:
        response = query_rag(q)
        print("=" * 20)
        print(f"Question: {q}")
        if response["error"]:
            print(f"Error: {response['error']}")
        else:
            print(f"Answer: {response['answer']}")
            # Note: Source documents are not retrieved in this simplified LCEL example
        print("=" * 20)