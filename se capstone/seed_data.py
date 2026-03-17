import csv
import os
from datetime import datetime
from setup_db import get_connection

BASE = os.path.dirname(os.path.abspath(__file__))

def seed_bins():
    conn = get_connection()
    cursor = conn.cursor()
    with open(os.path.join(BASE, "bins.csv")) as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT IGNORE INTO bins
                (bin_id, zone, area_type, capacity_kg, latitude, longitude, fill_percent, status)
                VALUES (%s,%s,%s,%s,%s,%s, 0, 'green')
            """, (row['bin_id'], row['zone'], row['area_type'],
                  float(row['capacity_kg']), float(row['latitude']), float(row['longitude'])))
    conn.commit()
    cursor.close(); conn.close()
    print("✓ Bins seeded")

def seed_workers():
    conn = get_connection()
    cursor = conn.cursor()
    with open(os.path.join(BASE, "workers.csv")) as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT IGNORE INTO workers
                (worker_id, assigned_zone, vehicle_id, avg_speed_kmph)
                VALUES (%s,%s,%s,%s)
            """, (row['worker_id'], row['assigned_zone'],
                  row['vehicle_id'], float(row['avg_speed_kmph'])))
    conn.commit()
    cursor.close(); conn.close()
    print("✓ Workers seeded")

def seed_weight_readings():
    conn = get_connection()
    cursor = conn.cursor()
    with open(os.path.join(BASE, "weight_readings.csv")) as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT INTO weight_readings
                (bin_id, weight_kg, fill_percent, day_of_week, time_of_day, timestamp)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (row['bin_id'], float(row['weight_kg']), float(row['fill_percent']),
                  row['day_of_week'], row['time_of_day'], row['timestamp']))
    conn.commit()
    cursor.close(); conn.close()
    print("✓ Weight readings seeded")

def seed_collections():
    conn = get_connection()
    cursor = conn.cursor()
    with open(os.path.join(BASE, "collections.csv")) as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT INTO collections
                (bin_id, worker_id, fill_percent_at_collect, collected_at)
                VALUES (%s,%s,%s,%s)
            """, (row['bin_id'], row['worker_id'],
                  float(row['fill_percent_at_collection']), row['collection_time']))
    conn.commit()
    cursor.close(); conn.close()
    print("✓ Collections seeded")

def seed_complaints():
    conn = get_connection()
    cursor = conn.cursor()
    with open(os.path.join(BASE, "complaints.csv")) as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT INTO complaints
                (bin_id, zone, reason, reported_fill, status, created_at)
                VALUES (%s,%s,%s,%s,'resolved',%s)
            """, (row['bin_id'], row['zone'], row['reason'],
                  float(row['reported_fill_percent']), row['complaint_time']))
    conn.commit()
    cursor.close(); conn.close()
    print("✓ Complaints seeded")

def seed_routes():
    conn = get_connection()
    cursor = conn.cursor()
    with open(os.path.join(BASE, "routes.csv")) as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT IGNORE INTO routes
                (route_code, zone, bins_sequence, estimated_duration_min, status)
                VALUES (%s,%s,%s,%s,'completed')
            """, (row['route_id'], row['zone'],
                  row['bins_sequence'], int(row['estimated_duration_min'])))
    conn.commit()
    cursor.close(); conn.close()
    print("✓ Routes seeded")

def seed_default_users():
    conn = get_connection()
    cursor = conn.cursor()
    # Default admin + one citizen for testing
    users = [
        ("Admin User",   "admin@smartwaste.com",  "admin123",  "admin",   "All Zones"),
        ("Test Citizen", "citizen@smartwaste.com", "citizen123","citizen", "Adyar"),
    ]
    for name, email, pwd, role, zone in users:
        cursor.execute("""
            INSERT IGNORE INTO users (name, email, password, role, zone)
            VALUES (%s,%s,%s,%s,%s)
        """, (name, email, pwd, role, zone))

    # Create user accounts for each worker and link them
    worker_users = [
        ("Worker W01","w01@smartwaste.com","worker123","worker","Anna Nagar","W01"),
        ("Worker W02","w02@smartwaste.com","worker123","worker","Tambaram","W02"),
        ("Worker W03","w03@smartwaste.com","worker123","worker","Anna Nagar","W03"),
        ("Worker W04","w04@smartwaste.com","worker123","worker","Velachery","W04"),
        ("Worker W05","w05@smartwaste.com","worker123","worker","T. Nagar","W05"),
        ("Worker W06","w06@smartwaste.com","worker123","worker","Adyar","W06"),
    ]
    for name, email, pwd, role, zone, wid in worker_users:
        cursor.execute("""
            INSERT IGNORE INTO users (name, email, password, role, zone)
            VALUES (%s,%s,%s,%s,%s)
        """, (name, email, pwd, role, zone))
        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        result = cursor.fetchone()
        if result:
            cursor.execute("""
                UPDATE workers SET user_id=%s WHERE worker_id=%s
            """, (result[0], wid))

    conn.commit()
    cursor.close(); conn.close()
    print("✓ Default users seeded")

if __name__ == "__main__":
    print("🌱 Seeding database...\n")
    seed_bins()
    seed_workers()
    seed_weight_readings()
    seed_collections()
    seed_complaints()
    seed_routes()
    seed_default_users()
    print("\n✅ All data seeded successfully!")
    print("\n── Default Logins ──────────────────────")
    print("Admin   → admin@smartwaste.com   / admin123")
    print("Worker  → w01@smartwaste.com     / worker123")
    print("Citizen → citizen@smartwaste.com / citizen123")
