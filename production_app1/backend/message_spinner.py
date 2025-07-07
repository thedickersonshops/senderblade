#!/usr/bin/env python3
"""
Message Spinner
Spins content using various techniques
"""

import re
import random
import string
import html
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('message_spinner')

class MessageSpinner:
    """Message spinner that uses various techniques to spin content"""
    
    def __init__(self):
        """Initialize the message spinner"""
        # Zero-width characters for invisible uniqueness
        self.zero_width_chars = [
            '\u200B',  # Zero-width space
            '\u200C',  # Zero-width non-joiner
            '\u200D',  # Zero-width joiner
            '\u2060',  # Word joiner
            '\u2061',  # Function application
            '\u2062',  # Invisible times
            '\u2063',  # Invisible separator
            '\u2064'   # Invisible plus
        ]
        
        # HTML comment templates for uniqueness
        self.html_comments = [
            '<!-- -->',
            '<!-- unique -->',
            '<!-- {random} -->',
            '<!-- {timestamp} -->'
        ]
    
    def spin_text(self, content: str) -> str:
        """
        Spin content using spinning syntax
        
        Args:
            content: Content with spinning syntax {option1|option2|option3}
            
        Returns:
            Spun content with one option selected from each set
        """
        if not content:
            return ""
            
        # Find all spinning sections - handle both inside and outside HTML tags
        pattern = r'\{([^{}]*\|[^{}]*)\}'
        
        def replace_spin(match):
            options_text = match.group(1)
            if '|' in options_text:
                options = [opt.strip() for opt in options_text.split('|')]
                return random.choice(options)
            return match.group(0)  # Return unchanged if no pipe found
            
        # Replace all spinning sections
        result = re.sub(pattern, replace_spin, content)
        return result
    
    def add_invisible_chars(self, content: str) -> str:
        """
        Add invisible characters to content for uniqueness
        
        Args:
            content: Original content
            
        Returns:
            Content with invisible characters added
        """
        if not content:
            return ""
            
        result = ""
        
        # Add invisible characters after spaces and punctuation
        for i, char in enumerate(content):
            result += char
            
            # Add invisible character with 30% probability after spaces and punctuation
            if char in ' ,.!?:;' and random.random() < 0.3:
                result += random.choice(self.zero_width_chars)
                
        return result
    
    def add_html_uniqueness(self, content: str) -> str:
        """
        Add uniqueness to HTML content
        
        Args:
            content: Original HTML content
            
        Returns:
            HTML content with uniqueness added
        """
        if not content:
            return ""
            
        # Check if it's HTML content
        if '<html' not in content.lower() and '<body' not in content.lower():
            # Not HTML, use invisible chars instead
            return self.add_invisible_chars(content)
            
        result = content
        
        # Add random HTML comments
        for _ in range(3):
            # Generate a random position to insert comment
            # Avoid inserting in the middle of tags
            parts = result.split('>')
            if len(parts) > 2:
                insert_pos = random.randint(1, len(parts) - 1)
                
                # Get comment template and fill in any placeholders
                comment = random.choice(self.html_comments)
                comment = comment.replace('{random}', ''.join(random.choices(string.ascii_letters + string.digits, k=8)))
                comment = comment.replace('{timestamp}', str(random.randint(10000000, 99999999)))
                
                # Insert comment
                parts[insert_pos] = parts[insert_pos] + comment
                result = '>'.join(parts)
        
        # Add random attributes to some tags
        tags_to_modify = ['div', 'span', 'p', 'a', 'table', 'tr', 'td']
        for tag in tags_to_modify:
            # Find tag occurrences
            pattern = f'<{tag}([^>]*)>'
            
            def add_random_attr(match):
                attrs = match.group(1)
                # Add a random data attribute
                attr_name = f'data-u{random.randint(1000, 9999)}'
                attr_value = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
                return f'<{tag}{attrs} {attr_name}="{attr_value}">'
                
            # Replace some occurrences (50% chance for each)
            if random.random() < 0.5:
                result = re.sub(pattern, add_random_attr, result, count=random.randint(1, 3))
        
        return result
    
    def generate_variations(self, content: str, count: int = 5) -> List[str]:
        """
        Generate multiple variations of the content
        
        Args:
            content: Original content with spinning syntax
            count: Number of variations to generate
            
        Returns:
            List of spun content variations
        """
        variations = []
        
        for _ in range(count):
            # Spin the content
            spun = self.spin_text(content)
            
            # Add uniqueness
            if '<html' in content.lower() or '<body' in content.lower():
                spun = self.add_html_uniqueness(spun)
            else:
                spun = self.add_invisible_chars(spun)
                
            variations.append(spun)
            
        return variations
    
    def auto_spin(self, content: str, level: str = 'medium') -> str:
        """
        Automatically add spinning syntax to content
        
        Args:
            content: Original content
            level: Spinning level (low, medium, high)
            
        Returns:
            Content with spinning syntax added
        """
        if not content:
            return ""
        
        # Get common words to replace based on level
        common_words = self._get_common_words_for_level(level)
        
        # Extract personalization variables to preserve them
        personalization_vars = self._extract_personalization_variables(content)
        
        # Replace common words with spinning syntax
        spun_content = self._auto_replace_with_synonyms(content, common_words, personalization_vars)
        
        return spun_content
    
    def _get_common_words_for_level(self, level: str) -> Dict[str, List[str]]:
        """Get common words to replace based on spinning level"""
        # Dictionary of common words and their synonyms
        common_words = {
            # Greetings
            'Hello': ['Hi', 'Hey', 'Greetings'],
            'Hi': ['Hello', 'Hey', 'Greetings'],
            # Common verbs
            'get': ['receive', 'obtain', 'acquire'],
            'use': ['utilize', 'employ', 'leverage'],
            'make': ['create', 'produce', 'develop'],
            'see': ['view', 'observe', 'notice'],
            'know': ['understand', 'recognize', 'realize'],
            'want': ['desire', 'wish', 'need'],
            'look': ['check', 'examine', 'view'],
            'find': ['discover', 'locate', 'identify'],
            # Common adjectives
            'good': ['great', 'excellent', 'wonderful'],
            'new': ['recent', 'latest', 'fresh'],
            'best': ['finest', 'top', 'leading'],
            'free': ['complimentary', 'no-cost', 'zero-cost'],
            'better': ['improved', 'enhanced', 'superior'],
            # Common phrases
            'thank you': ['thanks', 'appreciate it', 'many thanks'],
            'let me know': ['inform me', 'keep me posted', 'update me'],
            'get back to you': ['follow up with you', 'respond to you', 'reply to you'],
            'looking forward': ['excited about', 'anticipating', 'eager for']
        }
        
        # Filter based on level
        if level == 'low':
            # Return only the most common words (greetings and basic verbs)
            return {k: v for k, v in common_words.items() if k in ['Hello', 'Hi', 'get', 'use', 'make', 'thank you']}
        elif level == 'medium':
            # Return most words except phrases
            return {k: v for k, v in common_words.items() if len(k.split()) <= 1}
        else:  # high
            # Return all words and phrases
            return common_words
    
    def _extract_personalization_variables(self, content: str) -> List[str]:
        """Extract personalization variables from content"""
        # Find all potential personalization variables (both single and double braces)
        variables = []
        # Check for double-brace format: {{first_name}}
        for match in re.findall(r'\{\{([^{}]+)\}\}', content):
            if match not in variables:
                variables.append(match)
        
        # Check for single-brace format that doesn't contain pipes: {first_name}
        for match in re.findall(r'\{([^{}|]+)\}', content):
            if match not in variables and not match.strip().startswith('|') and not match.strip().endswith('|'):
                variables.append(match)
        
        return variables
    
    def _auto_replace_with_synonyms(self, content: str, common_words: Dict[str, List[str]], personalization_vars: List[str]) -> str:
        """Replace common words with spinning syntax while preserving personalization variables"""
        result = content
        
        # First, protect all personalization variables by replacing them with placeholders
        protected_content = result
        for var in personalization_vars:
            # Handle both formats: {first_name} and {{first_name}}
            protected_content = protected_content.replace('{{' + var + '}}', f'PERSONALIZATION_VAR_DOUBLE_{var}_PLACEHOLDER')
            protected_content = protected_content.replace('{' + var + '}', f'PERSONALIZATION_VAR_SINGLE_{var}_PLACEHOLDER')
        
        # Create a regex pattern that matches whole words only
        for word, synonyms in common_words.items():
            # Skip if the word is too short
            if len(word) < 3:
                continue
                
            # Create pattern to match whole word with word boundaries
            pattern = r'\b' + re.escape(word) + r'\b'
            
            # Create spinning syntax with the original word and its synonyms
            replacement = '{' + word + '|' + '|'.join(synonyms) + '}'
            
            # Replace the word with spinning syntax
            protected_content = re.sub(pattern, replacement, protected_content, flags=re.IGNORECASE)
        
        # Restore personalization variables
        for var in personalization_vars:
            protected_content = protected_content.replace(f'PERSONALIZATION_VAR_DOUBLE_{var}_PLACEHOLDER', '{{' + var + '}}')
            protected_content = protected_content.replace(f'PERSONALIZATION_VAR_SINGLE_{var}_PLACEHOLDER', '{' + var + '}')
        
        return protected_content

# Singleton instance
_spinner = None

def get_message_spinner() -> MessageSpinner:
    """Get the singleton instance of the message spinner"""
    global _spinner
    if _spinner is None:
        _spinner = MessageSpinner()
    return _spinner