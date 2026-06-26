"""
prompt.py — Builds the system and user prompts for the OpenAI API call.
"""

from utils.metadata import get_schema_summary


SYSTEM_PROMPT = """You are a helpful SQL assistant. You are given a natural language question about an ecommerce database and must return ONLY a valid SQLite SELECT query — no explanations, no markdown fences, just the raw SQL.

Rules:
- Only generate SELECT queries (read-only).
- Use the exact table and column names from the schema provided.
- Do not use any tables or columns not listed in the schema.
- Return a single SQL statement ending with a semicolon.
"""


def build_messages(user_question: str) -> list[dict]:
    """
    Build the message list for the OpenAI chat completion call.
    """
    schema = get_schema_summary()

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Database schema:\n{schema}\n\n"
                f"Question: {user_question}\n\n"
                "Respond with ONLY the SQL query."
            ),
        },
    ]
