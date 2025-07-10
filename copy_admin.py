import os
import sqlite3
import shutil
from werkzeug.security import generate_password_hash

# Your main database path (from python app.py)
main_db = "ct_install.db"

def create_admin_user():
    """Create admin user directly in the database"""
    try:
        conn = sqlite3.connect(main_db)
        cursor = conn.cursor()
        
        # Check if admin user already exists
        cursor.execute("SELECT * FROM ab_user WHERE username = 'admin'")
        if cursor.fetchone():
            print("Admin user already exists in main database")
            return
        
        # Hash the password
        password_hash = generate_password_hash("admin123")
        
        # Insert admin user
        cursor.execute("""
            INSERT INTO ab_user (first_name, last_name, username, password, email, active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("Admin", "User", "admin", password_hash, "admin@ct-scanner.com", 1))
        
        # Get the user ID
        user_id = cursor.lastrowid
        
        # Add admin role (role ID 1 is usually Admin)
        cursor.execute("INSERT INTO ab_user_role (user_id, role_id) VALUES (?, ?)", (user_id, 1))
        
        conn.commit()
        conn.close()
        
        print("✅ Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_admin_user()
