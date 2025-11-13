import pandas as pd
import psycopg2

PAYMENT_TYPE_DESCRIPTIONS = {
    "credit_card": "Payment by credit card",
    "boleto": "Boleto (bank slip)",
    "voucher": "Voucher payment",
    "debit_card": "Payment by debit card",
    "not_defined": "Payment type not defined",
}

def get_connection():
    return psycopg2.connect(
        host="postgres",
        port=5432,         
        user="admin",
        password="admin",
        dbname="operation",
    )


def load_payment_type_from_csv(csv_path: str):
    df = pd.read_csv(csv_path)

    payment_types = (
        df["payment_type"]
        .dropna()
        .astype(str)
        .str.lower()
        .sort_values()
        .unique()
    )

    conn = get_connection()
    cur = conn.cursor()

    for code in payment_types:
        desc = PAYMENT_TYPE_DESCRIPTIONS.get(
            code,
            code.replace("_", " ").title(),  
        )
        cur.execute(
            """
            INSERT INTO payment_type (payment_type_code, payment_type_description)
            VALUES (%s, %s)
            ON CONFLICT (payment_type_code)
            DO UPDATE SET payment_type_description = EXCLUDED.payment_type_description;
            """,
            (code, desc),
        )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Loaded/updated {len(payment_types)} payment types.")

if __name__ == "__main__":
    load_payment_type_from_csv("source_data/olist_order_payments_dataset.csv")
