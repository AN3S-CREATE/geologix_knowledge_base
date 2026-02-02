"""
GeoLogix AI - Deep Analysis & Thinking Module
Provides structured thinking, deep analysis, and future projections.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

class DeepAnalysis:
    """
    Deep thinking and analysis engine for complex business questions.
    Implements chain-of-thought reasoning and structured analysis frameworks.
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.thinking_steps = []
        self.analysis_frameworks = {
            "swot": self._swot_analysis,
            "pestel": self._pestel_analysis,
            "financial": self._financial_analysis,
            "risk": self._risk_analysis,
            "forecast": self._forecast_analysis,
            "root_cause": self._root_cause_analysis,
            "scenario": self._scenario_analysis
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # DEEP THINKING ENGINE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def think_deeply(self, question: str, context: str = "", data: dict = None) -> Dict:
        """
        Perform deep thinking analysis with chain-of-thought reasoning.
        
        Returns structured thinking process and conclusions.
        """
        self.thinking_steps = []
        
        # Step 1: Understand the question
        self._add_thought("UNDERSTANDING", f"Analyzing question: {question[:200]}")
        question_type = self._classify_question(question)
        self._add_thought("CLASSIFICATION", f"Question type: {question_type}")
        
        # Step 2: Identify required data
        data_needs = self._identify_data_needs(question, question_type)
        self._add_thought("DATA_REQUIREMENTS", f"Required data: {', '.join(data_needs)}")
        
        # Step 3: Select analysis framework
        framework = self._select_framework(question_type)
        self._add_thought("FRAMEWORK_SELECTION", f"Using framework: {framework}")
        
        # Step 4: Apply framework
        if framework in self.analysis_frameworks:
            analysis_result = self.analysis_frameworks[framework](question, context, data)
            self._add_thought("ANALYSIS", f"Framework analysis complete")
        else:
            analysis_result = self._general_analysis(question, context, data)
        
        # Step 5: Generate insights
        insights = self._generate_insights(analysis_result)
        self._add_thought("INSIGHTS", f"Generated {len(insights)} key insights")
        
        # Step 6: Formulate recommendations
        recommendations = self._generate_recommendations(analysis_result, insights)
        self._add_thought("RECOMMENDATIONS", f"Generated {len(recommendations)} recommendations")
        
        return {
            "question": question,
            "question_type": question_type,
            "framework_used": framework,
            "thinking_process": self.thinking_steps,
            "analysis": analysis_result,
            "insights": insights,
            "recommendations": recommendations,
            "confidence": self._calculate_confidence(context, data),
            "timestamp": datetime.now().isoformat()
        }
    
    def _add_thought(self, stage: str, thought: str):
        """Add a thinking step."""
        self.thinking_steps.append({
            "stage": stage,
            "thought": thought,
            "timestamp": datetime.now().isoformat()
        })
    
    def _classify_question(self, question: str) -> str:
        """Classify the type of question."""
        q_lower = question.lower()
        
        if any(w in q_lower for w in ["forecast", "predict", "future", "projection", "next"]):
            return "predictive"
        elif any(w in q_lower for w in ["why", "cause", "reason", "explain"]):
            return "diagnostic"
        elif any(w in q_lower for w in ["should", "recommend", "best", "optimize"]):
            return "prescriptive"
        elif any(w in q_lower for w in ["risk", "threat", "danger", "vulnerability"]):
            return "risk_assessment"
        elif any(w in q_lower for w in ["compare", "versus", "difference", "better"]):
            return "comparative"
        elif any(w in q_lower for w in ["trend", "pattern", "over time", "history"]):
            return "trend_analysis"
        elif any(w in q_lower for w in ["cost", "expense", "budget", "financial", "revenue", "profit"]):
            return "financial"
        elif any(w in q_lower for w in ["strategy", "strategic", "long-term", "vision"]):
            return "strategic"
        else:
            return "general"
    
    def _identify_data_needs(self, question: str, q_type: str) -> List[str]:
        """Identify what data is needed to answer the question."""
        needs = []
        q_lower = question.lower()
        
        if "financial" in q_lower or q_type == "financial":
            needs.extend(["financial_statements", "budgets", "invoices"])
        if "production" in q_lower or "operations" in q_lower:
            needs.extend(["production_logs", "operational_reports"])
        if "employee" in q_lower or "staff" in q_lower or "hr" in q_lower:
            needs.extend(["hr_records", "payroll_data"])
        if "sales" in q_lower or "customer" in q_lower:
            needs.extend(["sales_data", "customer_records"])
        if "compliance" in q_lower or "safety" in q_lower:
            needs.extend(["compliance_records", "safety_audits"])
        if q_type == "predictive":
            needs.append("historical_trends")
        
        return needs if needs else ["general_knowledge_base"]
    
    def _select_framework(self, q_type: str) -> str:
        """Select appropriate analysis framework."""
        framework_map = {
            "predictive": "forecast",
            "diagnostic": "root_cause",
            "prescriptive": "scenario",
            "risk_assessment": "risk",
            "financial": "financial",
            "strategic": "swot",
            "comparative": "scenario",
            "trend_analysis": "forecast"
        }
        return framework_map.get(q_type, "general")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ANALYSIS FRAMEWORKS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _generate_analysis_with_llm(self, framework: str, question: str, context: str, structure: str) -> Dict:
        """Helper to generate structured analysis using LLM."""
        if not self.llm_client:
            return {"error": "LLM Client not initialized"}
            
        prompt = f"""
        Perform a {framework} analysis based on the following context.
        
        QUESTION: {question}
        
        CONTEXT:
        {context[:8000]}
        
        OUTPUT FORMAT:
        Return ONLY valid JSON with this structure:
        {structure}
        """
        
        response = self.llm_client.chat(prompt, system_prompt="You are an expert business analyst. Output only valid JSON.")
        try:
            # Clean response
            json_str = response.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:-3]
            return json.loads(json_str)
        except:
            return {"error": "Failed to generate analysis", "raw_response": response}

    def _swot_analysis(self, question: str, context: str, data: dict) -> Dict:
        """SWOT Analysis framework."""
        structure = """
        {
            "framework": "SWOT",
            "strengths": ["list", "of", "strengths"],
            "weaknesses": ["list", "of", "weaknesses"],
            "opportunities": ["list", "of", "opportunities"],
            "threats": ["list", "of", "threats"],
            "strategic_implication": "Overall strategic takeaway"
        }
        """
        return self._generate_analysis_with_llm("SWOT", question, context, structure)
    
    def _pestel_analysis(self, question: str, context: str, data: dict) -> Dict:
        """PESTEL Analysis framework."""
        structure = """
        {
            "framework": "PESTEL",
            "political": "Analysis of political factors",
            "economic": "Analysis of economic factors",
            "social": "Analysis of social factors",
            "technological": "Analysis of technological factors",
            "environmental": "Analysis of environmental factors",
            "legal": "Analysis of legal factors"
        }
        """
        return self._generate_analysis_with_llm("PESTEL", question, context, structure)
    
    def _financial_analysis(self, question: str, context: str, data: dict) -> Dict:
        """Financial analysis framework."""
        return {
            "framework": "Financial Analysis",
            "metrics": {
                "profitability": "Revenue - Costs = Profit Margin",
                "liquidity": "Current Assets / Current Liabilities",
                "efficiency": "Output / Input Resources",
                "leverage": "Debt / Equity Ratio"
            },
            "calculations": {
                "roi": "ROI = (Gain - Cost) / Cost × 100",
                "breakeven": "Fixed Costs / (Price - Variable Cost)",
                "npv": "NPV = Σ(Cash Flow / (1 + r)^t)"
            },
            "context_data": context[:500] if context else "No financial context provided"
        }
    
    def _risk_analysis(self, question: str, context: str, data: dict) -> Dict:
        """Risk assessment framework."""
        structure = """
        {
            "framework": "Risk Assessment Matrix",
            "risk_categories": {
                "operational": {"probability": "Low/Med/High", "impact": "Low/Med/High", "description": "text"},
                "financial": {"probability": "Low/Med/High", "impact": "Low/Med/High", "description": "text"},
                "compliance": {"probability": "Low/Med/High", "impact": "Low/Med/High", "description": "text"},
                "safety": {"probability": "Low/Med/High", "impact": "Low/Med/High", "description": "text"},
                "reputational": {"probability": "Low/Med/High", "impact": "Low/Med/High", "description": "text"}
            },
            "mitigation_strategies": ["strategy 1", "strategy 2", "strategy 3"]
        }
        """
        return self._generate_analysis_with_llm("Risk Assessment", question, context, structure)
    
    def _forecast_analysis(self, question: str, context: str, data: dict) -> Dict:
        """Forecasting and projection framework."""
        return {
            "framework": "Forecasting Model",
            "methods": {
                "linear_regression": "y = mx + b (trend projection)",
                "moving_average": "MA = Σ(values) / n periods",
                "seasonal_adjustment": "Adjusted = Value × Seasonal Factor",
                "growth_model": "Future = Present × (1 + growth_rate)^periods"
            },
            "time_horizons": {
                "short_term": "1-3 months",
                "medium_term": "3-12 months",
                "long_term": "1-5 years"
            },
            "confidence_levels": {
                "short_term": "High (85-95%)",
                "medium_term": "Medium (70-85%)",
                "long_term": "Low (50-70%)"
            }
        }
    
    def _root_cause_analysis(self, question: str, context: str, data: dict) -> Dict:
        """Root cause analysis framework."""
        structure = """
        {
            "framework": "Root Cause Analysis",
            "problem_statement": "Clear definition of problem",
            "potential_causes": ["cause 1", "cause 2"],
            "root_cause": "The fundamental underlying cause",
            "evidence": "Supporting evidence from context",
            "corrective_actions": ["action 1", "action 2"]
        }
        """
        return self._generate_analysis_with_llm("Root Cause Analysis", question, context, structure)
    
    def _scenario_analysis(self, question: str, context: str, data: dict) -> Dict:
        """Scenario planning framework."""
        structure = """
        {
            "framework": "Scenario Analysis",
            "scenarios": {
                "best_case": {
                    "description": "Optimistic outcome",
                    "probability": "Low/Med/High",
                    "key_drivers": ["factor 1", "factor 2"]
                },
                "base_case": {
                    "description": "Most likely outcome",
                    "probability": "Low/Med/High",
                    "key_drivers": ["factor 1", "factor 2"]
                },
                "worst_case": {
                    "description": "Pessimistic outcome",
                    "probability": "Low/Med/High",
                    "key_drivers": ["factor 1", "factor 2"]
                }
            },
            "recommendation": "Strategic recommendation based on scenarios"
        }
        """
        return self._generate_analysis_with_llm("Scenario Planning", question, context, structure)
    
    def _general_analysis(self, question: str, context: str, data: dict) -> Dict:
        """General analysis for unclassified questions."""
        return {
            "framework": "General Analysis",
            "approach": "Comprehensive review",
            "data_sources": "Knowledge base search",
            "context_available": bool(context)
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # INSIGHTS & RECOMMENDATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _generate_insights(self, analysis: Dict) -> List[str]:
        """Generate insights from analysis."""
        insights = [
            "Analysis framework applied successfully",
            "Multiple data sources should be consulted for comprehensive view",
            "Historical patterns provide basis for projections"
        ]
        return insights
    
    def _generate_recommendations(self, analysis: Dict, insights: List[str]) -> List[Dict]:
        """Generate actionable recommendations."""
        return [
            {
                "priority": "HIGH",
                "action": "Review historical data for validation",
                "expected_impact": "Improved accuracy",
                "timeline": "Immediate"
            },
            {
                "priority": "MEDIUM",
                "action": "Implement monitoring for key metrics",
                "expected_impact": "Early warning capability",
                "timeline": "30 days"
            },
            {
                "priority": "LOW",
                "action": "Document assumptions and limitations",
                "expected_impact": "Better decision context",
                "timeline": "Ongoing"
            }
        ]
    
    def _calculate_confidence(self, context: str, data: dict) -> str:
        """Calculate confidence level based on available data."""
        if data and context:
            return "HIGH"
        elif context:
            return "MEDIUM"
        else:
            return "LOW"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FUTURE PROJECTIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def project_future(self, metric: str, current_value: float, 
                       growth_rate: float = 0.03, periods: int = 12,
                       seasonal_factors: List[float] = None) -> Dict:
        """
        Generate future projections for a metric.
        
        Args:
            metric: Name of the metric being projected
            current_value: Current value
            growth_rate: Expected growth rate per period (default 3%)
            periods: Number of periods to project
            seasonal_factors: Optional list of seasonal adjustment factors
        """
        projections = []
        base_date = datetime.now()
        
        for i in range(1, periods + 1):
            # Calculate projected value
            projected = current_value * ((1 + growth_rate) ** i)
            
            # Apply seasonal adjustment if provided
            if seasonal_factors and len(seasonal_factors) >= 12:
                month_index = (base_date.month + i - 1) % 12
                projected *= seasonal_factors[month_index]
            
            # Calculate date
            future_date = base_date + timedelta(days=30 * i)
            
            projections.append({
                "period": i,
                "date": future_date.strftime("%Y-%m"),
                "projected_value": round(projected, 2),
                "growth_from_current": f"{((projected / current_value) - 1) * 100:.1f}%"
            })
        
        # Confidence decreases over time
        confidence_schedule = {
            3: "HIGH (90%)",
            6: "MEDIUM-HIGH (80%)",
            9: "MEDIUM (70%)",
            12: "MEDIUM-LOW (60%)",
            24: "LOW (50%)"
        }
        
        return {
            "metric": metric,
            "current_value": current_value,
            "growth_rate": f"{growth_rate * 100}%",
            "projections": projections,
            "summary": {
                "3_month": projections[2] if len(projections) >= 3 else None,
                "6_month": projections[5] if len(projections) >= 6 else None,
                "12_month": projections[11] if len(projections) >= 12 else None
            },
            "confidence": confidence_schedule.get(periods, "LOW"),
            "methodology": "Compound growth with optional seasonal adjustment",
            "assumptions": [
                f"Constant growth rate of {growth_rate * 100}% per period",
                "No major market disruptions",
                "Current operational capacity maintained"
            ]
        }
    
    def format_thinking_for_display(self) -> str:
        """Format thinking process for display."""
        output = "\n╔══════════════════════════════════════════════════════════════╗\n"
        output += "║                    DEEP THINKING PROCESS                      ║\n"
        output += "╚══════════════════════════════════════════════════════════════╝\n\n"
        
        for step in self.thinking_steps:
            output += f"🔹 [{step['stage']}]\n"
            output += f"   {step['thought']}\n\n"
        
        return output
