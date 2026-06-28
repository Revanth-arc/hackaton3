import sqlite3
import uuid
import logging
from datetime import datetime
from ai.validator import ExtractedEntitiesDTO

logger = logging.getLogger(__name__)
DB_PATH = "firstruct.db"

def init_db():
    """Initializes the SQLite database schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS firs (
        id TEXT PRIMARY KEY,
        complaint_id TEXT,
        victim_name TEXT,
        accused_name TEXT,
        crime_type TEXT,
        incident_date TEXT,
        incident_time TEXT,
        location TEXT,
        summary TEXT,
        status TEXT,
        created_at TEXT
    )''')
    
    tables = {
        'vehicles': 'vehicle_number',
        'weapons': 'weapon_type',
        'stolen_items': 'item_description',
        'ipc_sections': 'section_code'
    }
    
    for table, col in tables.items():
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {table} (
            fir_id TEXT,
            {col} TEXT,
            FOREIGN KEY(fir_id) REFERENCES firs(id)
        )''')
        
    conn.commit()
    conn.close()
    logger.info("Database initialized.")

def save_fir_draft(dto: ExtractedEntitiesDTO, complaint_id: str) -> str:
    """Saves a validated DTO into the database with 'Draft' status."""
    fir_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''INSERT INTO firs 
            (id, complaint_id, victim_name, accused_name, crime_type, incident_date, incident_time, location, summary, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Draft', ?)''', 
            (fir_id, complaint_id, dto.victim, dto.accused, dto.crime_type, dto.date, dto.time, dto.location, dto.summary, datetime.now().isoformat())
        )
        
        for v in dto.vehicles:
            cursor.execute('INSERT INTO vehicles (fir_id, vehicle_number) VALUES (?, ?)', (fir_id, v))
        for w in dto.weapons:
            cursor.execute('INSERT INTO weapons (fir_id, weapon_type) VALUES (?, ?)', (fir_id, w))
        for item in dto.stolen_items:
            cursor.execute('INSERT INTO stolen_items (fir_id, item_description) VALUES (?, ?)', (fir_id, item))
        for sec in dto.sections:
            cursor.execute('INSERT INTO ipc_sections (fir_id, section_code) VALUES (?, ?)', (fir_id, sec))
            
        conn.commit()
        logger.info(f"Saved FIR draft {fir_id}")
        return fir_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to save FIR draft: {e}")
        raise
    finally:
        conn.close()

def search_firs(query: str):
    """Basic search implementation."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM firs WHERE 
        victim_name LIKE ? OR accused_name LIKE ? OR crime_type LIKE ? OR location LIKE ?''', 
        (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
    results = cursor.fetchall()
    conn.close()
    return results
