SCENARIOS = {
    "returns_policy_retrieval": {
        "documents": [
            {
                "id": "doc_returns",
                "title": "Electronics Return Policy",
                "content": (
                    "Electronics may be returned within a 30-day return window. "
                    "Items must be in original packaging, and refunds are processed "
                    "within 5-7 business days after approval."
                ),
            },
            {
                "id": "doc_shipping",
                "title": "Shipping Policy",
                "content": "Standard shipping takes 3-5 business days and express shipping takes 1-2 days.",
            },
            {
                "id": "doc_accounts",
                "title": "Account Support",
                "content": "Users can reset passwords and change their profile settings from the account console.",
            },
        ],
        "default_query": "What is the return policy for electronics?",
        "baseline_prompt": "Answer the question.",
    },
    "refund_processing_chunking": {
        "documents": [
            {
                "id": "doc_refunds",
                "title": "Refund Processing",
                "content": (
                    "Customers may request a refund within 30 days of purchase. "
                    "Approved refunds are processed within 5-7 business days "
                    "after the item is received and inspected."
                ),
            },
            {
                "id": "doc_warranty",
                "title": "Warranty",
                "content": "Warranty claims cover manufacturing defects for one year.",
            },
        ],
        "default_query": "How long do approved refunds take to process?",
        "baseline_prompt": "Answer using the context.",
    },
    "grounding_prompt_rewrite": {
        "documents": [
            {
                "id": "doc_abstention",
                "title": "Grounding Instructions",
                "content": (
                    "The assistant must answer using only retrieved documents. "
                    "If the context is insufficient, say you do not know."
                ),
            }
        ],
        "default_query": "How should the assistant behave if context is missing?",
        "baseline_prompt": "Be helpful and answer confidently.",
    },
    "abstain_when_retrieval_is_weak": {
        "documents": [
            {
                "id": "doc_retrieval_limits",
                "title": "Retrieval Reliability Guidance",
                "content": (
                    "When retrieval relevance is low, the assistant must abstain "
                    "instead of inventing an answer."
                ),
            },
            {
                "id": "doc_returns_short",
                "title": "Returns Summary",
                "content": "Returns are allowed in limited cases with manager approval.",
            },
        ],
        "default_query": "What should the assistant do when retrieval confidence is low?",
        "baseline_prompt": "Provide the best answer you can.",
    },
}
