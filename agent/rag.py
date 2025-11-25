import os
from typing import List, Optional
from langchain_core.documents import Document, BaseDocumentCompressor
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank

# Fallback implementations if imports fail
try:
    from langchain.retrievers import EnsembleRetriever
except ImportError:
    class EnsembleRetriever(BaseRetriever):
        retrievers: List[BaseRetriever]
        weights: List[float]

        def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
        ) -> List[Document]:
            # Reciprocal Rank Fusion (RRF) Implementation
            # rrf_score = sum(weight * (1 / (rank + k)))
            rrf_k = 60
            doc_scores = {}
            all_docs = {}
            
            for i, retriever in enumerate(self.retrievers):
                docs = retriever.invoke(query)
                weight = self.weights[i]
                for rank, doc in enumerate(docs):
                    # Use content as key for deduplication
                    key = doc.page_content
                    if key not in all_docs:
                        all_docs[key] = doc
                        doc_scores[key] = 0.0
                    doc_scores[key] += weight * (1 / (rank + rrf_k))
            
            # Sort by RRF score and return documents
            sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
            return [all_docs[k] for k, v in sorted_docs]

try:
    from langchain.retrievers import ContextualCompressionRetriever
except ImportError:
    class ContextualCompressionRetriever(BaseRetriever):
        base_compressor: BaseDocumentCompressor
        base_retriever: BaseRetriever
        
        def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
        ) -> List[Document]:
            docs = self.base_retriever.invoke(query)
            compressed_docs = self.base_compressor.compress_documents(docs, query)
            return list(compressed_docs)

def get_retriever(docs_dir: str = "docs", enable_rerank: bool = False):
    """
    Initializes and returns a retriever from the documents in the specified directory.
    Supports .txt, .md, and .pdf files.
    
    Args:
        docs_dir: Directory containing documents.
        enable_rerank: Whether to enable re-ranking using Flashrank.
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
    
    # 1. Vector Search (Chroma)
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=OpenAIEmbeddings(),
        persist_directory=persist_directory
    )
    vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    # 2. Keyword Search (BM25)
    bm25_retriever = BM25Retriever.from_documents(splits)
    bm25_retriever.k = 5
    
    # 3. Hybrid Search (Ensemble)
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, vector_retriever],
        weights=[0.5, 0.5]
    )
    
    final_retriever = ensemble_retriever
    
    # 4. Optional Re-ranking
    if enable_rerank:
        compressor = FlashrankRerank()
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor, 
            base_retriever=ensemble_retriever
        )
        final_retriever = compression_retriever
    
    return final_retriever
