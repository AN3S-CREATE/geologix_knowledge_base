"""
Spell Correction & Fuzzy Matching System
Handles misspelled words and improves query understanding.
"""

from typing import Dict, List, Tuple
import re


class SpellCorrector:
    """Handle misspelled words and fuzzy matching for user queries."""
    
    def __init__(self):
        # Common business/technical terms and their misspellings
        self.corrections = {
            # Actions
            'analyz': 'analyze', 'analize': 'analyze', 'analise': 'analyze',
            'forscast': 'forecast', 'forcast': 'forecast', 'forcaste': 'forecast',
            'retrive': 'retrieve', 'retreive': 'retrieve', 'retreve': 'retrieve',
            'serch': 'search', 'seach': 'search', 'srch': 'search',
            'sumary': 'summary', 'summery': 'summary',
            'recomend': 'recommend', 'recomendation': 'recommendation',
            
            # Objects
            'emal': 'email', 'emial': 'email', 'emai': 'email', 'e-mail': 'email',
            'documnt': 'document', 'docment': 'document', 'dcument': 'document',
            'reprt': 'report', 'raport': 'report',
            'contarct': 'contract', 'contrat': 'contract',
            'invice': 'invoice', 'invois': 'invoice',
            'quater': 'quarter', 'quartr': 'quarter',
            
            # Descriptors  
            'comunication': 'communication', 'comunicate': 'communicate',
            'communicaton': 'communication', 'comuniction': 'communication',
            'improvment': 'improvement', 'imporve': 'improve', 'improv': 'improve',
            'bussiness': 'business', 'busines': 'business', 'buisness': 'business',
            'finacial': 'financial', 'financal': 'financial',
            'operationl': 'operational', 'opperational': 'operational',
            
            # Time periods
            'yestarday': 'yesterday', 'yesturday': 'yesterday',
            'tommorow': 'tomorrow', 'tomorro': 'tomorrow',
            'mounth': 'month', 'mont': 'month',
            'yer': 'year', 'yeer': 'year',
        }
        
        # Synonyms for better understanding
        self.synonyms = {
            'show': ['display', 'present', 'list', 'give'],
            'get': ['fetch', 'retrieve', 'find', 'obtain'],
            'find': ['search', 'locate', 'look for', 'discover'],
            'analyze': ['examine', 'assess', 'evaluate', 'review', 'study'],
            'create': ['make', 'generate', 'produce', 'build'],
            'improve': ['enhance', 'better', 'optimize', 'upgrade'],
            'email': ['mail', 'message', 'correspondence'],
            'document': ['file', 'doc', 'paper', 'record'],
        }
    
    def correct_spelling(self, text: str) -> Tuple[str, List[str]]:
        """
        Correct spelling in text.
        
        Returns:
            Tuple of (corrected_text, list_of_corrections_made)
        """
        corrected = text
        corrections_made = []
        
        words = text.lower().split()
        corrected_words = []
        
        for word in words:
            # Remove punctuation for checking
            clean_word = re.sub(r'[^\w\s]', '', word)
            
            if clean_word in self.corrections:
                corrected_word = self.corrections[clean_word]
                corrected_words.append(corrected_word)
                corrections_made.append(f"{clean_word} → {corrected_word}")
            else:
                corrected_words.append(word)
        
        corrected = ' '.join(corrected_words)
        return corrected, corrections_made
    
    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def fuzzy_match(self, word: str, candidates: List[str], threshold: int = 2) -> str:
        """
        Find best fuzzy match for a word from candidates.
        
        Args:
            word: The word to match
            candidates: List of correct words to match against
            threshold: Maximum edit distance to consider (default: 2)
        
        Returns:
            Best match or original word if no good match found
        """
        word_lower = word.lower()
        best_match = word
        best_distance = threshold + 1
        
        for candidate in candidates:
            distance = self.levenshtein_distance(word_lower, candidate.lower())
            if distance < best_distance:
                best_distance = distance
                best_match = candidate
        
        return best_match if best_distance <= threshold else word
    
    def expand_with_synonyms(self, text: str) -> List[str]:
        """
        Expand query with synonyms for better matching.
        
        Returns:
            List of alternative phrasings
        """
        alternatives = [text]
        words = text.lower().split()
        
        for word in words:
            if word in self.synonyms:
                for synonym in self.synonyms[word][:2]:  # Use top 2 synonyms
                    alt_text = text.lower().replace(word, synonym)
                    if alt_text not in alternatives:
                        alternatives.append(alt_text)
        
        return alternatives
    
    def normalize_query(self, query: str) -> Dict:
        """
        Normalize user query by correcting spelling and expanding synonyms.
        
        Returns:
            Dict with:
                - original: Original query
                - corrected: Spell-corrected query
                - corrections: List of corrections made
                - alternatives: Alternative phrasings with synonyms
        """
        # Correct spelling
        corrected, corrections = self.correct_spelling(query)
        
        # Expand with synonyms
        alternatives = self.expand_with_synonyms(corrected)
        
        return {
            'original': query,
            'corrected': corrected,
            'corrections': corrections,
            'alternatives': alternatives,
            'has_corrections': len(corrections) > 0
        }
    
    def get_intent_keywords(self) -> Dict[str, List[str]]:
        """Get all intent keywords including synonyms for fuzzy matching."""
        intent_keywords = {
            'list': ['list', 'show', 'display', 'index', 'all'],
            'retrieve': ['get', 'retrieve', 'fetch', 'open', 'read'],
            'search': ['search', 'find', 'look', 'locate', 'discover'],
            'analyze': ['analyze', 'analysis', 'examine', 'assess', 'evaluate', 'review'],
            'forecast': ['forecast', 'predict', 'project', 'estimate'],
            'create': ['create', 'make', 'generate', 'produce', 'build'],
        }
        return intent_keywords
