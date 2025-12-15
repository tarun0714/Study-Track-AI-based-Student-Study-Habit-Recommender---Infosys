
import sqlite3

def add_columns():
    try:
        conn = sqlite3.connect('study_reco.db')
        cursor = conn.cursor()
        
        # Check if columns exist
        cursor.execute("PRAGMA table_info(students)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'cluster_label' not in columns:
            print("Adding cluster_label column...")
            cursor.execute("ALTER TABLE students ADD COLUMN cluster_label TEXT")
            
        if 'cluster_insights' not in columns:
            print("Adding cluster_insights column...")
            cursor.execute("ALTER TABLE students ADD COLUMN cluster_insights TEXT")
            
        conn.commit()
        conn.close()
        print("Database updated successfully.")
    except Exception as e:
        print(f"Error updating database: {e}")

if __name__ == "__main__":
    add_columns()
