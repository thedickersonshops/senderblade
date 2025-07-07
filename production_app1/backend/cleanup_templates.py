#!/usr/bin/env python3
"""
Clean up excess templates - keep only essential ones
"""
import sqlite3

def cleanup_templates():
    """Remove excess templates, keep only a few essential ones"""
    try:
        conn = sqlite3.connect('sender.db')
        cursor = conn.cursor()
        
        # Check all possible template tables
        template_tables = ['email_templates', 'templates', 'message_templates']
        
        for table_name in template_tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if cursor.fetchone():
                # Count current templates
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                current_count = cursor.fetchone()[0]
                print(f"📊 Found {current_count} templates in {table_name}")
                
                if current_count > 8:
                    # Keep only the first 8 templates (most recent)
                    cursor.execute(f"""
                        DELETE FROM {table_name} 
                        WHERE id NOT IN (
                            SELECT id FROM {table_name} 
                            ORDER BY created_at DESC 
                            LIMIT 8
                        )
                    """)
                    
                    # Get new count
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    new_count = cursor.fetchone()[0]
                    
                    conn.commit()
                    print(f"🗑️ Cleaned {table_name}: {current_count} → {new_count}")
                else:
                    print(f"✅ {table_name} count is reasonable")
        
        # Also check spinner templates
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='spinner_templates'")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM spinner_templates")
            spinner_count = cursor.fetchone()[0]
            print(f"📊 Found {spinner_count} spinner templates")
            
            if spinner_count > 8:
                cursor.execute("""
                    DELETE FROM spinner_templates 
                    WHERE id NOT IN (
                        SELECT id FROM spinner_templates 
                        ORDER BY id DESC 
                        LIMIT 8
                    )
                """)
                cursor.execute("SELECT COUNT(*) FROM spinner_templates")
                new_spinner_count = cursor.fetchone()[0]
                conn.commit()
                print(f"🗑️ Cleaned spinner_templates: {spinner_count} → {new_spinner_count}")
        

        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error cleaning templates: {e}")

if __name__ == '__main__':
    cleanup_templates()