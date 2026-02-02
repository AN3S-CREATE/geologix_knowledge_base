from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
import uvicorn
import os
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(
    title="Geologix AI Backend",
    description="Enterprise AI API for Geologix Knowledge Base",
    version="1.0.0"
)

# CORS Configuration
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "*"  # Allow all for local dev, restrict for production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve UI static files - Updated for new structure
UI_DIR = Path(__file__).resolve().parent.parent / "ui"  # src/geologix/ui
if UI_DIR.exists():
    app.mount("/ui", StaticFiles(directory=str(UI_DIR), html=True), name="ui")

@app.get("/")
async def root():
    """Redirect to UI or return API status."""
    if UI_DIR.exists():
        return RedirectResponse(url="/ui/index.html")
    return {
        "system": "Geologix AI",
        "status": "online",
        "version": "1.0.0",
        "message": "Operational Intelligence Ready"
    }

@app.get("/api")
async def api_root():
    """API status endpoint."""
    return {
        "system": "Geologix AI",
        "status": "online",
        "version": "1.0.0",
        "message": "Operational Intelligence Ready"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "geologix-backend"}

@app.get("/api/dashboard")
async def system_dashboard():
    """
    Comprehensive system health and statistics dashboard.
    """
    import psutil
    from datetime import datetime
    
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Knowledge base stats
    from geologix.core.knowledge_engine import KnowledgeEngine
    engine = KnowledgeEngine()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_gb": round(memory.used / (1024**3), 2),
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2),
        },
        "knowledge_base": {
            "company_docs": len(engine.company_docs),
            "emails": len(engine.email_docs),
            "archives": len(engine.archive_docs),
            "archive_summary": engine.get_archive_summary() if engine.archive_docs else "No archives indexed"
        },
        "ai": {
            "provider": llm.provider if 'llm' in dir() else "unknown",
            "available": llm.is_available() if 'llm' in dir() else False
        }
    }

# --- Core API Endpoints ---
from geologix.core.file_storage import FileStorage
storage = FileStorage()

