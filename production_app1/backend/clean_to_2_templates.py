"""
Clean Templates to Just 2 Professional Ones
Protecting all functionality while keeping only the best templates
"""
import sqlite3

def clean_to_2_templates():
    """Keep only 2 professional templates"""
    
    print("🧹 CLEANING TO 2 PROFESSIONAL TEMPLATES")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('sender.db')
        cursor = conn.cursor()
        
        # Show current count
        cursor.execute("SELECT COUNT(*) FROM spinner_templates")
        total_before = cursor.fetchone()[0]
        print(f"📊 Templates before: {total_before}")
        
        # Delete all existing templates
        cursor.execute("DELETE FROM spinner_templates")
        
        # Insert 2 professional templates
        templates = [
            {
                'name': 'Professional Introduction',
                'description': 'A professional introduction email template for business outreach',
                'subject': '{Hello|Hi|Greetings} {first_name}, let\'s connect!',
                'content': '''Hello {first_name},

I hope this email finds you well. My name is {sender_name} and I wanted to reach out to introduce myself and explore potential opportunities for collaboration.

{I noticed|I saw|I came across} your work at {company} and was impressed by your expertise in the field. I believe there could be some great synergies between what we do.

Would you be interested in a brief call to discuss this further? I'm available {this week|next week} at your convenience.

Best regards,
{sender_name}'''
            },
            {
                'name': 'Follow-up Email',
                'description': 'A professional follow-up email template for continued engagement',
                'subject': 'Following up on our {conversation|discussion|chat}',
                'content': '''Hi {first_name},

I wanted to follow up on our recent {conversation|discussion|meeting} and see if you had any questions about what we discussed.

{I'm excited|I'm looking forward|I'm eager} to move forward with the next steps and would love to hear your thoughts on how we can proceed.

Please let me know if you need any additional information or if there's a good time for us to connect again.

Looking forward to hearing from you!

Best regards,
{sender_name}'''
            }
        ]
        
        for template in templates:
            cursor.execute("""
                INSERT INTO spinner_templates (name, description, subject, content, created_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (template['name'], template['description'], template['subject'], template['content']))
        
        # Show final count
        cursor.execute("SELECT COUNT(*) FROM spinner_templates")
        total_after = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        print(f"✅ CLEANUP COMPLETE:")
        print(f"   • Templates before: {total_before}")
        print(f"   • Templates after: {total_after}")
        print(f"   • Removed: {total_before - total_after}")
        print(f"   • Clean professional templates ready!")
        
        return True
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False

def show_final_templates():
    """Show the final 2 templates"""
    
    try:
        conn = sqlite3.connect('sender.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, description FROM spinner_templates ORDER BY id")
        templates = cursor.fetchall()
        
        print(f"\n📋 FINAL TEMPLATES ({len(templates)}):")
        for i, (name, description) in enumerate(templates, 1):
            print(f"   {i}. {name}")
            print(f"      {description}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error showing templates: {e}")

if __name__ == "__main__":
    print("⚠️ This will delete ALL templates and create 2 clean professional ones!")
    print("Are you sure? (y/N): ", end="")
    
    confirm = input().lower()
    if confirm == 'y':
        if clean_to_2_templates():
            show_final_templates()
            print("\n🎉 Template cleanup successful!")
            print("You now have 2 clean, professional templates for testing!")
        else:
            print("❌ Cleanup failed - check errors above")
    else:
        print("❌ Cleanup cancelled")