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
INDEX_NAME = "project2025"



def run_llm(query: str, chat_history: List[Dict[str, Any]] = []) -> Dict[str, Any]:
    """Run the LLM with the given query and chat history."""
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        docsearch = PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings)
        
        search_kwargs = {'k': 10}
        

        chat = ChatOpenAI(verbose=True, temperature=0)
        retrieval_qa_chat_prompt = hub.pull("tonijwilliams/project2025")
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
    res = run_llm(query="Can you find any proposals within Project 2025 that could affect the balance of power between the federal government and states?")
    print(res["result"])