"""
agent.py — Calls the OpenAI API to generate SQL from a natural language question.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
from utils.prompt import build_messages

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_sql(question: str, model: str = "gpt-4o-mini") -> str:
    """
    Send a natural language question to OpenAI and return the generated SQL.
    """
    messages = build_messages(question)

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        max_tokens=300,
    )

    sql = response.choices[0].message.content.strip()

    # Strip markdown code fences if the model wraps them anyway
    if sql.startswith("```"):
        sql = sql.split("\n", 1)[1] if "\n" in sql else sql[3:]
    if sql.endswith("```"):
        sql = sql[:-3].strip()

    return sql
