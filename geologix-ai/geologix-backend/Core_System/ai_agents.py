"""
GeoLogix AI - Intelligent Agents
Auto tool chaining, task decomposition, and multi-step reasoning.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import re


class AIAgents:
    """
    Intelligent agent system for complex task execution.
    Handles tool chaining, task decomposition, and multi-step workflows.
    """
    
    def __init__(self, tools_instance=None):
        self.tools = tools_instance
        self.execution_history = []
        self.task_templates = self._load_task_templates()
    
    def _load_task_templates(self) -> Dict:
        """Load predefined task templates."""
        return {
            "financial_analysis": {
                "description": "Complete financial analysis workflow",
                "steps": [
                    {"tool": "search_knowledge_base", "params": {"source": "documents"}, "extract": "query"},
                    {"tool": "deep_analyze", "params": {}, "extract": "question"},
                    {"tool": "forecast", "params": {"periods": 12}, "extract": "metric,current_value"}
                ]
            },
            "document_review": {
                "description": "Review and summarize a document",
                "steps": [
                    {"tool": "read_document", "params": {}, "extract": "file_path"},
                    {"tool": "summarize_text", "params": {}},
                    {"tool": "extract_entities", "params": {}}
                ]
            },
            "competitive_analysis": {
                "description": "Analyze competition and market",
                "steps": [
                    {"tool": "web_search", "params": {"max_results": 10}},
                    {"tool": "search_industry_news", "params": {}},
                    {"tool": "swot_analysis", "params": {}}
                ]
            },
            "risk_review": {
                "description": "Comprehensive risk assessment",
                "steps": [
                    {"tool": "search_knowledge_base", "params": {"source": "all"}},
                    {"tool": "risk_assessment", "params": {}},
                    {"tool": "deep_analyze", "params": {}}
                ]
            }
        }
    
    def analyze_intent(self, query: str) -> Dict:
        """Analyze user intent and determine required actions."""
        query_lower = query.lower()
        
        intents = []
        required_tools = []
        confidence = 0.5
        
        # Financial intent
        if any(w in query_lower for w in ['cost', 'revenue', 'profit', 'budget', 'financial', 'money', 'expense']):
            intents.append("financial_analysis")
            required_tools.extend(["search_knowledge_base", "deep_analyze", "calculator"])
            confidence += 0.1
        
        # Forecasting intent
        if any(w in query_lower for w in ['forecast', 'predict', 'future', 'projection', 'next']):
            intents.append("forecasting")
            required_tools.extend(["forecast", "deep_analyze"])
            confidence += 0.1
        
        # Search intent
        if any(w in query_lower for w in ['find', 'search', 'look', 'show', 'list', 'where']):
            intents.append("search")
            required_tools.append("search_knowledge_base")
            confidence += 0.1
        
        # Analysis intent
        if any(w in query_lower for w in ['analyze', 'analysis', 'review', 'assess', 'evaluate']):
            intents.append("deep_analysis")
            required_tools.append("deep_analyze")
            confidence += 0.1
        
        # Comparison intent
        if any(w in query_lower for w in ['compare', 'versus', 'difference', 'between']):
            intents.append("comparison")
            required_tools.extend(["search_knowledge_base", "compare_documents"])
            confidence += 0.1
        
        # Risk intent
        if any(w in query_lower for w in ['risk', 'threat', 'danger', 'vulnerability', 'issue']):
            intents.append("risk_assessment")
            required_tools.append("risk_assessment")
            confidence += 0.1
        
        # Web search intent
        if any(w in query_lower for w in ['current', 'latest', 'news', 'market', 'today']):
            intents.append("web_search")
            required_tools.append("web_search")
            confidence += 0.1
        
        # Summary intent
        if any(w in query_lower for w in ['summarize', 'summary', 'brief', 'overview']):
            intents.append("summarization")
            required_tools.append("summarize_text")
            confidence += 0.1
        
        return {
            "query": query,
            "intents": intents if intents else ["general"],
            "required_tools": list(set(required_tools)),
            "confidence": min(confidence, 0.95),
            "suggested_workflow": self._suggest_workflow(intents),
            "complexity": "high" if len(required_tools) > 2 else "medium" if len(required_tools) > 1 else "low"
        }
    
    def _suggest_workflow(self, intents: List[str]) -> Optional[str]:
        """Suggest a predefined workflow based on intents."""
        if "financial_analysis" in intents:
            return "financial_analysis"
        if "risk_assessment" in intents:
            return "risk_review"
        if "comparison" in intents:
            return "document_review"
        return None
    
    def create_execution_plan(self, query: str, intent_analysis: Dict = None) -> Dict:
        """Create a step-by-step execution plan for a query."""
        if not intent_analysis:
            intent_analysis = self.analyze_intent(query)
        
        steps = []
        step_num = 1
        
        # Always start with understanding
        steps.append({
            "step": step_num,
            "action": "understand_query",
            "description": "Parse and understand user request",
            "tool": None,
            "status": "pending"
        })
        step_num += 1
        
        # Add search if needed
        if any(t in intent_analysis["required_tools"] for t in ["search_knowledge_base", "web_search"]):
            if "search_knowledge_base" in intent_analysis["required_tools"]:
                steps.append({
                    "step": step_num,
                    "action": "search_internal",
                    "description": "Search company knowledge base",
                    "tool": "search_knowledge_base",
                    "params": {"query": query, "source": "all"},
                    "status": "pending"
                })
                step_num += 1
            
            if "web_search" in intent_analysis["required_tools"]:
                steps.append({
                    "step": step_num,
                    "action": "search_web",
                    "description": "Search internet for current info",
                    "tool": "web_search",
                    "params": {"query": query},
                    "status": "pending"
                })
                step_num += 1
        
        # Add analysis
        if "deep_analyze" in intent_analysis["required_tools"]:
            steps.append({
                "step": step_num,
                "action": "analyze",
                "description": "Perform deep analysis",
                "tool": "deep_analyze",
                "params": {"question": query},
                "status": "pending"
            })
            step_num += 1
        
        # Add forecasting
        if "forecast" in intent_analysis["required_tools"]:
            steps.append({
                "step": step_num,
                "action": "forecast",
                "description": "Generate projections",
                "tool": "forecast",
                "status": "pending"
            })
            step_num += 1
        
        # Add risk assessment
        if "risk_assessment" in intent_analysis["required_tools"]:
            steps.append({
                "step": step_num,
                "action": "assess_risk",
                "description": "Evaluate risks",
                "tool": "risk_assessment",
                "params": {"topic": query},
                "status": "pending"
            })
            step_num += 1
        
        # Always end with synthesis
        steps.append({
            "step": step_num,
            "action": "synthesize",
            "description": "Combine results into response",
            "tool": None,
            "status": "pending"
        })
        
        return {
            "query": query,
            "intent_analysis": intent_analysis,
            "steps": steps,
            "total_steps": len(steps),
            "estimated_time": f"{len(steps) * 2}-{len(steps) * 5} seconds",
            "created": datetime.now().isoformat()
        }
    
    def execute_plan(self, plan: Dict, tools_executor=None) -> Dict:
        """Execute a plan step by step."""
        results = {
            "plan_id": plan.get("created"),
            "query": plan.get("query"),
            "steps_executed": [],
            "final_result": None,
            "status": "in_progress"
        }
        
        executor = tools_executor or (self.tools.execute_tool if self.tools else None)
        collected_data = {}
        
        for step in plan["steps"]:
            step_result = {
                "step": step["step"],
                "action": step["action"],
                "status": "pending"
            }
            
            try:
                if step.get("tool") and executor:
                    params = step.get("params", {})
                    # Inject context from previous steps
                    if "context" not in params and collected_data:
                        params["context"] = str(collected_data)[:1000]
                    
                    tool_result = executor(step["tool"], params)
                    step_result["result"] = tool_result
                    step_result["status"] = "completed"
                    
                    # Store for later steps
                    collected_data[step["action"]] = tool_result
                else:
                    step_result["status"] = "skipped"
                    step_result["note"] = "No tool or executor"
                    
            except Exception as e:
                step_result["status"] = "error"
                step_result["error"] = str(e)
            
            results["steps_executed"].append(step_result)
        
        results["status"] = "completed"
        results["collected_data"] = collected_data
        results["completed_at"] = datetime.now().isoformat()
        
        self.execution_history.append(results)
        return results
    
    def get_execution_history(self, limit: int = 10) -> List[Dict]:
        """Get recent execution history."""
        return self.execution_history[-limit:]
    
    def suggest_follow_ups(self, query: str, result: Any) -> List[str]:
        """Suggest follow-up questions based on query and result."""
        query_lower = query.lower()
        suggestions = []
        
        if any(w in query_lower for w in ['cost', 'expense', 'budget']):
            suggestions.extend([
                "What are the main cost drivers?",
                "How does this compare to last year?",
                "What cost reduction opportunities exist?"
            ])
        
        if any(w in query_lower for w in ['revenue', 'sales', 'income']):
            suggestions.extend([
                "What's the revenue forecast for next quarter?",
                "Which segments are performing best?",
                "What factors affect revenue growth?"
            ])
        
        if any(w in query_lower for w in ['risk', 'issue', 'problem']):
            suggestions.extend([
                "What mitigation strategies are available?",
                "What's the probability of occurrence?",
                "What would be the business impact?"
            ])
        
        if any(w in query_lower for w in ['forecast', 'predict', 'future']):
            suggestions.extend([
                "What assumptions drive this forecast?",
                "What's the best/worst case scenario?",
                "How confident are we in these projections?"
            ])
        
        # Default suggestions
        if not suggestions:
            suggestions = [
                "Can you provide more details?",
                "What are the key takeaways?",
                "What action should we take?"
            ]
        
        return suggestions[:3]
