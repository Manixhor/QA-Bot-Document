"""
Document Q&A Bot - Command Line Interface
An interactive CLI for asking questions about your documents.
"""

import os
import sys
from rag_engine import RAGEngine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def print_header():
    """Print the application header."""
    print("\n" + "=" * 60)
    print("📚 Document Q&A Bot")
    print("Powered by RAG (Retrieval-Augmented Generation)")
    print("=" * 60)


def print_menu():
    """Print the main menu."""
    print("\n📋 Commands:")
    print("  1. Ingest documents  - Load and process documents")
    print("  2. Ask a question    - Query your documents")
    print("  3. View sources      - Show retrieved chunks")
    print("  4. Exit              - Quit the application")
    print("-" * 60)


def ingest_documents(engine: RAGEngine):
    """Handle document ingestion."""
    print("\n📥 Ingesting documents...")
    try:
        engine.ingest()
        print("\n✅ Documents ingested successfully!")
    except FileNotFoundError as e:
        print(f"\n❌ Error: {str(e)}")
        print("Please create a 'data' folder and add documents.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def ask_question(engine: RAGEngine):
    """Handle user questions."""
    print("\n💬 Enter your question (or 'back' to return to menu):")
    question = input("> ").strip()
    
    if question.lower() == 'back':
        return
    
    if not question:
        print("Please enter a valid question.")
        return
    
    print("\n🔍 Searching and generating answer...")
    
    try:
        result = engine.generate_answer(question)
        
        print("\n" + "=" * 60)
        print("📝 ANSWER:")
        print("=" * 60)
        print(result["answer"])
        
        print("\n" + "=" * 60)
        print("📚 SOURCES:")
        print("=" * 60)
        
        for i, source in enumerate(result["sources"], 1):
            filename = source["metadata"].get("source", "Unknown")
            page = source["metadata"].get("page", "N/A")
            print(f"\nSource {i}: {os.path.basename(filename)} (Page {page})")
            print("-" * 40)
            content = source["content"][:300] + "..." if len(source["content"]) > 300 else source["content"]
            print(content)
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def view_sources(engine: RAGEngine):
    """View all sources in the vector store."""
    print("\n📚 Available Sources:")
    print("-" * 60)
    
    try:
        if engine.vector_store is None:
            engine.load_vector_store()
        
        # Get all documents
        collection = engine.vector_store._collection
        count = collection.count()
        
        print(f"Total chunks in database: {count}")
        print("\nType a search query to see relevant sources (or 'back' to return):")
        
        while True:
            query = input("\n> ").strip()
            
            if query.lower() == 'back':
                break
            
            if not query:
                continue
            
            results = engine.retrieve(query, k=3)
            
            print(f"\n🔍 Top {len(results)} results for '{query}':")
            print("-" * 40)
            
            for i, doc in enumerate(results, 1):
                filename = doc.metadata.get("source", "Unknown")
                page = doc.metadata.get("page", "N/A")
                print(f"\n{i}. {os.path.basename(filename)} (Page {page})")
                content = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                print(f"   {content}")
            
    except FileNotFoundError:
        print("❌ Vector store not found. Please ingest documents first.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def main():
    """Main application loop."""
    print_header()
    
    # Check for Groq API key
    required_key = "GROQ_API_KEY"
    
    if not os.environ.get(required_key):
        print(f"\n⚠️  Warning: GROQ_API_KEY not set.")
        print("Please set it in a .env file or environment variable.")
        
        api_key = input("\nEnter your Groq API key (or press Enter to continue): ").strip()
        if api_key:
            os.environ[required_key] = api_key
        else:
            print("\nSome features may not work without an API key.")
    
    # Initialize RAG engine
    engine = RAGEngine()
    
    # Check if vector store exists
    if os.path.exists("./vector_store"):
        print("\n✅ Found existing vector store.")
        try:
            engine.load_vector_store()
            print("Loaded successfully!")
        except Exception as e:
            print(f"Could not load: {str(e)}")
    
    # Main loop
    while True:
        print_menu()
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == "1":
            ingest_documents(engine)
            
        elif choice == "2":
            ask_question(engine)
            
        elif choice == "3":
            view_sources(engine)
            
        elif choice == "4":
            print("\n👋 Goodbye! Have a good day!")
            sys.exit(0)
            
        else:
            print("\n⚠️  Invalid option. Please select 1-4.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Have a good day! Thank you")
        sys.exit(0)
