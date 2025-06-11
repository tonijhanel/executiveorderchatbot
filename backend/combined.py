from dotenv import load_dotenv
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
import re
from typing import List, Dict, Any, Optional
load_dotenv()

from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
from backend.core import create_metadata_filters


PROJECT_2025_INDEX_NAME = "project2025"
EXECUTIVE_ORDERS_INDEX_NAME = "executiveorderscleantxt"
TOP_K_RESULTS = 5 # You can adjust this number


embeddings_proj25 = OpenAIEmbeddings(model="text-embedding-3-small")
docsearch_proj25 = PineconeVectorStore(index_name=PROJECT_2025_INDEX_NAME, embedding=embeddings_proj25)

embeddings_eo = OpenAIEmbeddings(model="text-embedding-3-large")
docsearch_eo = PineconeVectorStore(index_name=EXECUTIVE_ORDERS_INDEX_NAME, embedding=embeddings_eo)

if __name__ == "__main__":
    query_str = "Can you find any proposals within Project 2025 that Trump could affect the balance of power between the federal government and states?"
    res = create_metadata_filters(query=query_str)
    print(res)

    print(f"Connected to Pinecone vector stores: {PROJECT_2025_INDEX_NAME} and {EXECUTIVE_ORDERS_INDEX_NAME}")

    # --- Query Project 2025 Database ---
    project_2025_retriever = docsearch_proj25.as_retriever(
        search_kwargs={"k": TOP_K_RESULTS}
    )
    project_2025_docs: list[Document] = project_2025_retriever.invoke(query_str)

    print(f"Retrieved {len(project_2025_docs)} documents from Project 2025.")

    project_2025_contexts = []
    for doc in project_2025_docs:
        section = doc.metadata.get('section', 'Unknown Section')  # If you added section metadata
        project_2025_contexts.append(f"Source: Project 2025, Section: {section}\nContent: {doc.page_content}")

    print(project_2025_contexts)