@app.get("/api/files")
async def list_files(source: str = "documents"):
    """
    List files from the knowledge base.
    Source options: documents, emails, knowledge
    """
    return storage.list_documents(source)

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to the internal storage.
    """
    content = await file.read()
    result = storage.save_upload(content, file.filename)
    return result

# --- Intelligence Endpoints ---
from geologix.core.mcp_tools import MCPTools
from geologix.core.llm_client import LLMClient
from geologix.core.chat_manager import ChatManager
from geologix.core.web_search import WebSearch
from geologix.core.deep_analysis import DeepAnalysis
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

tools = MCPTools()
llm = LLMClient()
chat_mgr = ChatManager()
web_search = WebSearch()
deep_analyzer = DeepAnalysis()

class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None
    conversation_id: Optional[str] = None
    deep_thinking: bool = False
    web_search: bool = False
    model: str = "auto"

class FolderRequest(BaseModel):
    folder_id: str
    name: str

class CreateChatRequest(BaseModel):
    folder_id: str = "default"
    title: Optional[str] = None

class MoveChatRequest(BaseModel):
    chat_id: str
    target_folder_id: str

class ToolExecuteRequest(BaseModel):
    tool_name: str
    params: Dict[str, Any] = Field(default_factory=dict)

@app.get("/api/search")
async def search_knowledge(q: str, source: str = "all", limit: int = 10):
    """
    Search the indexed knowledge base.
    """
    return tools.execute_tool("search_knowledge_base", {"query": q, "source": source, "limit": limit})

@app.get("/api/stats")
async def knowledge_stats():
    """Get lightweight knowledge base statistics for UI dashboards."""
    from geologix.config.config import DATA_DIR

    knowledge_docs = tools.knowledge._load_json(DATA_DIR / "knowledge_index.json")

    categories = {
        "documents": len(tools.knowledge.company_docs),
        "emails": len(tools.knowledge.email_docs),
        "knowledge": len(knowledge_docs),
        "archives": len(tools.knowledge.archive_docs),
    }

    total_items = sum(categories.values())
    return {"success": True, "total_items": total_items, "categories": categories}

@app.get("/api/ai/status")
async def ai_status():
    """Check AI backend availability."""
    return llm.get_status()

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Main AI Interaction Endpoint with Ollama/LM Studio integration.
    Supports: deep thinking, web search, chat history.
    """
    user_msg = request.message
    chat_id = request.chat_id or request.conversation_id
    thinking_output = None
    web_results = None
    
    # Create or load chat session
    if not chat_id:
        chat_result = chat_mgr.create_chat()
        chat_id = chat_result["chat_id"]
    
    # Save user message to history
    chat_mgr.add_message(chat_id, "user", user_msg)
    
    # Get chat history for context
    history = chat_mgr.get_context_messages(chat_id, limit=10)
    
    # 1. Web Search (if enabled)
    web_context = ""
    if request.web_search:
        web_results = web_search.search(user_msg)
        if web_results.get("success"):
            web_context = web_search.format_for_context(web_results)
    
    # 2. Deep Thinking (if enabled)
    if request.deep_thinking:
        context = tools.knowledge.get_context(user_msg)
        deep_result = deep_analyzer.think_deeply(user_msg, context)
        thinking_output = deep_analyzer.format_thinking_for_display()
        
        # Enhanced prompt with thinking
        enhanced_prompt = f"""
{thinking_output}

Based on the above analysis, provide a comprehensive response.

Question: {user_msg}

Analysis Framework: {deep_result.get('framework_used')}
Confidence: {deep_result.get('confidence')}
"""
        ai_response = llm.chat(enhanced_prompt, context=context + web_context)
        
        # Save AI response with thinking
        chat_mgr.add_message(chat_id, "assistant", ai_response, thinking=thinking_output)
        
        return {
            "response": ai_response,
            "chat_id": chat_id,
            "thinking": thinking_output,
            "analysis": deep_result,
            "web_search": web_results,
            "provider": llm.provider
        }
    
    # 3. Initialize context variables early
    context = tools.knowledge.get_context(user_msg)
    
    # 3.5. SPELL CORRECTION & QUERY NORMALIZATION
    from geologix.core.spell_corrector import SpellCorrector
    spell_checker = SpellCorrector()
    
    # Normalize the query (correct spelling, expand synonyms)
    normalized = spell_checker.normalize_query(user_msg)
    corrected_msg = normalized['corrected']
    
    # Log corrections if any were made
    if normalized['has_corrections']:
        print(f"[SPELL CHECK] Corrections: {normalized['corrections']}")
        # Optionally inform user about corrections in response
        correction_note = f"(I understood: {corrected_msg})" if len(normalized['corrections']) > 0 else ""
    else:
        correction_note = ""
    
    # Use corrected message for intent detection
    processing_msg = corrected_msg
    
    # 4. CLARIFICATION & CONFIDENCE SYSTEM
    from geologix.core.intent_clarifier import IntentClarifier
    clarifier = IntentClarifier()
    
    # Detect ambiguity (using corrected message)
    ambiguity_info = clarifier.detect_ambiguity(processing_msg)
    
    # Calculate initial confidence (using corrected message)
    initial_confidence = clarifier.calculate_intent_confidence(processing_msg, [])
    
    # If query is ambiguous or low confidence, ask for clarification
    if clarifier.should_ask_for_clarification(initial_confidence, ambiguity_info):
        clarification = clarifier.generate_clarification_options(processing_msg, ambiguity_info)
        clarification_text = clarifier.format_clarification_response(clarification)
        
        chat_mgr.add_message(chat_id, "assistant", clarification_text)
        return {
            "response": clarification_text,
            "chat_id": chat_id,
            "needs_clarification": True,
            "clarification_options": clarification['options'],
            "confidence": initial_confidence
        }
    
    # 5. SMART INTENT DETECTION & TOOL ROUTING (using spell-corrected message)
    msg_lower = processing_msg.lower()
    
    # === INTENT 1: LIST/INDEX REQUEST ===
    # Detect: "show me index", "list emails", "show all documents", "what emails do we have"
    list_patterns = ["index", "list all", "show all", "list email", "list document", "what email", "what document", 
                     "how many email", "show email index", "show document index", "all email", "all document"]
    is_list_request = any(pattern in msg_lower for pattern in list_patterns)
    
    # Determine source type
    source_type = "all"
    if "email" in msg_lower:
        source_type = "emails"
    elif "document" in msg_lower or "doc" in msg_lower:
        source_type = "documents"
    elif "archive" in msg_lower:
        source_type = "archives"
    
    if is_list_request:
        # Get file listing
        file_list = storage.list_documents(source_type)
        
        if file_list:
            # Create summary for AI
            summary = f"Found {len(file_list)} items in {source_type}:\n"
            for i, item in enumerate(file_list[:20], 1):  # Show first 20
                if isinstance(item, dict):
                    filename = item.get('filename', item.get('subject', 'Unknown'))
                    summary += f"{i}. {filename}\n"
            
            if len(file_list) > 20:
                summary += f"... and {len(file_list) - 20} more items\n"
            
            ai_response = llm.chat(
                f"Present this {source_type} index to the user in a helpful format:\n{summary}",
                context=context + web_context
            )
            chat_mgr.add_message(chat_id, "assistant", ai_response)
            return {
                "response": ai_response,
                "chat_id": chat_id,
                "data": file_list[:100],  # Return first 100 items
                "tool_used": "list_files"
            }
        else:
            response = f"No {source_type} found in the knowledge base."
            chat_mgr.add_message(chat_id, "assistant", response)
            return {"response": response, "chat_id": chat_id, "data": []}
    
    # === INTENT 2: RETRIEVE/READ SPECIFIC ITEM ===
    # Detect: "retrieve email", "read document", "get email", "open document", "show me the email about"
    retrieve_patterns = ["retrieve", "read the", "get the", "open the", "show me the email", 
                        "show me the document", "pull up", "fetch"]
    is_retrieve_request = any(pattern in msg_lower for pattern in retrieve_patterns)
    
    if is_retrieve_request:
        # Try to extract filename or search for specific item
        query = user_msg
        for pattern in retrieve_patterns:
            query = query.lower().replace(pattern, "").strip()
        
        #Search for the specific item
        results = tools.execute_tool("search_knowledge_base", {"query": query, "source": source_type, "limit": 3})
        
        if results:
            # Try to read the first result
            first_result = results[0]
            
            if first_result.get('type') == 'email':
                item_desc = f"Email from {first_result.get('sender', 'Unknown')}: {first_result.get('subject', 'No subject')}"
                content_preview = first_result.get('content', first_result.get('body', 'No content available'))
            else:
                item_desc = f"Document: {first_result.get('filename', 'Unknown file')}"
                content_preview = first_result.get('content', 'No content available')[:1000]
            
            ai_response = llm.chat(
                f"The user requested to retrieve: {item_desc}\n\nContent:\n{content_preview}\n\nSummarize or present this information helpfully.",
                context=context + web_context
            )
            chat_mgr.add_message(chat_id, "assistant", ai_response)
            return {
                "response": ai_response,
                "chat_id": chat_id,
                "data": results[:5],
                "tool_used": "retrieve_document"
            }
        else:
            response = f"I couldn't find the specific item you're looking for. Try being more specific or use the search function."
            chat_mgr.add_message(chat_id, "assistant", response)
            return {"response": response, "chat_id": chat_id}
    
    # === INTENT 3: CALCULATION ===
    if "calculate" in msg_lower or "compute" in msg_lower or "=" in user_msg:
        expr = msg_lower.replace("calculate", "").replace("compute", "").strip()
        result = tools.execute_tool("calculator", {"expression": expr})
        response = f"The result is: {result}"
        chat_mgr.add_message(chat_id, "assistant", response)
        return {"response": response, "chat_id": chat_id, "tool_used": "calculator"}
    
    # === INTENT 4: SEARCH REQUEST ===
    # Detect: "search for", "find emails about", "look for documents containing"
    search_keywords = ["search", "find", "look for"]
    is_search = any(kw in msg_lower for kw in search_keywords) and not is_list_request
    
    if is_search:
        query = user_msg
        for kw in search_keywords:
            query = query.lower().replace(kw, "").strip()
        
        results = tools.execute_tool("search_knowledge_base", {"query": query, "source": source_type})
        
        if results:
            search_context = f"Search results for '{query}':\n"
            for r in results[:10]:
                if r.get('type') == 'email':
                    search_context += f"- Email from {r.get('sender')}: {r.get('subject')}\n"
                elif r.get('type') == 'archive':
                    search_context += f"- Archive: {r.get('filename')} ({r.get('category', 'uncategorized')})\n"
                else:
                    search_context += f"- Document: {r.get('filename')}\n"
            
            ai_response = llm.chat(
                f"The user searched for '{query}'. Here's what I found:\n{search_context}\n\nSummarize these results helpfully and offer to retrieve specific items.",
                context=context + web_context
            )
            chat_mgr.add_message(chat_id, "assistant", ai_response)
            return {
                "response": ai_response,
                "chat_id": chat_id,
                "data": results[:10],
                "tool_used": "search_knowledge_base"
            }
        else:
            response = f"No results found for '{query}'. Try different search terms or check the index to see what's available."
            chat_mgr.add_message(chat_id, "assistant", response)
            return {"response": response, "chat_id": chat_id, "data": [], "tool_used": "search_knowledge_base"}
    
    # 6. General AI chat with knowledge context
    full_context = context + web_context
    ai_response = llm.chat(user_msg, context=full_context)
    
    # Save AI response
    chat_mgr.add_message(chat_id, "assistant", ai_response)
    
    return {
        "response": ai_response,
        "chat_id": chat_id,
        "web_search": web_results if request.web_search else None,
        "provider": llm.provider
    }

