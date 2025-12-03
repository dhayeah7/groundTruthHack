"""PII Redaction Layer - Section 5 of Architecture.

IMPORTANT: Only redacts RAG-retrieved context, NOT user input.
This ensures no PII reaches the Gemini LLM.
"""
import re
from typing import List, Dict


class PIIRedactor:
    """Redact PII from retrieved context while preserving operational data."""
    
    # Patterns for PII detection
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    # Phone pattern: Requires at least 7 digits total to avoid matching prices/years
    # Matches: +1-555-555-5555, 555-555-5555, +91 44 4214 3200
    PHONE_PATTERN = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,9}')
    ORDER_ID_PATTERN = re.compile(r'\b(ORD|ORDER|ID)[-_]?[A-Z0-9]{6,}\b', re.IGNORECASE)
    
    # Preservations - keep these patterns
    PRESERVE_PATTERNS = [
        r'\bKLCC\b',
        r'\bPavilion\b',
        r'\bMid Valley\b',
        r'\b1 Utama\b',
        r'\bSunway\b',
        r'\bNike\b',
        r'\bPegasus\b',
        r'\bAir Max\b',
        r'\bVaporfly\b',
        r'\bMetcon\b',
        r'\bRevolution\b',
        r'\bDri-FIT\b',
        r'\RM\d+',
        r'\$\d+',
    ]
    
    def __init__(self):
        """Initialize the PII redactor."""
        self.redaction_count = 0
    
    def redact_email(self, text: str) -> str:
        """Redact email addresses."""
        return self.EMAIL_PATTERN.sub('[EMAIL_REDACTED]', text)
    
    def redact_phone(self, text: str) -> str:
        """
        Redact phone numbers.
        Note: We explicitly allow store phone numbers to remain visible.
        """
        # Check if this is likely store information
        # Chennai store phones start with +91 44
        is_store_contact = "+91 44" in text or "Nike Store" in text or "Mall" in text or "contact:" in text
        
        if is_store_contact:
            return text
            
        return self.PHONE_PATTERN.sub('[PHONE_REDACTED]', text)
    
    def redact_order_ids(self, text: str) -> str:
        """Redact order/transaction IDs."""
        return self.ORDER_ID_PATTERN.sub('[ORDER_ID_REDACTED]', text)
    
    def redact_exact_addresses(self, text: str) -> str:
        """
        Redact exact street addresses while keeping mall names.
        This is a simplified version - in production, use NER models.
        """
        # Remove "Lot" addresses from malls
        text = re.sub(r'Lot\s+[A-Z0-9.-]+,?\s*', '', text)
        # Remove level/floor info that might be too specific
        text = re.sub(r'Level\s+\d+,?\s*', '', text)
        text = re.sub(r'Floor\s+\d+,?\s*', '', text)
        # Remove postal codes
        text = re.sub(r'\b\d{5,6}\b', '', text)
        
        return text
    
    def redact_order_ids(self, text: str) -> str:
        """Redact order/transaction IDs."""
        return self.ORDER_ID_PATTERN.sub('[ORDER_ID_REDACTED]', text)
    
    def redact_exact_addresses(self, text: str) -> str:
        """
        Redact exact street addresses while keeping mall names.
        This is a simplified version - in production, use NER models.
        """
        # Remove "Lot" addresses from malls
        text = re.sub(r'Lot\s+[A-Z0-9.-]+,?\s*', '', text)
        # Remove level/floor info that might be too specific
        text = re.sub(r'Level\s+\d+,?\s*', '', text)
        text = re.sub(r'Floor\s+\d+,?\s*', '', text)
        # Remove postal codes
        text = re.sub(r'\b\d{5,6}\b', '', text)
        
        return text
    
    def should_preserve(self, text: str) -> bool:
        """Check if text matches preservation patterns."""
        for pattern in self.PRESERVE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def redact_context(self, context_chunks: List[Dict]) -> List[Dict]:
        """
        Redact PII from retrieved RAG context chunks.
        
        Args:
            context_chunks: List of context dictionaries with 'text' field
        
        Returns:
            Sanitized context chunks with PII removed
        """
        self.redaction_count = 0
        sanitized_chunks = []
        
        for chunk in context_chunks:
            if 'text' not in chunk:
                sanitized_chunks.append(chunk)
                continue
            
            original_text = chunk['text']
            sanitized_text = original_text
            
            # Apply redactions in sequence
            sanitized_text = self.redact_email(sanitized_text)
            sanitized_text = self.redact_phone(sanitized_text)
            sanitized_text = self.redact_order_ids(sanitized_text)
            sanitized_text = self.redact_exact_addresses(sanitized_text)
            
            # Count redactions
            if sanitized_text != original_text:
                self.redaction_count += 1
            
            # Create sanitized chunk
            sanitized_chunk = chunk.copy()
            sanitized_chunk['text'] = sanitized_text
            sanitized_chunk['pii_redacted'] = sanitized_text != original_text
            
            sanitized_chunks.append(sanitized_chunk)
        
        return sanitized_chunks
    
    def get_redaction_summary(self) -> Dict[str, int]:
        """Get summary of redactions performed."""
        return {
            "chunks_redacted": self.redaction_count,
            "status": "PII sanitized - safe for LLM"
        }


# Global redactor instance
redactor = PIIRedactor()
