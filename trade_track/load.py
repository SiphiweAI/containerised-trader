from dotenv import load_dotenv
import os
import psycopg2
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def load_trade_data(parsed):
    """
    Inserts parsed trade data into the 'trades' table.
    
    Parameters:
        parsed (dict): Example:
            {
                'Pair': 'EUR/USD',
                'Verdict': 'Win',
                'Entry Price': '1.0845',
                'Stop-Loss': '1.0800',
                'PnL': 25.3
            }
    """
    
    # connect to PostgreSQL
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 5432)
    )

    conn.autocommit = True

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO trades (time, pair, verdict, entry_price, pnl)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                datetime.utcnow(),
                parsed.get("Pair"),
                parsed.get("Verdict"),
                float(parsed.get("Entry Price", 0) or 0),
                float(parsed.get("PnL", 0) or 0),
            )
        )
    conn.close()
    logger.info("✅ Trade inserted successfully.")
