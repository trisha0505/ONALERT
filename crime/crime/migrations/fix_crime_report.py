import sqlite3
import os

# Get the absolute path to the database file
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(os.path.dirname(os.path.dirname(basedir)), 'crime_report.db')

print(f"Using database at: {db_path}")

def add_column():
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(crime_report)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_anonymous' not in columns:
            # Add the is_anonymous column
            cursor.execute("ALTER TABLE crime_report ADD COLUMN is_anonymous BOOLEAN DEFAULT FALSE")
            conn.commit()
            print("Successfully added is_anonymous column!")
        else:
            print("Column is_anonymous already exists.")
            
        # Verify the column was added
        cursor.execute("PRAGMA table_info(crime_report)")
        columns = [column[1] for column in cursor.fetchall()]
        print("\nCurrent columns in crime_report table:")
        for column in columns:
            print(f"- {column}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    add_column()
