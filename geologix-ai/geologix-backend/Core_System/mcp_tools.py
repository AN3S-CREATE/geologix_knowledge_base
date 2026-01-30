"""
GeoLogix AI - MCP Tools Suite
Complete toolkit for enterprise intelligence operations.
"""

from typing import Dict, Any, List, Optional
import math
import sys
from pathlib import Path
from datetime import datetime

# Imports
sys.path.append(str(Path(__file__).resolve().parent.parent))
from Core_System.knowledge_engine import KnowledgeEngine
from Core_System.file_storage import FileStorage
from Core_System.web_search import WebSearch
from Core_System.deep_analysis import DeepAnalysis
from Core_System.chat_manager import ChatManager
from Core_System.ai_memory import AIMemory
from Core_System.ai_extractors import AIExtractors
from Core_System.ai_agents import AIAgents
from Core_System.llm_client import LLMClient


class MCPTools:
    """
    Complete suite of MCP tools available to GeoLogix AI.
    Includes: Knowledge, Web Search, Analysis, Forecasting, Chat Management.
    """
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.knowledge = KnowledgeEngine()
        self.storage = FileStorage()
        self.web_search = WebSearch()
        self.analyzer = DeepAnalysis(self.llm_client)
        self.chat_manager = ChatManager()
        self.memory = AIMemory()
        self.extractors = AIExtractors(self.llm_client)
        self.agents = AIAgents(self)

    # ═══════════════════════════════════════════════════════════════════════════
    # TOOL REGISTRY
    # ═══════════════════════════════════════════════════════════════════════════

    def list_available_tools(self) -> List[Dict]:
        """Return all available MCP tools with descriptions."""
        return [
            # Knowledge Base Tools
            {
                "name": "search_knowledge_base",
                "description": "Search internal company documents, emails, and archives.",
                "parameters": {"query": "string", "source": "string (optional: all|documents|emails|archives)"}
            },
            {
                "name": "read_document",
                "description": "Read the full content of a specific file.",
                "parameters": {"file_path": "string"}
            },
            {
                "name": "search_archives",
                "description": "Search historical company archives with tag filtering.",
                "parameters": {"query": "string", "tags": "list of strings (optional)"}
            },
            {
                "name": "get_archive_summary",
                "description": "Get summary statistics of indexed archives.",
                "parameters": {}
            },
            
            # Web Search Tools
            {
                "name": "web_search",
                "description": "Search the internet for current information.",
                "parameters": {"query": "string", "max_results": "integer (default: 5)"}
            },
            {
                "name": "search_industry_news",
                "description": "Search for mining/earthworks industry news.",
                "parameters": {"topic": "string"}
            },
            
            # Analysis Tools
            {
                "name": "deep_analyze",
                "description": "Perform deep thinking analysis on a complex question.",
                "parameters": {"question": "string", "context": "string (optional)"}
            },
            {
                "name": "swot_analysis",
                "description": "Perform SWOT analysis on a topic.",
                "parameters": {"topic": "string"}
            },
            {
                "name": "risk_assessment",
                "description": "Perform risk assessment analysis.",
                "parameters": {"topic": "string"}
            },
            {
                "name": "root_cause_analysis",
                "description": "Perform root cause analysis (5 Whys).",
                "parameters": {"problem": "string"}
            },
            
            # Forecasting Tools
            {
                "name": "forecast",
                "description": "Generate future projections for a metric.",
                "parameters": {
                    "metric": "string",
                    "current_value": "number",
                    "growth_rate": "number (default: 0.03)",
                    "periods": "integer (default: 12)"
                }
            },
            {
                "name": "calculate_growth",
                "description": "Calculate growth rate between two values.",
                "parameters": {"start_value": "number", "end_value": "number", "periods": "integer"}
            },
            {
                "name": "calculate_roi",
                "description": "Calculate return on investment.",
                "parameters": {"investment": "number", "returns": "number"}
            },
            {
                "name": "calculate_breakeven",
                "description": "Calculate breakeven point.",
                "parameters": {"fixed_costs": "number", "variable_cost": "number", "price": "number"}
            },
            
            # Calculator
            {
                "name": "calculator",
                "description": "Evaluate a mathematical expression.",
                "parameters": {"expression": "string"}
            },
            
            # Chat Management Tools
            {
                "name": "list_chats",
                "description": "List all chat sessions.",
                "parameters": {"folder_id": "string (optional)"}
            },
            {
                "name": "get_chat_history",
                "description": "Get messages from a chat session.",
                "parameters": {"chat_id": "string", "limit": "integer (default: 20)"}
            },
            {
                "name": "create_folder",
                "description": "Create a new chat folder.",
                "parameters": {"folder_id": "string", "name": "string"}
            },
            {
                "name": "list_folders",
                "description": "List all chat folders.",
                "parameters": {}
            },
            {
                "name": "move_chat",
                "description": "Move a chat to a different folder.",
                "parameters": {"chat_id": "string", "target_folder": "string"}
            },
            
            # Memory Tools
            {
                "name": "remember_fact",
                "description": "Store a learned fact in long-term memory.",
                "parameters": {"fact": "string", "category": "string (optional)", "confidence": "float (0-1)"}
            },
            {
                "name": "recall_facts",
                "description": "Recall facts from memory.",
                "parameters": {"query": "string (optional)", "category": "string (optional)"}
            },
            {
                "name": "remember_entity",
                "description": "Store info about a person, company, or project.",
                "parameters": {"name": "string", "entity_type": "string", "attributes": "object"}
            },
            {
                "name": "get_entity",
                "description": "Get stored info about an entity.",
                "parameters": {"name": "string", "entity_type": "string (optional)"}
            },
            {
                "name": "memory_stats",
                "description": "Get memory system statistics.",
                "parameters": {}
            },
            
            # Extractor Tools
            {
                "name": "extract_entities",
                "description": "Extract people, companies, dates, amounts from text.",
                "parameters": {"text": "string"}
            },
            {
                "name": "analyze_sentiment",
                "description": "Analyze sentiment of text (positive/negative/neutral).",
                "parameters": {"text": "string"}
            },
            {
                "name": "summarize_text",
                "description": "Generate a summary of text.",
                "parameters": {"text": "string", "max_sentences": "integer (default: 5)"}
            },
            {
                "name": "extract_timeline",
                "description": "Extract events with dates from text.",
                "parameters": {"text": "string"}
            },
            {
                "name": "compare_documents",
                "description": "Compare two documents for differences.",
                "parameters": {"doc1": "string", "doc2": "string"}
            },
            
            # Agent Tools
            {
                "name": "analyze_intent",
                "description": "Analyze user intent and required tools.",
                "parameters": {"query": "string"}
            },
            {
                "name": "create_plan",
                "description": "Create execution plan for complex query.",
                "parameters": {"query": "string"}
            },
            {
                "name": "execute_plan",
                "description": "Execute a multi-step plan.",
                "parameters": {"plan": "object"}
            },
            {
                "name": "suggest_followups",
                "description": "Suggest follow-up questions.",
                "parameters": {"query": "string", "result": "any"}
            }
        ]

    # ═══════════════════════════════════════════════════════════════════════════
    # TOOL EXECUTOR
    # ═══════════════════════════════════════════════════════════════════════════

    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Dispatcher for tool execution."""
        
        # ─── Knowledge Base Tools ───────────────────────────────────────────────
        if tool_name == "search_knowledge_base":
            query = params.get("query", "")
            source = (params.get("source") or "all").lower()
            limit = int(params.get("limit", 10))

            if source in {"all", "*"}:
                sources = ["docs", "emails", "knowledge", "archives"]
            elif source in {"documents", "docs", "doc"}:
                sources = ["docs"]
            elif source in {"emails", "email"}:
                sources = ["emails"]
            elif source in {"knowledge", "kb", "strategic"}:
                sources = ["knowledge"]
            elif source in {"archives", "archive"}:
                sources = ["archives"]
            else:
                sources = ["docs", "emails", "knowledge", "archives"]

            return self.knowledge.search(query, limit=limit, sources=sources)
        
        elif tool_name == "read_document":
            path = params.get("file_path")
            content = self.storage.read_file(path)
            if content:
                try:
                    return content.decode('utf-8')
                except:
                    return f"[Binary Content: {len(content)} bytes]"
            return "File not found or unreadable."
        
        elif tool_name == "search_archives":
            query = params.get("query", "")
            tags = params.get("tags", [])
            limit = int(params.get("limit", 20))
            return self.knowledge.search_archives(query, tags, limit=limit)
        
        elif tool_name == "get_archive_summary":
            return self.knowledge.get_archive_summary()
        
        # ─── Web Search Tools ───────────────────────────────────────────────────
        elif tool_name == "web_search":
            query = params.get("query", "")
            max_results = params.get("max_results", 5)
            return self.web_search.search(query, max_results)
        
        elif tool_name == "search_industry_news":
            topic = params.get("topic", "mining")
            return self.web_search.search_industry(topic)
        
        # ─── Analysis Tools ─────────────────────────────────────────────────────
        elif tool_name == "deep_analyze":
            question = params.get("question", "")
            context = params.get("context", "")
            return self.analyzer.think_deeply(question, context)
        
        elif tool_name == "swot_analysis":
            topic = params.get("topic", "")
            return self.analyzer._swot_analysis(topic, "", None)
        
        elif tool_name == "risk_assessment":
            topic = params.get("topic", "")
            return self.analyzer._risk_analysis(topic, "", None)
        
        elif tool_name == "root_cause_analysis":
            problem = params.get("problem", "")
            return self.analyzer._root_cause_analysis(problem, "", None)
        
        # ─── Forecasting Tools ──────────────────────────────────────────────────
        elif tool_name == "forecast":
            return self.analyzer.project_future(
                metric=params.get("metric", "value"),
                current_value=float(params.get("current_value", 0)),
                growth_rate=float(params.get("growth_rate", 0.03)),
                periods=int(params.get("periods", 12))
            )
        
        elif tool_name == "calculate_growth":
            start = float(params.get("start_value", 0))
            end = float(params.get("end_value", 0))
            periods = int(params.get("periods", 1))
            if start == 0:
                return {"error": "Start value cannot be zero"}
            growth_rate = ((end / start) ** (1 / periods)) - 1
            return {
                "start_value": start,
                "end_value": end,
                "periods": periods,
                "growth_rate": f"{growth_rate * 100:.2f}%",
                "cagr": f"{growth_rate * 100:.2f}%"
            }
        
        elif tool_name == "calculate_roi":
            investment = float(params.get("investment", 0))
            returns = float(params.get("returns", 0))
            if investment == 0:
                return {"error": "Investment cannot be zero"}
            roi = ((returns - investment) / investment) * 100
            return {
                "investment": investment,
                "returns": returns,
                "roi": f"{roi:.2f}%",
                "profit": returns - investment
            }
        
        elif tool_name == "calculate_breakeven":
            fixed = float(params.get("fixed_costs", 0))
            variable = float(params.get("variable_cost", 0))
            price = float(params.get("price", 0))
            if price <= variable:
                return {"error": "Price must be greater than variable cost"}
            breakeven = fixed / (price - variable)
            return {
                "fixed_costs": fixed,
                "variable_cost_per_unit": variable,
                "price_per_unit": price,
                "breakeven_units": round(breakeven, 2),
                "breakeven_revenue": round(breakeven * price, 2)
            }
        
        # ─── Calculator ─────────────────────────────────────────────────────────
        elif tool_name == "calculator":
            try:
                expr = params.get("expression", "0")
                # Safe math operations
                allowed = "0123456789+-*/(). "
                if not all(c in allowed for c in str(expr)):
                    return {"error": "Invalid characters in expression"}
                result = eval(expr, {"__builtins__": None}, {"math": math})
                return {"expression": expr, "result": result}
            except Exception as e:
                return {"error": f"Math Error: {e}"}
        
        # ─── Chat Management Tools ──────────────────────────────────────────────
        elif tool_name == "list_chats":
            folder_id = params.get("folder_id")
            return self.chat_manager.list_chats(folder_id)
        
        elif tool_name == "get_chat_history":
            chat_id = params.get("chat_id", "")
            limit = int(params.get("limit", 20))
            return self.chat_manager.get_history(chat_id, limit)
        
        elif tool_name == "create_folder":
            folder_id = params.get("folder_id", "")
            name = params.get("name", "")
            return self.chat_manager.create_folder(folder_id, name)
        
        elif tool_name == "list_folders":
            return self.chat_manager.list_folders()
        
        elif tool_name == "move_chat":
            chat_id = params.get("chat_id", "")
            target = params.get("target_folder", "default")
            return self.chat_manager.move_chat(chat_id, target)
        
        # ─── Memory Tools ────────────────────────────────────────────────────────
        elif tool_name == "remember_fact":
            return self.memory.remember_fact(
                fact=params.get("fact", ""),
                category=params.get("category", "general"),
                confidence=float(params.get("confidence", 0.8))
            )
        
        elif tool_name == "recall_facts":
            return self.memory.recall_facts(
                query=params.get("query"),
                category=params.get("category"),
                limit=int(params.get("limit", 10))
            )
        
        elif tool_name == "remember_entity":
            return self.memory.remember_entity(
                name=params.get("name", ""),
                entity_type=params.get("entity_type", "unknown"),
                attributes=params.get("attributes", {})
            )
        
        elif tool_name == "get_entity":
            return self.memory.get_entity(
                name=params.get("name", ""),
                entity_type=params.get("entity_type")
            )
        
        elif tool_name == "memory_stats":
            return self.memory.get_stats()
        
        # ─── Extractor Tools ─────────────────────────────────────────────────────
        elif tool_name == "extract_entities":
            return self.extractors.extract_entities(params.get("text", ""))
        
        elif tool_name == "analyze_sentiment":
            return self.extractors.analyze_sentiment(params.get("text", ""))
        
        elif tool_name == "summarize_text":
            return self.extractors.summarize_text(
                text=params.get("text", ""),
                max_sentences=int(params.get("max_sentences", 5))
            )
        
        elif tool_name == "extract_timeline":
            return self.extractors.extract_timeline(params.get("text", ""))
        
        elif tool_name == "compare_documents":
            return self.extractors.compare_documents(
                doc1=params.get("doc1", ""),
                doc2=params.get("doc2", "")
            )
        
        # ─── Agent Tools ─────────────────────────────────────────────────────────
        elif tool_name == "analyze_intent":
            return self.agents.analyze_intent(params.get("query", ""))
        
        elif tool_name == "create_plan":
            return self.agents.create_execution_plan(params.get("query", ""))
        
        elif tool_name == "execute_plan":
            return self.agents.execute_plan(params.get("plan", {}), self.execute_tool)
        
        elif tool_name == "suggest_followups":
            return self.agents.suggest_follow_ups(
                query=params.get("query", ""),
                result=params.get("result")
            )
        
        # ─── Unknown Tool ───────────────────────────────────────────────────────
        return {"error": f"Unknown tool: {tool_name}"}

    # ═══════════════════════════════════════════════════════════════════════════
    # TOOL CATEGORIES
    # ═══════════════════════════════════════════════════════════════════════════

    def get_tool_categories(self) -> Dict[str, List[str]]:
        """Return tools organized by category."""
        return {
            "knowledge": [
                "search_knowledge_base", "read_document", 
                "search_archives", "get_archive_summary"
            ],
            "web": [
                "web_search", "search_industry_news"
            ],
            "analysis": [
                "deep_analyze", "swot_analysis", 
                "risk_assessment", "root_cause_analysis"
            ],
            "forecasting": [
                "forecast", "calculate_growth", 
                "calculate_roi", "calculate_breakeven"
            ],
            "utility": [
                "calculator"
            ],
            "chat": [
                "list_chats", "get_chat_history", 
                "create_folder", "list_folders", "move_chat"
            ],
            "memory": [
                "remember_fact", "recall_facts",
                "remember_entity", "get_entity", "memory_stats"
            ],
            "extractors": [
                "extract_entities", "analyze_sentiment",
                "summarize_text", "extract_timeline", "compare_documents"
            ],
            "agents": [
                "analyze_intent", "create_plan",
                "execute_plan", "suggest_followups"
            ]
        }
    
    def get_tool_count(self) -> int:
        """Return total number of available tools."""
        return len(self.list_available_tools())