# ═══════════════════════════════════════════════════════════════════════════════
# CHAT HISTORY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/chats")
async def list_chats(folder_id: str = None):
    """List all chat sessions, optionally filtered by folder."""
    return chat_mgr.list_chats(folder_id)

@app.post("/api/chats")
async def create_chat(request: CreateChatRequest):
    """Create a new chat session."""
    return chat_mgr.create_chat(title=request.title, folder_id=request.folder_id)

@app.get("/api/chats/{chat_id}")
async def get_chat(chat_id: str):
    """Get a specific chat session with history."""
    chat = chat_mgr.load_chat(chat_id)
    if not chat:
        return {"error": "Chat not found"}
    return chat

@app.delete("/api/chats/{chat_id}")
async def delete_chat(chat_id: str):
    """Delete a chat session."""
    return chat_mgr.delete_chat(chat_id)

@app.post("/api/chats/{chat_id}/move")
async def move_chat(chat_id: str, request: MoveChatRequest):
    """Move a chat to a different folder."""
    return chat_mgr.move_chat(chat_id, request.target_folder_id)

# ═══════════════════════════════════════════════════════════════════════════════
# FOLDER MANAGEMENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/folders")
async def list_folders():
    """List all chat folders."""
    return chat_mgr.list_folders()

@app.post("/api/folders")
async def create_folder(request: FolderRequest):
    """Create a new chat folder."""
    return chat_mgr.create_folder(request.folder_id, request.name)

