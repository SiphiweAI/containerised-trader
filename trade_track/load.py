import os
import psycopg2
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
db_pool = None  # initialized later


def get_db_pool():
    """Return a global connection pool, creating it if necessary."""
    global db_pool
    if db_pool is None:
        db_pool = psycopg2.pool.SimpleConnectionPool(
            1,
            10,
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", 5432)
        )
    return db_pool


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
    conn = get_db_pool().getconn()
    try:
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
                ),
            )
        conn.commit()
        logger.info("✅ Trade inserted successfully.")
    finally:
        get_db_pool().putconn(conn)