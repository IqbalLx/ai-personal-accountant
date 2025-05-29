import os
from dotenv import load_dotenv

from psycopg import Connection, Error as DBError
from psycopg.rows import dict_row
from google.adk.tools.tool_context import ToolContext
from pydantic import ValidationError

from personal_accountant.types.type import SpendingAgentOutput

if os.path.exists(".env"):
    load_dotenv(".env")


conn: Connection | None = None


def get_db_conn():
    global conn

    if conn is not None:
        return

    db_url = os.getenv("POSTGRES_URL")
    if db_url is None:
        raise ValueError("POSTGRES_URL is not set!")

    conn = Connection.connect(db_url)

    return


def migrate():
    global conn

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


def save_spending(tool_context: ToolContext):
    """
    Use this tool to save user spending into database. No need to pass the parameter, just pass the context, it will read it from there

    Args:
        tool_context: The ADK tool context.
    """

    get_db_conn()

    structured_spending = tool_context.state.get("structured_spending")
    if structured_spending is None:
        return {
            "state": "error",
            "result": "spending not found, make sure you call spend_extractor_agent first",
        }

    try:
        spending_data = SpendingAgentOutput.model_validate(structured_spending)
    except ValidationError as e:
        return {
            "state": "error",
            "result": f"spending data validation failed with error {e.title}, retry spend_extractor_agent tool call",
        }

    global conn
    cursor = conn.cursor()

    try:
        insert_spending_sql = """
        INSERT INTO spendings (
            type, currency, transaction_date, transaction_time, transaction_category,
            merchant_name, merchant_address, merchant_phone, merchant_website, merchant_tax_id,
            summary_subtotal, summary_discount_amount, summary_tax_amount, summary_shipping_amount,
            summary_total_amount, summary_amount_paid, summary_change_due,
            payment_method, payment_card_type, payment_transaction_id, notes
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id;
        """
        spending_values = (
            spending_data.type,
            spending_data.currency,
            spending_data.transaction_date,
            spending_data.transaction_time,
            spending_data.transaction_category,
            spending_data.merchant_name,
            spending_data.merchant_address,
            spending_data.merchant_phone,
            spending_data.merchant_website,
            spending_data.merchant_tax_id,
            spending_data.summary_subtotal,
            spending_data.summary_discount_amount,
            spending_data.summary_tax_amount,
            spending_data.summary_shipping_amount,
            spending_data.summary_total_amount,
            spending_data.summary_amount_paid,
            spending_data.summary_change_due,
            spending_data.payment_method,
            spending_data.payment_card_type,
            spending_data.payment_transaction_id,
            spending_data.notes,
        )

        cursor.execute(insert_spending_sql, spending_values)
        inserted_spending_id = cursor.fetchone()[0]  # Get the generated ID

        # SQL for inserting into spending_items table
        insert_item_sql = """
        INSERT INTO spending_items (
            spending_id, description, quantity, unit_price, total
        ) VALUES (%s, %s, %s, %s, %s);
        """
        for item in spending_data.items:
            item_values = (
                inserted_spending_id,
                item.description,
                item.quantity,
                item.unit_price,
                item.total,
            )
            cursor.execute(insert_item_sql, item_values)

        conn.commit()  # Commit the transaction
        return {"state": "success", "result": "spending saved succesfully"}

    except (Exception, DBError) as error:
        if conn:
            conn.rollback()  # Rollback in case of error
        return {
            "state": "error",
            "result": f"Error while saving spending data to PostgreSQL: {error}",
        }
    finally:
        if cursor:
            cursor.close()


def query_database(query: str, tool_context: ToolContext):
    """
    Use this tool to query from the database.

    Args:
        query: The SQL query to be executed into the database.
        tool_context: The ADK tool context.
    """
    get_db_conn()

    global conn

    cur = conn.cursor(row_factory=dict_row)

    try:
        res = cur.execute(query).fetchall()

        tool_context.state["sql_output"] = res

        return {
            "state": "success",
            "result": "data retrieved, you can call exit_loop tool now",
        }
    except Exception as e:
        tool_context.state["sql_error"] = e

        return {
            "state": "error",
            "result": f"query errored with message {e}",
        }

    finally:
        cur.close()


if __name__ == "__main__":
    get_db_conn()
    migrate()
