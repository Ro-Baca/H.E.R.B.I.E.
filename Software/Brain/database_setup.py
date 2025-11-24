import sqlite3
from datetime import datetime

# --- Configuration ---
DATABASE_FILE = "herbie_data.db"

def create_database():
    """
    Connects to the database and creates the 'readings' table if it doesn't exist.
    """
    # 'connect' will create the file if it's not there
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # SQL command to create the table
    # Using "IF NOT EXISTS" prevents errors if we run this script again
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        moisture REAL,
        temperature REAL,
        humidity REAL,
        light REAL
    )
    """)

    # Save the changes and close the connection
    conn.commit()
    conn.close()
    print(f"Database '{DATABASE_FILE}' and table 'readings' are ready.")

def add_test_reading():
    """
    Adds a single row of sample data to the 'readings' table.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Get the current time and format it
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Sample data
    sample_moisture = 55.5
    sample_temp = 23.4
    sample_humidity = 60.1
    sample_light = 1500.0

    # SQL command to insert data
    # Using placeholders (?) is a security best practice
    cursor.execute("""
    INSERT INTO readings (timestamp, moisture, temperature, humidity, light)
    VALUES (?, ?, ?, ?, ?)
    """, (now, sample_moisture, sample_temp, sample_humidity, sample_light))

    conn.commit()
    conn.close()
    print("Added one sample reading to the database.")


# --- Main execution block ---
if __name__ == "__main__":
    create_database()
    add_test_reading()
