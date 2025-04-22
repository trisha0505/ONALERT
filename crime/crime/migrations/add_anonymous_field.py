from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# Get the absolute path to the database file
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(os.path.dirname(os.path.dirname(basedir)), 'crime_report.db')
DATABASE_URL = f'sqlite:///{db_path}'

print(f"Using database at: {db_path}")

def upgrade():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # First create the table if it doesn't exist
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS crime_report (
                id INTEGER PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                location VARCHAR(200) NOT NULL,
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                timestamp DATETIME,
                updated_at DATETIME,
                user_id INTEGER,
                status VARCHAR(20),
                notes TEXT,
                evidence_file VARCHAR(255),
                is_verified BOOLEAN,
                verification_status VARCHAR(20),
                action_taken TEXT,
                suspect_description TEXT,
                suspect_sketch VARCHAR(255),
                FOREIGN KEY(user_id) REFERENCES user(id)
            );
        """))
        
        # Create new table with is_anonymous column
        session.execute(text("""
            CREATE TABLE crime_report_new (
                id INTEGER PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                location VARCHAR(200) NOT NULL,
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                timestamp DATETIME,
                updated_at DATETIME,
                user_id INTEGER,
                is_anonymous BOOLEAN DEFAULT FALSE,
                status VARCHAR(20),
                notes TEXT,
                evidence_file VARCHAR(255),
                is_verified BOOLEAN,
                verification_status VARCHAR(20),
                action_taken TEXT,
                suspect_description TEXT,
                suspect_sketch VARCHAR(255),
                FOREIGN KEY(user_id) REFERENCES user(id)
            );
        """))
        
        # Copy data from old table to new table
        session.execute(text("""
            INSERT INTO crime_report_new 
            SELECT id, title, description, location, latitude, longitude, 
                   timestamp, updated_at, user_id, 
                   FALSE as is_anonymous, status, notes, 
                   evidence_file, is_verified, verification_status, 
                   action_taken, suspect_description, suspect_sketch
            FROM crime_report;
        """))
        
        # Drop old table and rename new table
        session.execute(text("DROP TABLE crime_report;"))
        session.execute(text("ALTER TABLE crime_report_new RENAME TO crime_report;"))
        
        session.commit()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Error during migration: {e}")
        session.rollback()
    finally:
        session.close()

def downgrade():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create new table without is_anonymous column
        session.execute(text("""
            CREATE TABLE crime_report_new (
                id INTEGER PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                location VARCHAR(200) NOT NULL,
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                timestamp DATETIME,
                updated_at DATETIME,
                user_id INTEGER NOT NULL,
                status VARCHAR(20),
                notes TEXT,
                evidence_file VARCHAR(255),
                is_verified BOOLEAN,
                verification_status VARCHAR(20),
                action_taken TEXT,
                suspect_description TEXT,
                suspect_sketch VARCHAR(255),
                FOREIGN KEY(user_id) REFERENCES user(id)
            );
        """))
        
        # Copy data from old table to new table
        session.execute(text("""
            INSERT INTO crime_report_new 
            SELECT id, title, description, location, latitude, longitude, 
                   timestamp, updated_at, user_id, status, notes, 
                   evidence_file, is_verified, verification_status, 
                   action_taken, suspect_description, suspect_sketch
            FROM crime_report;
        """))
        
        # Drop old table and rename new table
        session.execute(text("DROP TABLE crime_report;"))
        session.execute(text("ALTER TABLE crime_report_new RENAME TO crime_report;"))
        
        session.commit()
        print("Downgrade completed successfully!")
    except Exception as e:
        print(f"Error during downgrade: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == '__main__':
    upgrade() 