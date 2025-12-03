from pii_redaction import PIIRedactor
import json

def run_demo():
    redactor = PIIRedactor()
    
    # Sample data with PII
    samples = [
        {
            "description": "Email Redaction",
            "text": "Please contact us at support@nike.com or john.doe@gmail.com for assistance."
        },
        {
            "description": "Phone Redaction (Personal)",
            "text": "Call me at +1-555-010-9988 or 555-0199."
        },
        {
            "description": "Phone Preservation (Store)",
            "text": "Store contact: +91 44 4214 3200."
        },
        {
            "description": "Order ID Redaction",
            "text": "My order number is ORD-123456789. Can you check status for ORDER_98765ABC?"
        },
        {
            "description": "Address Redaction",
            "text": "I live at Lot 123, Level 2, 50000 Kuala Lumpur. Meet me at Pavilion Mall."
        }
    ]
    
    print("=== PII Redaction Demo ===\n")
    
    for sample in samples:
        print(f"--- {sample['description']} ---")
        print(f"Original: {sample['text']}")
        
        # Create a chunk-like structure as expected by redact_context
        chunks = [{"text": sample['text']}]
        redacted_chunks = redactor.redact_context(chunks)
        redacted_text = redacted_chunks[0]['text']
        
        print(f"Redacted: {redacted_text}")
        print()

if __name__ == "__main__":
    run_demo()
