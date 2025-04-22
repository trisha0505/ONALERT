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
        # Check if the sos_alert table exists
        result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='sos_alert';"))
        table_exists = result.fetchone() is not None
        
        if table_exists:
            # Create new table with is_anonymous column and nullable user_id
            session.execute(text("""
                CREATE TABLE sos_alert_new (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    location VARCHAR(200),
                    latitude FLOAT,
                    longitude FLOAT,
                    timestamp DATETIME,
                    resolved_at DATETIME,
                    status VARCHAR(20),
                    message TEXT,
                    responder_id INTEGER,
                    responder_notes TEXT,
                    is_anonymous BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY(user_id) REFERENCES user(id),
                    FOREIGN KEY(responder_id) REFERENCES user(id)
                );
            """))
            
            # Copy data from old table to new table
            session.execute(text("""
                INSERT INTO sos_alert_new 
                SELECT id, user_id, location, latitude, longitude, 
                       timestamp, resolved_at, status, message, 
                       responder_id, responder_notes, FALSE as is_anonymous
                FROM sos_alert;
            """))
            
            # Drop old table and rename new table
            session.execute(text("DROP TABLE sos_alert;"))
            session.execute(text("ALTER TABLE sos_alert_new RENAME TO sos_alert;"))
        else:
            # Create the sos_alert table with the new schema
            session.execute(text("""
                CREATE TABLE sos_alert (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    location VARCHAR(200),
                    latitude FLOAT,
                    longitude FLOAT,
                    timestamp DATETIME,
                    resolved_at DATETIME,
                    status VARCHAR(20),
                    message TEXT,
                    responder_id INTEGER,
                    responder_notes TEXT,
                    is_anonymous BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY(user_id) REFERENCES user(id),
                    FOREIGN KEY(responder_id) REFERENCES user(id)
                );
            """))
        
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
        # Check if the sos_alert table exists
        result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='sos_alert';"))
        table_exists = result.fetchone() is not None
        
        if table_exists:
            # Create new table without is_anonymous column and non-nullable user_id
            session.execute(text("""
                CREATE TABLE sos_alert_new (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    location VARCHAR(200),
                    latitude FLOAT,
                    longitude FLOAT,
                    timestamp DATETIME,
                    resolved_at DATETIME,
                    status VARCHAR(20),
                    message TEXT,
                    responder_id INTEGER,
                    responder_notes TEXT,
                    FOREIGN KEY(user_id) REFERENCES user(id),
                    FOREIGN KEY(responder_id) REFERENCES user(id)
                );
            """))
            
            # Copy data from old table to new table, excluding anonymous alerts
            session.execute(text("""
                INSERT INTO sos_alert_new 
                SELECT id, user_id, location, latitude, longitude, 
                       timestamp, resolved_at, status, message, 
                       responder_id, responder_notes
                FROM sos_alert
                WHERE user_id IS NOT NULL;
            """))
            
            # Drop old table and rename new table
            session.execute(text("DROP TABLE sos_alert;"))
            session.execute(text("ALTER TABLE sos_alert_new RENAME TO sos_alert;"))
            
            session.commit()
            print("Downgrade completed successfully!")
        else:
            print("SOS alert table does not exist. Nothing to downgrade.")
    except Exception as e:
        print(f"Error during downgrade: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == '__main__':
    upgrade() 