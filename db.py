import sqlite3

def init_db():
    conn = sqlite3.connect('flights.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            email TEXT,
            flight_number TEXT,
            last_delay INTEGER DEFAULT 0,
            last_checked TIMESTAMP,
            active BOOLEAN DEFAULT 1
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully")
