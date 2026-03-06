"""Simulated knowledge base for the RAG pipeline.

These documents act as the "vector store" that the retrieval stage searches.
The content is intentionally simple so candidates can reason about retrieval
and chunking behavior without domain-specific knowledge.
"""

DOCUMENTS = [
    {
        "id": "doc-001",
        "title": "Refund Policy",
        "content": (
            "Customers may request a full refund within 30 days of purchase. "
            "Refunds are processed within 5-7 business days after the request "
            "is approved. To request a refund, contact support with your order "
            "number and reason for the return."
        ),
    },
    {
        "id": "doc-002",
        "title": "Shipping Policy",
        "content": (
            "Standard orders ship within 2 business days. Express shipping "
            "is available for an additional fee and delivers within 1 business "
            "day. All orders include tracking information sent via email."
        ),
    },
    {
        "id": "doc-003",
        "title": "Return Policy",
        "content": (
            "Items may be returned if they are unopened and in original "
            "packaging. Opened items are eligible for exchange only. Returns "
            "must be initiated within 14 days of delivery."
        ),
    },
    {
        "id": "doc-004",
        "title": "Warranty Information",
        "content": (
            "All electronics come with a 1-year manufacturer warranty. "
            "Warranty covers defects in materials and workmanship. Physical "
            "damage and water damage are not covered under warranty."
        ),
    },
    {
        "id": "doc-005",
        "title": "Account Management",
        "content": (
            "Users can update their account information in the settings page. "
            "Password changes require email verification. Two-factor "
            "authentication is available for enhanced security."
        ),
    },
]
