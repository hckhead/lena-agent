import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

def get_retriever(docs_dir: str = "docs"):
    """
    Initializes and returns a retriever from the documents in the specified directory.
    Supports .txt, .md, and .pdf files.
    """
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
        # Create a dummy file if empty to avoid errors
        with open(os.path.join(docs_dir, "readme.txt"), "w") as f:
            f.write("This is a placeholder document for the RAG system.")

    # Load documents from multiple file types
    all_docs = []
    
    # Load .txt files
    txt_loader = DirectoryLoader(docs_dir, glob="**/*.txt", loader_cls=TextLoader)
    all_docs.extend(txt_loader.load())
    
    # Load .md files
    md_loader = DirectoryLoader(docs_dir, glob="**/*.md", loader_cls=UnstructuredMarkdownLoader)
    all_docs.extend(md_loader.load())
    
    # Load .pdf files
    pdf_loader = DirectoryLoader(docs_dir, glob="**/*.pdf", loader_cls=PyPDFLoader)
    all_docs.extend(pdf_loader.load())
    
    if not all_docs:
        # Fallback if no docs found even after creation attempt (e.g. permission issues)
        return None

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(all_docs)
    
    # Persist directory for Chroma
    persist_directory = "./chroma_db"
    
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=OpenAIEmbeddings(),
        persist_directory=persist_directory
    )
    
    return vectorstore.as_retriever()
