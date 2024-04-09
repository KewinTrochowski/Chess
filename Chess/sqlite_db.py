import sqlite3

def create_connection(db_file):
    """Łączy się z bazą danych SQLite"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    """Tworzy tabelę 'moves'"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS moves (
                id INTEGER PRIMARY KEY,
                move TEXT
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def insert_moves(conn, moves):
    """Wstawia ruchy do tabeli 'moves'"""
    try:
        cursor = conn.cursor()
        for move in moves:
            cursor.execute("INSERT INTO moves (move) VALUES (?)", (move,))
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def delete_all_moves(db_file):
    """Usuwa wszystkie ruchy z tabeli 'moves'"""
    conn = create_connection(db_file)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM moves")
        conn.commit()
    except sqlite3.Error as e:
        print(e)
def read_from_database(db_file):
    """Odczytuje dane z bazy danych SQLite"""
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM moves")  # Zapytanie do pobrania wszystkich danych z tabeli 'moves'
        rows = cursor.fetchall()  # Pobranie wszystkich wierszy
        return rows
    except sqlite3.Error as e:
        print(e)
    finally:
        conn.close()


def save_to_database(moves, db_file):
    conn = create_connection(db_file)
    if conn is not None:
        create_table(conn)
        insert_moves(conn, moves)
        conn.close()
    else:
        print("Error! cannot create the database connection.")


if __name__ == "__main__":
    dir = f"db/2024-04-09 13.09.31"
    database = f"{dir}/history.db"
    print(read_from_database(database))
    database = f"{dir}/timing.db"
    print(read_from_database(database))