@app.delete("/api/folders/{folder_id}")
async def delete_folder(folder_id: str):
    """Delete a folder (moves chats to default)."""
    return chat_mgr.delete_folder(folder_id)

# ═══════════════════════════════════════════════════════════════════════════════
# WEB SEARCH ENDPOINT
# ═╝══════════════════════════════════════════════════════════════════════════════

@app.get("/api/web-search")
async def search_web(q: str, max_results: int = 5):
    """Perform a web search."""
    return web_search.search(q, max_results)

# ═══════════════════════════════════════════════════════════════════════════════
# DEEP ANALYSIS ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/analyze")
async def deep_analyze(request: ChatRequest):
    """Perform deep analysis on a question with full email/document context."""
    msg_lower = request.message.lower()
    
    # Get basic context
    context = tools.knowledge.get_context(request.message)
    
    # Detect if analysis requires email/document data
    requires_emails = any(kw in msg_lower for kw in ['email', 'emails', 'communication', 'correspondence'])
    requires_docs = any(kw in msg_lower for kw in ['document', 'documents', 'contract', 'report', 'invoice'])
    
    # Fetch relevant data from local knowledge base
    structured_data = {}
    
    if requires_emails:
        # Fetch up to 50 emails for comprehensive analysis
        email_results = tools.execute_tool("search_knowledge_base", {
            "query": request.message,
            "source": "emails",
            "limit": 50
        })
        
        if email_results:
            # Structure email data for analysis
            structured_data['emails'] = {
                'count': len(email_results),
                'items': []
            }
            
            for email in email_results:
                structured_data['emails']['items'].append({
                    'date': email.get('date', 'Unknown'),
                    'sender': email.get('sender', 'Unknown'),
                    'subject': email.get('subject', 'No subject'),
                    'content': email.get('content', email.get('body', ''))[:500]  # First 500 chars
                })
            
            # Add summary to context
            context += f"\n\n[EMAIL DATA AVAILABLE: {len(email_results)} emails found]\n"
    
    if requires_docs:
        # Fetch up to 30 documents for analysis
        doc_results = tools.execute_tool("search_knowledge_base", {
            "query": request.message,
            "source": "documents",
            "limit": 30
        })
        
        if doc_results:
            structured_data['documents'] = {
                'count': len(doc_results),
                'items': []
            }
            
            for doc in doc_results:
                structured_data['documents']['items'].append({
                    'filename': doc.get('filename', 'Unknown'),
                    'type': doc.get('type', 'document'),
                    'content': doc.get('content', '')[:500]
                })
            
            context += f"\n[DOCUMENT DATA AVAILABLE: {len(doc_results)} documents found]\n"
    
    # Pass structured data to deep analysis engine
    result = deep_analyzer.think_deeply(
        request.message, 
        context, 
        data=structured_data if structured_data else None
    )
    
    return result

