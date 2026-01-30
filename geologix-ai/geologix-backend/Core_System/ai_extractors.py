"""
GeoLogix AI - Intelligent Extractors
Entity extraction, sentiment analysis, summarization, and data parsing.
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class AIExtractors:
    """
    Extraction tools for documents and text.
    Provides entity extraction, sentiment analysis, and summarization.
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.currency_patterns = [
            (r'R\s?([\d,]+(?:\.\d{2})?)', 'ZAR'),
            (r'\$\s?([\d,]+(?:\.\d{2})?)', 'USD'),
            (r'€\s?([\d,]+(?:\.\d{2})?)', 'EUR'),
            (r'([\d,]+(?:\.\d{2})?)\s?(?:rand|ZAR)', 'ZAR'),
        ]
        self.date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}',
            r'\d{2}-\d{2}-\d{4}',
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}',
            r'\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}',
        ]
        self.positive_words = {'excellent', 'good', 'great', 'positive', 'success', 'profit', 
                               'growth', 'increase', 'improved', 'achievement', 'efficient',
                               'outstanding', 'exceeded', 'favorable', 'optimistic', 'strong'}
        self.negative_words = {'poor', 'bad', 'negative', 'loss', 'decline', 'decrease',
                               'failed', 'issue', 'problem', 'risk', 'concern', 'weak',
                               'below', 'adverse', 'unfavorable', 'disappointing', 'delay'}
    
    def extract_entities(self, text: str) -> Dict[str, List]:
        """Extract entities from text (people, companies, locations, amounts, dates)."""
        entities = {
            "people": [],
            "companies": [],
            "locations": [],
            "amounts": [],
            "dates": [],
            "emails": [],
            "phone_numbers": [],
            "percentages": []
        }
        
        # Extract emails
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        entities["emails"] = list(set(emails))
        
        # Extract phone numbers
        phones = re.findall(r'(?:\+27|0)\s?\d{2}\s?\d{3}\s?\d{4}', text)
        entities["phone_numbers"] = list(set(phones))
        
        # Extract monetary amounts
        for pattern, currency in self.currency_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                amount = match.replace(',', '')
                try:
                    entities["amounts"].append({
                        "value": float(amount),
                        "currency": currency,
                        "original": match
                    })
                except:
                    pass
        
        # Extract dates
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities["dates"].extend(matches)
        entities["dates"] = list(set(entities["dates"]))
        
        # Extract percentages
        percentages = re.findall(r'(\d+(?:\.\d+)?)\s?%', text)
        entities["percentages"] = [f"{p}%" for p in percentages]
        
        # Extract potential company names (words ending in Ltd, Pty, Inc, etc.)
        company_patterns = re.findall(
            r'([A-Z][A-Za-z\s&]+(?:Ltd|Pty|Inc|LLC|Corp|Company|Group|Mining|Holdings)\.?)',
            text
        )
        entities["companies"] = list(set([c.strip() for c in company_patterns]))
        
        # Extract potential person names (Title + Name pattern)
        name_patterns = re.findall(
            r'(?:Mr|Mrs|Ms|Dr|Prof)\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            text
        )
        entities["people"] = list(set(name_patterns))
        
        # Extract South African locations
        sa_locations = ['Johannesburg', 'Cape Town', 'Durban', 'Pretoria', 'Mpumalanga',
                        'Limpopo', 'Gauteng', 'KwaZulu-Natal', 'Witbank', 'Middelburg',
                        'Secunda', 'Ermelo', 'Belfast', 'Nelspruit']
        found_locations = [loc for loc in sa_locations if loc.lower() in text.lower()]
        entities["locations"] = found_locations
        
        return entities
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text."""
        text_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', text_lower))
        
        positive_count = len(words & self.positive_words)
        negative_count = len(words & self.negative_words)
        total = positive_count + negative_count
        
        if total == 0:
            sentiment = "neutral"
            score = 0.0
            confidence = 0.3
        else:
            score = (positive_count - negative_count) / total
            confidence = min(0.5 + (total * 0.05), 0.95)
            if score > 0.2:
                sentiment = "positive"
            elif score < -0.2:
                sentiment = "negative"
            else:
                sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "score": round(score, 2),
            "confidence": round(confidence, 2),
            "positive_indicators": positive_count,
            "negative_indicators": negative_count,
            "analysis": self._get_sentiment_summary(sentiment, score)
        }
    
    def _get_sentiment_summary(self, sentiment: str, score: float) -> str:
        """Generate sentiment summary."""
        if sentiment == "positive":
            return f"Document has positive tone (score: {score:.2f}). Contains favorable language indicating good performance or outcomes."
        elif sentiment == "negative":
            return f"Document has negative tone (score: {score:.2f}). Contains concerning language indicating issues or challenges."
        return f"Document has neutral tone (score: {score:.2f}). Balanced or factual language without strong sentiment."
    
    def summarize_text(self, text: str, max_sentences: int = 5) -> Dict:
        """Generate a summary of the text."""
        if self.llm_client:
            return self._summarize_with_llm(text, max_sentences)

        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if not sentences:
            return {"summary": "Text too short to summarize.", "key_points": []}
        
        # Score sentences by importance
        scored = []
        for i, sentence in enumerate(sentences):
            score = 0
            # Position bonus (first and last sentences often important)
            if i == 0:
                score += 2
            if i == len(sentences) - 1:
                score += 1
            # Length bonus (medium length preferred)
            word_count = len(sentence.split())
            if 10 <= word_count <= 30:
                score += 1
            # Keyword bonus
            important_words = ['important', 'significant', 'key', 'critical', 'main',
                             'total', 'result', 'conclusion', 'recommend', 'decision']
            for word in important_words:
                if word in sentence.lower():
                    score += 1
            # Number bonus (sentences with data often important)
            if re.search(r'\d+', sentence):
                score += 1
            scored.append((score, i, sentence))
        
        # Get top sentences maintaining order
        scored.sort(reverse=True)
        top_indices = sorted([s[1] for s in scored[:max_sentences]])
        summary_sentences = [sentences[i] for i in top_indices]
        
        # Extract key points
        key_points = []
        for sentence in summary_sentences[:3]:
            if len(sentence) > 100:
                key_points.append(sentence[:100] + "...")
            else:
                key_points.append(sentence)
        
        return {
            "summary": ". ".join(summary_sentences) + ".",
            "key_points": key_points,
            "original_length": len(text),
            "summary_length": len(". ".join(summary_sentences)),
            "compression_ratio": round(len(". ".join(summary_sentences)) / len(text), 2) if text else 0
        }

    def _summarize_with_llm(self, text: str, max_sentences: int) -> Dict:
        """Summarize using LLM."""
        prompt = f"""
        Provide a concise summary of the following text in {max_sentences} sentences or less.
        Also list 3-5 key bullet points.
        
        TEXT:
        {text[:4000]}
        
        OUTPUT FORMAT (JSON):
        {{
            "summary": "The concise summary paragraph.",
            "key_points": ["point 1", "point 2", "point 3"]
        }}
        """
        response = self.llm_client.chat(prompt, system_prompt="You are an expert summarizer. Output only valid JSON.")
        try:
            # Clean response
            json_str = response.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:-3]
            result = json.loads(json_str)
            return {
                "summary": result.get("summary", ""),
                "key_points": result.get("key_points", []),
                "original_length": len(text),
                "summary_length": len(result.get("summary", "")),
                "compression_ratio": round(len(result.get("summary", "")) / len(text), 2) if text else 0
            }
        except:
             # Fallback to simple extraction if LLM fails
            sentences = re.split(r'[.!?]+', text)
            return {"summary": text[:200] + "...", "key_points": [], "error": "LLM summarization failed"}
    
    def extract_timeline(self, text: str) -> List[Dict]:
        """Extract events with dates from text."""
        timeline = []
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            for pattern in self.date_patterns:
                dates = re.findall(pattern, sentence, re.IGNORECASE)
                if dates:
                    timeline.append({
                        "date": dates[0],
                        "event": sentence.strip()[:200],
                        "extracted_at": datetime.now().isoformat()
                    })
                    break
        
        return timeline
    
    def extract_metrics(self, text: str) -> List[Dict]:
        """Extract numerical metrics from text."""
        metrics = []
        
        # Pattern: "metric name: value" or "metric name is value"
        patterns = [
            r'([A-Za-z\s]+):\s*(R?\$?€?[\d,]+(?:\.\d+)?%?)',
            r'([A-Za-z\s]+)\s+(?:is|was|were|are)\s+(R?\$?€?[\d,]+(?:\.\d+)?%?)',
            r'([A-Za-z\s]+)\s+of\s+(R?\$?€?[\d,]+(?:\.\d+)?%?)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                name = match[0].strip()
                value = match[1].strip()
                if len(name) > 3 and len(name) < 50:
                    metrics.append({
                        "name": name,
                        "value": value,
                        "raw": f"{name}: {value}"
                    })
        
        return metrics[:20]  # Limit results
    
    def compare_documents(self, doc1: str, doc2: str) -> Dict:
        """Compare two documents and identify differences."""
        # Extract entities from both
        entities1 = self.extract_entities(doc1)
        entities2 = self.extract_entities(doc2)
        
        # Extract metrics
        metrics1 = {m["name"].lower(): m["value"] for m in self.extract_metrics(doc1)}
        metrics2 = {m["name"].lower(): m["value"] for m in self.extract_metrics(doc2)}
        
        # Sentiment comparison
        sent1 = self.analyze_sentiment(doc1)
        sent2 = self.analyze_sentiment(doc2)
        
        # Find differences
        comparison = {
            "document_1": {
                "length": len(doc1),
                "sentiment": sent1["sentiment"],
                "entities_count": sum(len(v) for v in entities1.values()),
                "metrics_count": len(metrics1)
            },
            "document_2": {
                "length": len(doc2),
                "sentiment": sent2["sentiment"],
                "entities_count": sum(len(v) for v in entities2.values()),
                "metrics_count": len(metrics2)
            },
            "common_entities": {
                "companies": list(set(entities1["companies"]) & set(entities2["companies"])),
                "people": list(set(entities1["people"]) & set(entities2["people"])),
                "dates": list(set(entities1["dates"]) & set(entities2["dates"]))
            },
            "metric_changes": {},
            "sentiment_change": sent2["score"] - sent1["score"]
        }
        
        # Compare metrics
        common_metrics = set(metrics1.keys()) & set(metrics2.keys())
        for metric in common_metrics:
            comparison["metric_changes"][metric] = {
                "before": metrics1[metric],
                "after": metrics2[metric]
            }
        
        return comparison
