from langchain.tools.retriever import create_retriever_tool
from langchain.vectorstores.base import VectorStoreRetriever


def build_retriever_tool(
    vectorstore,
    name: str = "retrieve_docs",
    description: str = "Search and return information from Suprema Biostar2 documentation.",
):
    retriever: VectorStoreRetriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    return create_retriever_tool(retriever, name, description)