@app.post("/api/forecast")
async def generate_forecast(metric: str, current_value: float, growth_rate: float = 0.03, periods: int = 12):
    """Generate future projections for a metric."""
    return deep_analyzer.project_future(metric, current_value, growth_rate, periods)

# ═══════════════════════════════════════════════════════════════════════════════
# MEMORY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/memory/fact")
async def remember_fact(fact: str, category: str = "general", confidence: float = 0.8):
    """Store a fact in long-term memory."""
    return tools.memory.remember_fact(fact, category, confidence)

@app.get("/api/memory/facts")
async def recall_facts(query: str = None, category: str = None, limit: int = 10):
    """Recall facts from memory."""
    return tools.memory.recall_facts(query, category, limit)

@app.post("/api/memory/entity")
async def remember_entity(name: str, entity_type: str, attributes: dict = None):
    """Store entity information."""
    return tools.memory.remember_entity(name, entity_type, attributes or {})

@app.get("/api/memory/entity/{name}")
async def get_entity(name: str, entity_type: str = None):
    """Get entity information."""
    return tools.memory.get_entity(name, entity_type) or {"error": "Entity not found"}

@app.get("/api/memory/stats")
async def memory_stats():
    """Get memory system statistics."""
    return tools.memory.get_stats()

# ═══════════════════════════════════════════════════════════════════════════════
# EXTRACTOR ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/extract/entities")
async def extract_entities(text: str):
    """Extract entities from text."""
    return tools.extractors.extract_entities(text)

@app.post("/api/extract/sentiment")
async def analyze_sentiment(text: str):
    """Analyze sentiment of text."""
    return tools.extractors.analyze_sentiment(text)

@app.post("/api/extract/summary")
async def summarize_text(text: str, max_sentences: int = 5):
    """Summarize text."""
    return tools.extractors.summarize_text(text, max_sentences)

@app.post("/api/extract/timeline")
async def extract_timeline(text: str):
    """Extract timeline from text."""
    return tools.extractors.extract_timeline(text)

@app.post("/api/extract/compare")
async def compare_documents(doc1: str, doc2: str):
    """Compare two documents."""
    return tools.extractors.compare_documents(doc1, doc2)

# ═══════════════════════════════════════════════════════════════════════════════
# AGENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/agent/intent")
async def analyze_intent(query: str):
    """Analyze user intent."""
    return tools.agents.analyze_intent(query)

@app.post("/api/agent/plan")
async def create_plan(query: str):
    """Create execution plan for a query."""
    return tools.agents.create_execution_plan(query)

@app.post("/api/agent/execute")
async def execute_plan(plan: dict):
    """Execute a plan."""
    return tools.agents.execute_plan(plan, tools.execute_tool)

@app.get("/api/agent/followups")
async def suggest_followups(query: str):
    """Suggest follow-up questions."""
    return tools.agents.suggest_follow_ups(query, None)

# ═══════════════════════════════════════════════════════════════════════════════
# STREAMING ENDPOINT
#  ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """Stream AI response token by token."""
    context = tools.knowledge.get_context(request.message)
    
    async def generate():
        for chunk in llm.stream_chat(request.message, context=context):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

# ═══════════════════════════════════════════════════════════════════════════════
# TOOLS INFO ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/tools")
async def list_tools():
    """List all available MCP tools."""
    return {
        "tools": tools.list_available_tools(),
        "categories": tools.get_tool_categories(),
        "total": tools.get_tool_count()
    }

@app.post("/api/tools/execute")
async def execute_tool(request: ToolExecuteRequest):
    """Execute an MCP tool by name with parameters."""
    return tools.execute_tool(request.tool_name, request.params)

if __name__ == "__main__":
    import uvicorn
    # Updated: Run from new package structure
    uvicorn.run("geologix.core.server:app", host="0.0.0.0", port=8000, reload=True)
