import sqlite3
import datetime

class ShelfDatabase:
    def __init__(self, db_name="shelf_analytics.db"):
        """
        Initializes the database connection and creates the table if it doesn't exist.
        """
        self.db_name = db_name
        self.create_table()

    def create_table(self):
        """Creates the 'logs' table to store analysis results."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # SQL Query to create table
        create_query = '''
        CREATE TABLE IF NOT EXISTS analysis_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            image_name TEXT,
            product_count INTEGER,
            empty_count INTEGER,
            status TEXT
        )
        '''
        cursor.execute(create_query)
        conn.commit()
        conn.close()
        print(f"Checking Database: Connected to '{self.db_name}'")

    def log_analysis(self, image_name, product_count, empty_count, status):
        """Inserts a new analysis record into the database."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        insert_query = '''
        INSERT INTO analysis_logs (timestamp, image_name, product_count, empty_count, status)
        VALUES (?, ?, ?, ?, ?)
        '''
        
        cursor.execute(insert_query, (timestamp, image_name, product_count, empty_count, status))
        conn.commit()
        conn.close()
        print(f"💾 Database Log Saved: {status} (Gaps: {empty_count})")

    def fetch_recent_logs(self, limit=5):
        """Fetches the most recent logs for verification."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        query = "SELECT * FROM analysis_logs ORDER BY id DESC LIMIT ?"
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        
        conn.close()
        return rows