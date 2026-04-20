import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'inventory.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            category TEXT,
            quantity INTEGER,
            price REAL
        )
    ''')
    
    # Create distributors table
    cursor.execute('''
         CREATE TABLE IF NOT EXISTS distributors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT,
            address TEXT
        )
    ''')

    # Create bills table
    cursor.execute('''
         CREATE TABLE bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            distributor_id INTEGER NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(distributor_id) REFERENCES distributors(id)
        );
    ''')

    cursor.execute('''
         CREATE TABLE bill_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY(bill_id) REFERENCES bills(id),
            FOREIGN KEY(book_id) REFERENCES books(id)
        );
    ''')

    # Insert default users
    cursor.execute("INSERT INTO admin (username, password) VALUES ('admin','admin0123')")
    cursor.execute("INSERT INTO staff (username, password) VALUES ('staff','staff0123')")
    
    conn.commit()
    conn.close()
    print("Database and tables created successfully.")

if __name__ == "__main__":
    setup_database()
