from fastapi import FastAPI, HTTPException
from pydantic import BaseModel # For defining request/response data structures
import uvicorn # For running the server
import rag_core # Import the module containing our RAG logic

# --- Data Models for API ---

class ChatQuery(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    error: str | None = None

# --- FastAPI Application ---

app = FastAPI(
    title="NeoBot RAG API",
    description="API endpoint for the NeoBot RAG chatbot.",
    version="0.1.0",
)

# --- API Endpoint ---

@app.post("/chat", response_model=ChatResponse)
async def handle_chat_query(query: ChatQuery):
    """
    Receives a user question, processes it through the RAG chain,
    and returns the answer.
    """
    print(f"API received query: {query.question}")

    try:
        # Call the core RAG logic function from rag_core.py
        rag_result = rag_core.query_rag(query.question)

        if rag_result["error"]:
            # If rag_core reported an error, return it appropriately
            # We might use HTTP 500 for internal server errors
            print(f"RAG core returned an error: {rag_result['error']}")
            # Return a structured error, but avoid HTTP 500 if it's just "not found"
            if "not found" in rag_result["error"].lower() or "not available" in rag_result["error"].lower():
                 # Still return a valid response, but indicate error clearly
                 return ChatResponse(answer="", error=rag_result["error"])
            else:
                # For more severe errors, raise an HTTP exception
                raise HTTPException(status_code=500, detail=f"RAG Processing Error: {rag_result['error']}")

        if rag_result["answer"] is None:
             # Handle cases where answer is None without an explicit error string
             print("RAG core returned None answer without explicit error.")
             raise HTTPException(status_code=500, detail="RAG Processing Error: Failed to generate answer.")

        print(f"RAG core returned answer: {rag_result['answer'][:100]}...") # Log snippet
        # Return the successful response
        return ChatResponse(answer=rag_result["answer"])

    except HTTPException as http_exc:
        # Re-raise HTTPExceptions to let FastAPI handle them
        raise http_exc
    except Exception as e:
        # Catch any unexpected errors during API handling
        print(f"Unexpected API error: {e}")
        # import traceback # Uncomment for detailed debugging
        # traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

@app.get("/", include_in_schema=False)
async def root():
    """Simple root endpoint to check if the server is running."""
    return {"message": "NeoBot RAG API is running. Use the /chat endpoint with POST."}

# --- Preload RAG Chain (Optional but Recommended) ---
# Call get_rag_chain() once when the server starts to load models into memory.
# This avoids the delay on the very first API request.
@app.on_event("startup")
async def startup_event():
    print("Server starting up... Pre-loading RAG chain.")
    rag_chain = rag_core.get_rag_chain()
    if rag_chain is None:
        print("ERROR: RAG chain failed to initialize on startup. Check rag_core logs.")
    else:
        print("RAG chain pre-loaded successfully.")

# --- Main entry point for running the server ---
if __name__ == "__main__":
    print("Starting FastAPI server using uvicorn...")
    # Host '0.0.0.0' makes it accessible on your local network
    # '127.0.0.1' makes it accessible only from your own machine
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    # reload=True automatically restarts the server when you save changes to .py files (good for development)