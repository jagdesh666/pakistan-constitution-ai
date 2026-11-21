import psycopg2

# The REAL host from your Neon screenshot:
HOST = "ep-royal-frog-b5qnfl3o-pooler.c-7.us-east-2.aws.neon.tech"
PORT = 5432
DATABASE = "neondb"
USER = "neondb_owner"
PASSWORD = "npg_AdVacMXN98ns"

print("=" * 60)
print("TESTING DIRECT PSYCOPG2 CONNECTION TO NEON...")
print("=" * 60)

try:
    conn = psycopg2.connect(
        host=HOST,
        port=PORT,
        dbname=DATABASE,
        user=USER,
        password=PASSWORD,
        sslmode="require",
        connect_timeout=10
    )
    cur = conn.cursor()
    cur.execute("SELECT current_database(), current_user, version();")
    row = cur.fetchone()
    print(" SUCCESS! Connected to Neon Cloud:")
    print(f"  • Database: {row[0]}")
    print(f"  • User:     {row[1]}")
    print(f"  • Version:  {row[2][:35]}...")
    cur.close()
    conn.close()
except Exception as e:
    print(f" CONNECTION FAILED: {e}")