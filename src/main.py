import os
from dotenv import load_dotenv
from huggingface_hub import login
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.graph import START, StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import List, TypedDict
from IPython.display import Image, display

# === Load environment variables and login ===
load_dotenv()
hf_token = os.getenv("HUGGINGFACE_ACCESS_TOKEN")
login(token=hf_token)

# === Load PDFs ===
directory_path = "E:\\Varshith\\biometric-rag-agent\\data"
all_docs = []

for file in os.listdir(directory_path):
    if file.endswith(".pdf"):
        file_path = os.path.join(directory_path, file)
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        all_docs.extend(docs)

# === Text splitting ===
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = [doc.page_content for doc in all_docs]
chunks = [chunk for text in texts for chunk in text_splitter.split_text(text)]

print(f"Total chunks created: {len(chunks)}")

# === Embedding and FAISS vector store ===
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_texts(chunks, embedding_model)
vectorstore.save_local("my_faiss_index")
print("Saved to vector store")

retriever = vectorstore.as_retriever()

# === LLM endpoint ===
hf_endpoint = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-4-Maverick-17B-128E-Instruct",
    task="text-generation",
    max_new_tokens=512,
    do_sample=False,
    repetition_penalty=1.03,
    api_key=hf_token,
)

chat_hf = ChatHuggingFace(llm=hf_endpoint, verbose=True)

# === Quick LLM test ===
response = chat_hf.invoke("What is the capital of India?")
print(f"Response: {response.content}")

# === Basic RetrievalQA ===
qa_chain = RetrievalQA.from_chain_type(
    llm=chat_hf,
    chain_type="stuff",
    retriever=retriever
)

query2 = "How to add user?"
result = qa_chain.invoke(query2)
print(result)

# === Prompt Template for custom QA ===
prompt = PromptTemplate(
    input_variables=["question", "context"],
    template="""
Use the following context to answer the question at the end.

Context:
{context}

Question:
{question}

Answer:""",
)

# === State type ===
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

# === State functions ===
def retrieve(state: State):
    retrieved_docs = vectorstore.similarity_search(state["question"])
    return {"context": retrieved_docs}

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    formatted_prompt = prompt.format(question=state["question"], context=docs_content)
    messages = [HumanMessage(content=formatted_prompt)]
    response = chat_hf.invoke(messages)
    return {"answer": response.content}

# === Build LangGraph ===
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

# === Run graph ===
response = graph.invoke({"question": "How to add a user"})
print(response["answer"])

# === Try visualizing the graph ===
try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    pass

# === Stream graph steps ===
for step in graph.stream(
    {"question": "What does the documentation say about Creating a user"},
    stream_mode="updates",
):
    print(f"{step}\n\n----------------\n")

print(step["generate"]["answer"])
