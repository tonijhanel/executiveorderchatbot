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

# Constants
INDEX_NAME = "executiveorderscleantxt"



def extract_executive_order_number(query: str) -> Optional[int]:
    """Extract executive order number from query if present."""
    match = re.search(r"executive order\s+(\d+)", query.lower())
    return int(match.group(1)) if match else None

def get_president_filter(query: str) -> Optional[Dict[str, Any]]:
    """Get president filter based on query."""
    query_lower = query.lower()
    if "biden" in query_lower:
        return {"president": {"$eq": "Biden"}}
    elif "trump" in query_lower:
        return {"president": {"$eq": "Trump"}}
    return None

def get_category_filters(query: str) -> Dict[str, Any]:
    """Get category filters based on query."""
    filters = {}
    query_lower = query.lower()
    
    if "immigration" in query_lower:
        filters["Immigration & Border Control"] = {"$eq": 1}
    
    if "constitution" in query_lower:
        filters["constitutional_impact"] = {"$eq": "Y"}
    
    return filters

def create_metadata_filters(query: str) -> Dict[str, Any]:
    """Create metadata filters based on query content."""
    filters = {}
    
    # Check for executive order number
    eo_number = extract_executive_order_number(query)
    if eo_number:
        filters["executive_order_number"] = {"$eq": eo_number}
    
    # Check for president
    president_filter = get_president_filter(query)
    if president_filter:
        filters.update(president_filter)
    
    # Check for categories
    category_filters = get_category_filters(query)
    if category_filters:
        filters.update(category_filters)
    
    return filters

def run_llm(query: str, chat_history: List[Dict[str, Any]] = []) -> Dict[str, Any]:
    """Run the LLM with the given query and chat history."""
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        docsearch = PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings)
        
        search_kwargs = {'k': 10}
        metadata_filter = create_metadata_filters(query)
        
        if metadata_filter:
            search_kwargs['filter'] = metadata_filter
            print(f"Applying metadata filters: {metadata_filter}")

        chat = ChatOpenAI(verbose=True, temperature=0)
        retrieval_qa_chat_prompt = hub.pull("tonijwilliams/execorder_prompt")
        stuff_documents_chain = create_stuff_documents_chain(chat, retrieval_qa_chat_prompt)

        rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")
        history_aware_retriever = create_history_aware_retriever(
            llm=chat, 
            retriever=docsearch.as_retriever(search_kwargs=search_kwargs), 
            prompt=rephrase_prompt
        )

        qa = create_retrieval_chain(
            retriever=history_aware_retriever, 
            combine_docs_chain=stuff_documents_chain
        )
        
        result = qa.invoke(input={"input": query, "chat_history": chat_history})
        
        return {
            "query": result["input"],
            "result": result["answer"],
            "source_documents": result["context"]
        }
    except Exception as e:
        print(f"Error in run_llm: {str(e)}")
        raise

if __name__ == "__main__":
    res = run_llm(query="List 5 executive orders that mention immigration.")
    print(res["result"])