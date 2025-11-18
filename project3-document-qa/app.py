"""
Document Q&A System with RAG (Retrieval-Augmented Generation)
Simulates Azure OpenAI RAG pipeline using open-source tools
"""

import gradio as gr
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer
from typing import List, Dict, Tuple
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentQASystem:
    """
    RAG-based Document Q&A System
    Simulates Azure OpenAI with Azure Cognitive Search
    """
    
    def __init__(
        self,
        embedding_model_name: str = "all-MiniLM-L6-v2",
        llm_model_name: str = "distilgpt2",
        collection_name: str = "documents"
    ):
        """Initialize the Q&A system"""
        
        logger.info("🔄 Initializing Document Q&A System...")
        
        # Initialize embedding model
        logger.info("Loading embedding model: %s", embedding_model_name)
        self.embedding_model = SentenceTransformer(embedding_model_name)
        
        # Initialize ChromaDB
        logger.info("Initializing ChromaDB...")
        self.chroma_client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=True
        ))
        
        # Create or get collection
        try:
            self.collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={"description": "Document knowledge base"}
            )
        except Exception:
            self.collection = self.chroma_client.get_collection(name=collection_name)
        
        # Initialize LLM
        logger.info("Loading language model: %s", llm_model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(llm_model_name)
        self.llm = pipeline(
            "text-generation",
            model=llm_model_name,
            tokenizer=self.tokenizer,
            max_length=512,
            temperature=0.7,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        logger.info("✅ System initialized successfully")
    
    def add_documents(self, documents: List[str], metadata: List[Dict] = None, ids: List[str] = None):
        """
        Add documents to the knowledge base
        
        Args:
            documents: List of document texts
            metadata: Optional metadata for each document
            ids: Optional list of IDs to use; if not provided, auto-generate
        """
        if not documents:
            return
        
        logger.info("🔄 Adding %d documents to knowledge base...", len(documents))
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Generate IDs
        if ids is None:
            ids = [f"doc_{i}_{datetime.now().timestamp()}" for i in range(len(documents))]
        else:
            # Ensure lengths match
            if len(ids) != len(documents):
                raise ValueError("Length of ids must match length of documents")
        
        # Prepare metadata
        if metadata is None:
            metadata = [{"source": f"document_{i}"} for i in range(len(documents))]
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            ids=ids,
            metadatas=metadata
        )
        
        logger.info("✅ Added %d documents successfully", len(documents))
        
        return len(documents)
    
    def search_documents(self, query: str, n_results: int = 3) -> Tuple[List[str], List[float]]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            n_results: Number of results to return
        
        Returns:
            Tuple of (documents, distances)
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        documents = results['documents'][0] if results['documents'] else []
        distances = results['distances'][0] if results['distances'] else []
        
        return documents, distances
    
    def generate_answer(
        self,
        question: str,
        context_docs: List[str],
        max_new_tokens: int = 150
    ) -> str:
        """
        Generate answer using retrieved context
        
        Args:
            question: User question
            context_docs: Retrieved context documents
            max_new_tokens: Maximum tokens to generate
        
        Returns:
            Generated answer
        """
        # Prepare prompt with context
        context = "\n\n".join([f"Context {i+1}: {doc}" for i, doc in enumerate(context_docs)])
        
        prompt = f"""Based on the following context, answer the question concisely.

{context}

Question: {question}

Answer:"""
        
        # Generate response
        try:
            response = self.llm(
                prompt,
                max_new_tokens=max_new_tokens,
                num_return_sequences=1,
                temperature=0.7
            )
            
            # Extract answer (remove prompt)
            full_text = response[0]['generated_text']
            answer = full_text[len(prompt):].strip()
            
            # Clean up answer
            if not answer:
                answer = "I couldn't generate a specific answer based on the context."
            
            return answer
            
        except Exception as e:
            logger.error("Error generating answer: %s", e)
            return f"Error generating answer: {str(e)}"
    
    def answer_question(
        self,
        question: str,
        n_context_docs: int = 3
    ) -> Tuple[str, List[str], List[float]]:
        """
        Complete RAG pipeline: retrieve and generate
        
        Args:
            question: User question
            n_context_docs: Number of context documents to retrieve
        
        Returns:
            Tuple of (answer, retrieved_docs, relevance_scores)
        """
        logger.info("🔍 Processing question: %s", question)
        
        # Retrieve relevant documents
        context_docs, distances = self.search_documents(question, n_context_docs)
        
        if not context_docs:
            return "No relevant documents found in the knowledge base.", [], []
        
        # Calculate relevance scores (inverse of distance)
        relevance_scores = [1.0 / (1.0 + d) for d in distances]
        
        # Generate answer
        answer = self.generate_answer(question, context_docs)
        
        logger.info("✅ Answer generated successfully")
        
        return answer, context_docs, relevance_scores
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the document collection"""
        count = self.collection.count()
        
        return {
            "total_documents": count,
            "collection_name": self.collection.name,
            "metadata": self.collection.metadata
        }
    
    def clear_collection(self):
        """Clear all documents from the collection"""
        try:
            self.chroma_client.delete_collection(self.collection.name)
            self.collection = self.chroma_client.create_collection(
                name=self.collection.name,
                metadata={"description": "Document knowledge base"}
            )
            logger.info("✅ Collection cleared successfully")
        except Exception as e:
            logger.error("Error clearing collection: %s", e)


# Initialize the QA system
qa_system = DocumentQASystem()


# Sample documents for demonstration
SAMPLE_DOCUMENTS = [
    "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing computer programs that can access data and use it to learn for themselves.",
    
    "Deep learning is part of machine learning methods based on artificial neural networks with representation learning. Learning can be supervised, semi-supervised or unsupervised. Deep learning architectures such as deep neural networks, deep belief networks, and recurrent neural networks have been applied to fields including computer vision, speech recognition, and natural language processing.",
    
    "Natural language processing (NLP) is a subfield of linguistics, computer science, and artificial intelligence concerned with the interactions between computers and human language, in particular how to program computers to process and analyze large amounts of natural language data. The goal is to enable computers to understand, interpret, and generate human language in a valuable way.",
    
    "The transformer architecture revolutionized NLP by introducing the attention mechanism, which allows models to focus on different parts of the input when processing each word. This architecture forms the basis of modern large language models like GPT and BERT.",
    
    "MLOps is a set of practices that combines Machine Learning, DevOps, and Data Engineering to deploy and maintain ML systems in production reliably and efficiently. Key components include experiment tracking, model versioning, automated testing, continuous training, and monitoring.",
    
    "Cloud computing provides on-demand delivery of IT resources over the Internet with pay-as-you-go pricing. Instead of buying, owning, and maintaining physical data centers and servers, you can access technology services such as computing power, storage, and databases on an as-needed basis from cloud providers.",
    
    "Docker is a platform that uses OS-level virtualization to deliver software in packages called containers. Containers are isolated from one another and bundle their own software, libraries and configuration files; they can communicate with each other through well-defined channels.",
    
    "Kubernetes is an open-source container orchestration platform that automates deploying, scaling, and managing containerized applications. It groups containers into logical units for easy management and discovery, and provides tools for load balancing, rolling updates, and service discovery.",
]

# HR/Payroll policy sample documents for domain-specific demo
HR_SAMPLE_DOCUMENTS = [
    "Paid Time Off (PTO): Full-time employees accrue 1.67 days of PTO per month (20 days/year). Unused PTO carries over up to 5 days. PTO requests must be submitted at least 2 weeks in advance via the HR portal.",
    "Overtime Policy: Non-exempt hourly employees are eligible for overtime pay at 1.5x the regular rate for hours worked over 40 in a workweek. Overtime must be pre-approved by a manager.",
    "Payroll Schedule: Employees are paid bi-weekly on Fridays. Direct deposit is required. Payroll cut-off is Tuesday 5pm for the current pay period.",
    "Benefits Eligibility: Employees working 30+ hours per week are eligible for medical, dental, and vision plans starting on the first day of the month following 30 days of employment.",
    "Leave of Absence: FMLA provides up to 12 weeks of unpaid, job-protected leave for eligible employees. Employees must provide 30 days' notice when foreseeable and submit required documentation.",
    "Expense Reimbursement: Business expenses must be submitted within 30 days with itemized receipts. Reimbursements are processed in the next payroll cycle upon approval.",
    "Performance Reviews: Formal performance reviews occur annually in Q4 with mid-year checkpoints. Salary adjustments, if any, are effective in the first payroll of Q1."
]


# Helper: add sample documents with dedup by deterministic IDs
def _add_sample_documents_dedup() -> int:
    ids = [f"sample_doc_{i}" for i in range(len(SAMPLE_DOCUMENTS))]
    metadata = [{"source": ids[i], "topic": "AI/ML"} for i in range(len(SAMPLE_DOCUMENTS))]
    # Find which IDs already exist
    existing_ids = set()
    try:
        got = qa_system.collection.get(ids=ids)
        if got and isinstance(got.get("ids", None), list):
            existing_ids = set(got["ids"])  # only the ones that exist
    except Exception as e:
        logger.warning("Lookup existing sample docs failed (will attempt to add all): %s", e)
    # Compute missing indices
    to_add_idx = [i for i, _id in enumerate(ids) if _id not in existing_ids]
    if not to_add_idx:
        return 0
    # Slice the lists
    docs = [SAMPLE_DOCUMENTS[i] for i in to_add_idx]
    metas = [metadata[i] for i in to_add_idx]
    sel_ids = [ids[i] for i in to_add_idx]
    # Add only missing
    qa_system.add_documents(docs, metas, ids=sel_ids)
    return len(docs)


# Preload sample documents once on startup if collection is empty
def _preload_sample_documents_if_empty():
    try:
        stats = qa_system.get_collection_stats()
        total = stats.get("total_documents", 0)
        if total == 0:
            added = _add_sample_documents_dedup()
            logger.info("✅ Preloaded sample documents (added=%d)", added)
        else:
            logger.info("ℹ️ Knowledge base already has %d documents; skipping preload", total)
    except Exception as e:
        logger.warning("Could not preload sample documents: %s", e)


# Execute preload at import/startup
_preload_sample_documents_if_empty()


# Gradio Interface Functions
def load_sample_documents():
    """Load sample documents into the system (idempotent)"""
    added = _add_sample_documents_dedup()
    stats = qa_system.get_collection_stats()
    if added == 0:
        return f"ℹ️ Sample documents were already loaded. Total documents: {stats['total_documents']}"
    return f"✅ Loaded {added} sample documents. Total documents: {stats['total_documents']}"


def load_sample_hr_documents():
    """Load HR/policy sample documents into the system (idempotent)"""
    # Build deterministic IDs for HR docs
    ids = [f"hr_doc_{i}" for i in range(len(HR_SAMPLE_DOCUMENTS))]
    metadata = [{"source": ids[i], "domain": "hr", "topic": "HR/Payroll"} for i in range(len(HR_SAMPLE_DOCUMENTS))]

    # Determine which ones already exist
    existing_ids = set()
    try:
        got = qa_system.collection.get(ids=ids)
        if got and isinstance(got.get("ids", None), list):
            existing_ids = set(got["ids"])  # existing subset
    except Exception:
        existing_ids = set()

    to_add_idx = [i for i, _id in enumerate(ids) if _id not in existing_ids]
    if not to_add_idx:
        stats = qa_system.get_collection_stats()
        return f"ℹ️ HR policy documents already loaded. Total documents: {stats['total_documents']}"

    docs = [HR_SAMPLE_DOCUMENTS[i] for i in to_add_idx]
    metas = [metadata[i] for i in to_add_idx]
    sel_ids = [ids[i] for i in to_add_idx]

    qa_system.add_documents(docs, metas, ids=sel_ids)
    stats = qa_system.get_collection_stats()
    return f"✅ Loaded {len(docs)} HR policy documents. Total documents: {stats['total_documents']}"


def add_custom_document(text: str):
    """Add a custom document"""
    if not text.strip():
        return "⚠️ Please enter document text"
    
    qa_system.add_documents([text], [{"source": "user_upload", "timestamp": str(datetime.now())}])
    stats = qa_system.get_collection_stats()
    return f"✅ Document added successfully! Total documents: {stats['total_documents']}"


def ask_question(question: str, num_context: int):
    """Answer a question using RAG"""
    if not question.strip():
        return "⚠️ Please enter a question", "", ""
    
    # Get answer
    answer, context_docs, relevance_scores = qa_system.answer_question(question, num_context)
    
    # Format context documents
    context_display = ""
    for i, (doc, score) in enumerate(zip(context_docs, relevance_scores)):
        context_display += f"**Context {i+1}** (Relevance: {score:.3f})\n{doc}\n\n"
    
    # Format stats
    stats = qa_system.get_collection_stats()
    stats_display = f"📊 Knowledge Base: {stats['total_documents']} documents"
    
    return answer, context_display, stats_display


def clear_knowledge_base():
    """Clear all documents"""
    qa_system.clear_collection()
    return "✅ Knowledge base cleared successfully"


def get_stats():
    """Get system statistics"""
    stats = qa_system.get_collection_stats()
    return f"""
📊 **System Statistics**
- Total Documents: {stats['total_documents']}
- Collection: {stats['collection_name']}
- Embedding Model: all-MiniLM-L6-v2
- LLM: DistilGPT2
"""


# Build Gradio Interface
with gr.Blocks(title="Document Q&A System", theme=gr.themes.Soft()) as demo:
    
    gr.Markdown("""
    # 📚 Document Q&A System with RAG
    
    **Simulates:** Azure OpenAI + Azure Cognitive Search  
    **Tech Stack:** ChromaDB, SentenceTransformers, Hugging Face Transformers
    
    This system demonstrates Retrieval-Augmented Generation (RAG) for question answering over documents.
    """)
    
    with gr.Tab("💬 Ask Questions"):
        gr.Markdown("### Ask questions about your documents")
        
        with gr.Row():
            with gr.Column():
                question_input = gr.Textbox(
                    label="Your Question",
                    placeholder="What is machine learning?",
                    lines=3
                )
                num_context_slider = gr.Slider(
                    minimum=1,
                    maximum=5,
                    value=3,
                    step=1,
                    label="Number of context documents to retrieve"
                )
                ask_btn = gr.Button("🔍 Ask Question", variant="primary")
            
            with gr.Column():
                answer_output = gr.Textbox(
                    label="Answer",
                    lines=6,
                    interactive=False
                )
                stats_output = gr.Textbox(
                    label="Stats",
                    lines=1,
                    interactive=False
                )
        
        with gr.Accordion("📄 Retrieved Context", open=False):
            context_output = gr.Markdown()
        
        # Sample questions
        gr.Markdown("### 💡 Try these sample questions:")
        sample_questions = [
            "What is machine learning?",
            "Explain deep learning",
            "What is the transformer architecture?",
            "How does MLOps work?",
            "What is the difference between containers and virtual machines?"
        ]
        
        with gr.Row():
            for q in sample_questions[:3]:
                gr.Button(q, size="sm").click(
                    lambda x=q: x,
                    outputs=question_input
                )
        
        with gr.Row():
            for q in sample_questions[3:]:
                gr.Button(q, size="sm").click(
                    lambda x=q: x,
                    outputs=question_input
                )
        
        ask_btn.click(
            ask_question,
            inputs=[question_input, num_context_slider],
            outputs=[answer_output, context_output, stats_output]
        )
    
    with gr.Tab("📁 Manage Documents"):
        gr.Markdown("### Add documents to the knowledge base")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### Load Sample Documents")
                load_sample_btn = gr.Button("📥 Load Sample AI/ML Documents", variant="primary")
                load_hr_btn = gr.Button("📥 Load Sample HR Policy Documents")
                load_status = gr.Textbox(label="Status", interactive=False)
                
                load_sample_btn.click(
                    load_sample_documents,
                    outputs=load_status
                )
                load_hr_btn.click(
                    load_sample_hr_documents,
                    outputs=load_status
                )
            
            with gr.Column():
                gr.Markdown("#### Add Custom Document")
                custom_doc_input = gr.Textbox(
                    label="Document Text",
                    placeholder="Enter your document text here...",
                    lines=8
                )
                add_doc_btn = gr.Button("➕ Add Document")
                add_status = gr.Textbox(label="Status", interactive=False)
                
                add_doc_btn.click(
                    add_custom_document,
                    inputs=custom_doc_input,
                    outputs=add_status
                )
        
        gr.Markdown("---")
        
        with gr.Row():
            stats_btn = gr.Button("📊 View Statistics")
            clear_btn = gr.Button("🗑️ Clear Knowledge Base", variant="stop")
        
        management_output = gr.Markdown()
        
        stats_btn.click(get_stats, outputs=management_output)
        clear_btn.click(clear_knowledge_base, outputs=management_output)
    
    with gr.Tab("ℹ️ About"):
        gr.Markdown("""
        ## 🎯 About This System
        
        This Document Q&A system demonstrates a **Retrieval-Augmented Generation (RAG)** pipeline,
        which is the same architecture used in production systems like Azure OpenAI with Azure Cognitive Search.
        
        ### 🏗️ Architecture
        
        1. **Document Ingestion**: Documents are embedded using SentenceTransformers
        2. **Vector Storage**: ChromaDB stores document embeddings
        3. **Retrieval**: Questions are embedded and similar documents are retrieved
        4. **Generation**: A language model generates answers based on retrieved context
        
        ### 🛠️ Technology Stack
        
        - **Embeddings**: `all-MiniLM-L6-v2` (384-dimensional)
        - **Vector Database**: ChromaDB (open-source)
        - **LLM**: DistilGPT-2 (compact GPT-2 variant)
        - **Interface**: Gradio
        
        ### 💡 Enterprise Comparison
        
        | Component | This Implementation | Azure Enterprise |
        |-----------|-------------------|------------------|
        | Embeddings | SentenceTransformers | Azure OpenAI Embeddings |
        | Vector DB | ChromaDB | Azure Cognitive Search |
        | LLM | DistilGPT-2 | GPT-4 / GPT-3.5 |
        | Interface | Gradio | Custom Web App |
        
        ### 🎤 Interview Tips
        
        When discussing this project:
        - Emphasize understanding of **RAG architecture**
        - Explain **trade-offs** between open-source and commercial solutions
        - Discuss **vector similarity search** and embedding techniques
        - Highlight **scalability considerations** for production
        - Show knowledge of **prompt engineering** for better answers
        
        ### 🚀 Improvements for Production
        
        1. Use larger, more capable LLMs (LLaMA, Falcon)
        2. Implement reranking for better context selection
        3. Add conversation memory for multi-turn dialogues
        4. Implement caching for frequently asked questions
        5. Add evaluation metrics (ROUGE, BLEU, etc.)
        6. Scale with distributed vector database (Pinecone, Weaviate)
        
        ---
        
        **Built with ❤️ using 100% open-source tools**
        """)


# Launch the app
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting Document Q&A System")
    print("=" * 60)
    print("📚 Simulates: Azure OpenAI + Azure Cognitive Search")
    print("🛠️ Tech: ChromaDB + SentenceTransformers + HuggingFace")
    print("=" * 60)
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
