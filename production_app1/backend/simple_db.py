"""
Simple database helper for direct database access
"""
import os
import sqlite3

def get_connection(db_name='database.db'):
    """Get a direct database connection without Flask g object"""
    db_path = os.path.join(os.path.dirname(__file__), db_name)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def query_db(query, args=(), one=False, db_name='database.db'):
    """Query the database directly"""
    conn = get_connection(db_name)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=(), db_name='database.db'):
    """Execute a database command directly"""
    conn = get_connection(db_name)
    try:
        cur = conn.cursor()
        cur.execute(query, args)
        conn.commit()
        last_id = cur.lastrowid
        cur.close()
        return last_id
    except Exception as e:
        print(f"Database error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def fetch_db(query, args=(), one=False, db_name='database.db'):
    """Fetch data from database"""
    return query_db(query, args, one, db_name)