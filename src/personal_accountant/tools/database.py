import os
from dotenv import load_dotenv

from psycopg import Connection

if os.path.exists(".env"):
    load_dotenv(".env")


conn: Connection | None = None


def get_db_conn():
    global conn

    if conn is not None:
        return conn

    db_url = os.getenv("POSTGRES_URL")
    if db_url is None:
        raise ValueError("POSTGRES_URL is not set!")

    conn = Connection.connect(db_url)

    return conn


def migrate(conn: Connection):
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS spendings (
            id SERIAL PRIMARY KEY,
            type TEXT NOT NULL,
            currency TEXT NOT NULL,
            transaction_date DATE NOT NULL,
            transaction_time TIME NULL,
            transaction_category TEXT NULL,

            merchant_name TEXT NOT NULL,
            merchant_address TEXT NULL,
            merchant_phone TEXT NULL,
            merchant_website TEXT NULL,
            merchant_tax_id TEXT NULL,

            summary_subtotal NUMERIC(10, 2) NOT NULL,
            summary_discount_amount NUMERIC(10, 2) NULL,
            summary_tax_amount NUMERIC(10, 2) NULL,
            summary_shipping_amount NUMERIC(10, 2) NULL,
            summary_total_amount NUMERIC(10, 2) NOT NULL,
            summary_amount_paid NUMERIC(10, 2) NULL,
            summary_change_due NUMERIC(10, 2) NULL,

            payment_method TEXT NULL,
            payment_card_type TEXT NULL,
            payment_transaction_id TEXT NULL,

            notes TEXT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS spending_items (
            id SERIAL PRIMARY KEY,
            spending_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            quantity NUMERIC(10, 2) NOT NULL,
            unit_price NUMERIC(10, 2) NOT NULL,
            total NUMERIC(10, 2) NOT NULL,

            CONSTRAINT fk_spending
                FOREIGN KEY (spending_id)
                REFERENCES spendings (id)
                ON DELETE CASCADE
        );
    """)

    conn.commit()


def query_database(conn: Connection):
    def execute(query: str):
        try:
            cur = conn.cursor()
            cur.execute(query)
            results = cur.fetchall()
            results = [res for res in results]
            cur.close()

            return results

        except Exception as e:
            return f"Query {query} errored with message: {e}, fix and try again"

    return execute


if __name__ == "__main__":
    migrate(get_db_conn())
