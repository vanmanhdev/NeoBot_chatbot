import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
DATA_SOURCES = ["neobot_info.txt", "general_ai_info.txt", "dialog.txt"]
VECTORSTORE_PATH = "./chroma_db_neobot" # Directory to save the vector store
EMBEDDING_MODEL = "paraphrase-multilingual-mpnet-base-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
# --- ---

def main():
    print(f"Starting indexing process from folder: {os.getcwd()}")
    print(f"Using Vector Store Path: {os.path.abspath(VECTORSTORE_PATH)}")

    all_docs = []
    print("Loading documents from sources:")
    for source_file in DATA_SOURCES:
        source_path = os.path.abspath(source_file)
        print(f"- Checking for: {source_path}")
        if not os.path.exists(source_file):
            print(f"  Warning: Source file not found at '{source_file}'. Skipping.")
            continue

        try:
            # --- Add logic here later for different file types (PDF, DOCX) ---
            if source_file.lower().endswith(".txt"):
                print(f"  Loading text file: {source_file}")
                loader = TextLoader(source_file, encoding='utf-8')
                docs = loader.load()
                all_docs.extend(docs)
                print(f"    Loaded {len(docs)} sections.")
            else:
                print(f"  Warning: Unsupported file type for '{source_file}'. Skipping.")
                continue
        except Exception as load_error:
            print(f"  ERROR loading file {source_file}: {load_error}")
            continue


    if not all_docs:
        print("\nError: No documents were successfully loaded from any source. Exiting.")
        return

    print(f"\nTotal document sections loaded: {len(all_docs)}")

    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = text_splitter.split_documents(all_docs)
    print(f"Split into {len(chunks)} chunks.")

    if not chunks:
        print("No chunks generated. Check document content and splitter settings.")
        return

    print(f"\nInitializing embedding model: {EMBEDDING_MODEL}...")
    try:
        embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)
    except Exception as e:
        print(f"Error initializing embedding model: {e}")
        return

    vectorstore_abs_path = os.path.abspath(VECTORSTORE_PATH)
    print(f"Adding documents to vector store at: {vectorstore_abs_path}...")
    # Use Chroma directly to add documents to an existing store or create if not present
    # This avoids potential issues with `from_documents` overwriting or creating duplicates unnecessarily
    try:
        vectorstore = Chroma(
             persist_directory=VECTORSTORE_PATH,
             embedding_function=embeddings
        )
        print(f"  Existing vector store loaded. Contains approx {vectorstore._collection.count()} embeddings.")
        print(f"  Adding {len(chunks)} new chunks...")
        vectorstore.add_documents(chunks)
        print("  New documents added successfully.")

    except Exception as add_err:
         # This might happen if the DB doesn't exist yet or has issues
         print(f"  Could not load existing store or add docs (Error: {add_err}). Attempting to create from scratch...")
         try:
             vectorstore = Chroma.from_documents(
                 documents=chunks,
                 embedding=embeddings,
                 persist_directory=VECTORSTORE_PATH
             )
             print("  New vector store created successfully from scratch.")
         except Exception as create_err:
              print(f"  ERROR: Failed to create vector store from scratch: {create_err}")
              return



    print("-" * 30)
    print("Indexing Complete!")
    print(f"Vector store updated/created in: {vectorstore_abs_path}")
    print("-" * 30)

if __name__ == "__main__":
    main()