from langchain.tools.retriever import create_retriever_tool
from langchain.vectorstores.base import VectorStoreRetriever
from langchain_tavily import TavilySearch


def build_retriever_tool(
    vectorstore,
    name: str = "retrieve_docs",
    description: str = "Search and return information from Suprema Biostar2 documentation.",
):
    retriever: VectorStoreRetriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    return create_retriever_tool(retriever, name, description)


def build_tavily_search_tool(max_results, topic="general"):
    return TavilySearch(max_results=max_results, topic=topic)
