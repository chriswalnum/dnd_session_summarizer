# v1.2.0
# DnD-safe sanitization with preserved gaming terms

import re
from typing import List, Set

class DnDSanitizer:
    def __init__(self):
        # Common D&D terms that should never be filtered
        self.dnd_allowlist = {
            'attack', 'damage', 'kill', 'dead', 'death', 'blood', 
            'dragon', 'demon', 'devil', 'hell', 'undead', 'zombie',
            'corpse', 'body', 'wound', 'ritual', 'curse'
        }
        
        # Load actual profanity list (import from external source)
        self.profanity_set = self._load_profanity_list()
        
    def _load_profanity_list(self) -> Set[str]:
        # Replace with actual profanity list import
        return {'badword1', 'badword2'}  # Placeholder
        
    def sanitize(self, text: str) -> str:
        words = text.split()
        sanitized_words = []
        
        for word in words:
            clean_word = word.lower().strip('.,!?')
            if clean_word in self.profanity_set and clean_word not in self.dnd_allowlist:
                sanitized_words.append('[REMOVED]')
            else:
                sanitized_words.append(word)
                
        return ' '.join(sanitized_words)
        
    def is_safe(self, phrase: str) -> bool:
        words = phrase.lower().split()
        return not any(word.strip('.,!?') in self.profanity_set 
                      for word in words 
                      if word not in self.dnd_allowlist)
