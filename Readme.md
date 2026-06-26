# SmartSQL — Intelligent Text-to-SQL Agent

A chatbot that converts natural language questions into SQL queries and displays results using an e-commerce SQLite database.

## Tech Stack
- **Frontend**: Streamlit
- **LLM**: OpenAI GPT-4o-mini
- **Database**: SQLite (swappable to Snowflake)
- **Language**: Python

## Project Structure
```
smartsql/
├── app.py              # Streamlit UI — main entry point
├── db.py               # DB connection, query runner
├── agent.py            # OpenAI call to generate SQL
├── seed.py             # Creates and seeds the SQLite DB
├── utils/
│   ├── metadata.py     # Fetches table/column info from DB
│   └── prompt.py       # Builds the OpenAI prompt
├── data/
│   └── ecommerce.db    # SQLite database (auto-generated)
├── .env                # API keys (never commit this)
└── requirements.txt
```

## Setup

1. Clone the repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add your OpenAI API key in `.env`:
   ```
   OPENAI_API_KEY=your_key_here
   ```
4. Seed the database:
   ```bash
   python seed.py
   ```
5. Run the app:
   ```bash
   streamlit run app.py
   ```

## Sample Questions to Try
- "Show all customers from Mumbai"
- "Which product has the highest price?"
- "Total revenue by product category"
- "List all orders with status pending"
- "Top 5 customers by total order amount"