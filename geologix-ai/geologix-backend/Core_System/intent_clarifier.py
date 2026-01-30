"""
Intent Clarification & Confidence Scoring System
Handles ambiguous queries and generates clarification questions with options.
"""

from typing import Dict, List, Optional, Tuple


class IntentClarifier:
    """Analyzes query ambiguity and generates clarification questions."""
    
    def __init__(self):
        self.confidence_threshold = 0.6  # Lowered from 0.7 to reduce false positives
        
    def calculate_intent_confidence(self, user_query: str, detected_intents: List[str]) -> float:
        """
        Calculate confidence score for intent detection (0.0 to 1.0).
        
        Returns:
            float: Confidence score (1.0 = very confident, 0.0 = very uncertain)
        """
        query_lower = user_query.lower()
        query_words = query_lower.split()
        
        # Start with base confidence
        confidence = 0.5
        
        # HIGH CONFIDENCE for complete analytical queries
        analytical_patterns = ['analyze', 'analysis', 'report', 'forecast', 'evaluate', 'assess']
        if any(pattern in query_lower for pattern in analytical_patterns) and len(query_words) >= 5:
            confidence += 0.4  # Strong boost for analytical queries
        
        # Increase confidence for clear patterns
        clear_indicators = {
            'list': ['list all', 'show all', 'index', 'show me all'],
            'retrieve': ['get the', 'retrieve', 'open the', 'show me the', 'give me info', 'tell me about'],
            'search': ['search for', 'find all', 'look for', 'information about'],
            'analyze': ['analyze', 'analysis', 'evaluate', 'assess', 'report', 'explain'],
            'forecast': ['forecast', 'predict', 'project'],
        }
        
        # Check for strong matches
        for intent, patterns in clear_indicators.items():
            if intent in detected_intents:
                for pattern in patterns:
                    if pattern in query_lower:
                        confidence += 0.2
                        break
        
        # Decrease confidence for ambiguous queries
        ambiguous_signs = [
            '?' not in user_query and len(query_words) >= 20,  # Very long without question mark
            query_lower.startswith(('um', 'uh', 'like', 'maybe', 'i think')),  # Uncertain language
        ]
        
        for sign in ambiguous_signs:
            if sign:
                confidence -= 0.15

        # Handle short queries (Keyword Search Assumption)
        if len(query_words) <= 3 and '?' not in user_query:
            # Assume it's a search term (e.g. "Peter Nordin", "invoice", "sales plan")
            confidence += 0.2
        
        # Increase confidence for specific entities
        if any(word in query_lower for word in ['email', 'document', 'contract', 'invoice', 'report']):
            confidence += 0.15  # Increased from 0.1
        
        # STRONG confidence for complete sentences with clear goals
        goal_indicators = ['improve', 'create', 'generate', 'show', 'find', 'get']
        if any(goal in query_lower for goal in goal_indicators) and len(query_words) >= 4:
            confidence += 0.1
        
        # Cap between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def detect_ambiguity(self, user_query: str) -> Dict:
        """
        Detect if query is ambiguous and what type of ambiguity.
        
        Returns:
            Dict with:
                - is_ambiguous: bool
                - ambiguity_type: str (vague, multiple_intents, missing_info, unclear)
                - suggestions: List[str]
        """
        query_lower = user_query.lower()
        words = query_lower.split()
        
        # SKIP ambiguity check for complete analytical queries
        analytical_keywords = ['analyze', 'analysis', 'report', 'forecast', 'evaluate', 'assess', 'review']
        if any(kw in query_lower for kw in analytical_keywords) and len(words) >= 5:
            return {
                'is_ambiguous': False,
                'ambiguity_type': None,
                'reason': 'Complete analytical query'
            }
            
        # SKIP ambiguity check for greetings and conversation
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'how are you', 'howdy', 'greetings', 'thanks', 'thank you']
        if any(greet in query_lower for greet in greetings) or (len(words) < 10 and '?' in user_query and not any(kw in query_lower for kw in ['find', 'search', 'get', 'list'])):
             return {
                'is_ambiguous': False,
                'ambiguity_type': None,
                'reason': 'Conversational query'
            }
        
        # Vague pronouns without context
        if any(word in words for word in ['it', 'that', 'this', 'them', 'those']) and len(words) <= 5:
            return {
                'is_ambiguous': True,
                'ambiguity_type': 'vague_reference',
                'reason': 'Query uses pronouns without clear reference'
            }
        
        # Multiple possible intents
        intent_keywords = {
            'list': ['list', 'show', 'all'],
            'search': ['search', 'find', 'look'],
            'analyze': ['analyze', 'analysis'],
            'get': ['get', 'retrieve', 'open']
        }
        
        detected = []
        for intent, keywords in intent_keywords.items():
            if any(kw in query_lower for kw in keywords):
                detected.append(intent)
        
        if len(detected) >= 2 and len(words) <= 6:
            return {
                'is_ambiguous': True,
                'ambiguity_type': 'multiple_intents',
                'reason': f'Could mean: {", ".join(detected)}'
            }
        
        # Missing critical information
        action_verbs = ['show', 'get', 'find', 'list', 'analyze']
        has_action = any(verb in query_lower for verb in action_verbs)
        has_object = any(obj in query_lower for obj in ['email', 'document', 'file', 'report', 'contract', 'invoice'])
        
        if has_action and not has_object and len(words) <= 4:
            return {
                'is_ambiguous': True,
                'ambiguity_type': 'missing_object',
                'reason': 'Action specified but object unclear'
            }
        
        # Very short, unclear queries
        if len(words) <= 2 and '?' in user_query:
            return {
                'is_ambiguous': True,
                'ambiguity_type': 'too_vague',
                'reason': 'Query too short to determine intent'
            }
        
        return {
            'is_ambiguous': False,
            'ambiguity_type': None,
            'reason': None
        }
    
    def generate_clarification_options(self, user_query: str, ambiguity_info: Dict) -> Dict:
        """
        Generate multiple-choice clarification question from ambiguous query.
        
        Returns:
            Dict with:
                - question: str
                - options: List[Dict] with 'letter', 'text', 'intent'
                - suggested_response: str
        """
        ambiguity_type = ambiguity_info.get('ambiguity_type')
        query_lower = user_query.lower()
        
        if ambiguity_type == 'vague_reference':
            return {
                'question': "I want to help, but I'm not sure what you're referring to. What would you like me to do?",
                'options': [
                    {'letter': 'A', 'text': 'List all emails', 'intent': 'list_emails'},
                    {'letter': 'B', 'text': 'List all documents', 'intent': 'list_documents'},
                    {'letter': 'C', 'text': 'Search for something specific', 'intent': 'search'},
                    {'letter': 'D', 'text': 'Analyze business data', 'intent': 'analyze'},
                ],
                'suggested_response': 'reply with A, B, C, or D'
            }
        
        elif ambiguity_type == 'multiple_intents':
            # Extract what they might want
            options = []
            if 'email' in query_lower or 'mail' in query_lower:
                options.append({'letter': 'A', 'text': 'List all emails', 'intent': 'list_emails'})
                options.append({'letter': 'B', 'text': 'Search for specific emails', 'intent': 'search_emails'})
                options.append({'letter': 'C', 'text': 'Retrieve a specific email', 'intent': 'retrieve_email'})
            elif 'document' in query_lower or 'file' in query_lower:
                options.append({'letter': 'A', 'text': 'List all documents', 'intent': 'list_documents'})
                options.append({'letter': 'B', 'text': 'Search for specific documents', 'intent': 'search_documents'})
                options.append({'letter': 'C', 'text': 'Retrieve a specific document', 'intent': 'retrieve_document'})
            else:
                options.append({'letter': 'A', 'text': 'Show me a list/index', 'intent': 'list'})
                options.append({'letter': 'B', 'text': 'Search for something', 'intent': 'search'})
                options.append({'letter': 'C', 'text': 'Get a specific item', 'intent': 'retrieve'})
            
            return {
                'question': f"I understand you want to work with data, but I'm not quite sure what you need. Could you clarify?",
                'options': options,
                'suggested_response': 'reply with the letter of your choice'
            }
        
        elif ambiguity_type == 'missing_object':
            return {
                'question': "I'd be happy to help! What type of data would you like to work with?",
                'options': [
                    {'letter': 'A', 'text': 'Emails', 'intent': 'emails'},
                    {'letter': 'B', 'text': 'Documents/Files', 'intent': 'documents'},
                    {'letter': 'C', 'text': 'Archives', 'intent': 'archives'},
                    {'letter': 'D', 'text': 'All data sources', 'intent': 'all'},
                ],
                'suggested_response': 'reply with A, B, C, or D'
            }
        
        elif ambiguity_type == 'too_vague':
            return {
                'question': "I want to make sure I understand correctly. What would you like me to do?",
                'options': [
                    {'letter': 'A', 'text': 'Search or find specific information', 'intent': 'search'},
                    {'letter': 'B', 'text': 'Show me lists or indexes', 'intent': 'list'},
                    {'letter': 'C', 'text': 'Analyze or create reports', 'intent': 'analyze'},
                    {'letter': 'D', 'text': 'Forecast or project future trends', 'intent': 'forecast'},
                    {'letter': 'E', 'text': 'Just have a conversation', 'intent': 'chat'},
                ],
                'suggested_response': 'reply with the letter that best matches what you need'
            }
        
        # Default clarification
        return {
            'question': "I'm here to help! Could you tell me more about what you're looking for?",
            'options': [
                {'letter': 'A', 'text': 'Search for specific information', 'intent': 'search'},
                {'letter': 'B', 'text': 'Get a list or overview', 'intent': 'list'},
                {'letter': 'C', 'text': 'Analyze data or create reports', 'intent': 'analyze'},
            ],
            'suggested_response': 'reply with A, B, or C, or explain in your own words'
        }
    
    def format_clarification_response(self, clarification: Dict) -> str:
        """
        Format the clarification question into a friendly response with options.
        """
        question = clarification['question']
        options = clarification['options']
        suggested = clarification['suggested_response']
        
        # Build formatted response
        response = f"{question}\n\n"
        
        for opt in options:
            response += f"**{opt['letter']}**. {opt['text']}\n"
        
        response += f"\nPlease {suggested}, and I'll help you right away!"
        
        return response
    
    def should_ask_for_clarification(self, confidence: float, ambiguity_info: Dict) -> bool:
        """Determine if clarification should be requested."""
        return confidence < self.confidence_threshold or ambiguity_info['is_ambiguous']
