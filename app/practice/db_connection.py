from getpass import getpass

import psycopg


def main() -> None:
    with psycopg.connect(
        host="localhost",
        port=5433,
        dbname="platform",
        user="postgres",
        password="dev",
        connect_timeout=10,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database(), current_user")
            print("Connected:", cursor.fetchone())

            cursor.execute("SELECT COUNT(*) FROM rag.practice_chunks")
            print("Practice table row count:", cursor.fetchone())


if __name__ == "__main__":
    main()
