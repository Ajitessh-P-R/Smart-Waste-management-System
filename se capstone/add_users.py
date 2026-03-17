from setup_db import get_connection

def add_users():
    conn   = get_connection()
    cursor = conn.cursor()

    # Fix users table to support critical role
    try:
        cursor.execute("""
            ALTER TABLE users MODIFY COLUMN role ENUM('admin','worker','citizen','critical') NOT NULL
        """)
        print("✓ Users table updated for critical role")
    except Exception as e:
        print(f"  (role column already updated: {e})")

    # Add critical worker account
    try:
        cursor.execute("""
            INSERT IGNORE INTO users (name, email, password, role, zone)
            VALUES ('Critical Response', 'critical@smartwaste.com', 'critical123', 'critical', 'All Zones')
        """)
        print("✓ Critical worker account created")
    except Exception as e:
        print(f"  Critical worker: {e}")

    # Add critical worker to workers table
    cursor.execute("SELECT id FROM users WHERE email='critical@smartwaste.com'")
    u = cursor.fetchone()
    if u:
        try:
            cursor.execute("""
                INSERT IGNORE INTO workers (worker_id, user_id, assigned_zone, vehicle_id, avg_speed_kmph)
                VALUES ('W07', %s, 'All Zones', 'T07', 30)
            """, (u[0],))
            print("✓ Critical worker W07 added to workers table")
        except Exception as e:
            print(f"  W07: {e}")

    # Update existing worker logins with correct user_id links
    worker_emails = [
        ('W01', 'w01@smartwaste.com'),
        ('W02', 'w02@smartwaste.com'),
        ('W03', 'w03@smartwaste.com'),
        ('W04', 'w04@smartwaste.com'),
        ('W05', 'w05@smartwaste.com'),
        ('W06', 'w06@smartwaste.com'),
    ]
    for wid, email in worker_emails:
        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        u = cursor.fetchone()
        if u:
            cursor.execute("UPDATE workers SET user_id=%s WHERE worker_id=%s", (u[0], wid))
            print(f"✓ {wid} linked to {email}")

    conn.commit()
    cursor.close()
    conn.close()

    print("\n✅ All accounts ready!")
    print("\n── All Logins ──────────────────────────────────────────")
    print("Admin    → admin@smartwaste.com      / admin123")
    print("Worker 1 → w01@smartwaste.com        / worker123  (Anna Nagar)")
    print("Worker 2 → w02@smartwaste.com        / worker123  (Tambaram)")
    print("Worker 3 → w03@smartwaste.com        / worker123  (Anna Nagar)")
    print("Worker 4 → w04@smartwaste.com        / worker123  (Velachery)")
    print("Worker 5 → w05@smartwaste.com        / worker123  (Velachery)")
    print("Worker 6 → w06@smartwaste.com        / worker123  (T. Nagar)")
    print("Critical → critical@smartwaste.com   / critical123 (All Zones)")
    print("Citizen  → citizen@smartwaste.com    / citizen123")

if __name__ == '__main__':
    add_users()
