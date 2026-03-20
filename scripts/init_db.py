import asyncio
import os
import re
from pathlib import Path

import asyncpg
from dotenv import load_dotenv


async def main() -> None:
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    schema_path = Path(__file__).resolve().parents[1] / "supabase" / "migrations" / "001_initial.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    schema_sql = schema_path.read_text(encoding="utf-8")
    table_names = re.findall(r"CREATE TABLE\s+(?:IF NOT EXISTS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)", schema_sql)

    conn = await asyncpg.connect(dsn=database_url)
    try:
        await conn.execute(schema_sql)
    finally:
        await conn.close()

    for table_name in table_names:
        print(f"created table: {table_name}")
    print("Schema applied successfully")


if __name__ == "__main__":
    asyncio.run(main())
