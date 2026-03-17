from setup_db import get_connection

# Real Chennai coordinates for each bin zone
# All verified to be on land within Chennai city limits
BIN_COORDS = {
    'B001': (13.0067, 80.2206),  # Adyar
    'B002': (12.9249, 80.1000),  # Tambaram
    'B003': (12.9816, 80.2209),  # Velachery
    'B004': (13.0850, 80.2101),  # Anna Nagar
    'B005': (13.0418, 80.2341),  # T. Nagar
    'B006': (13.0012, 80.2565),  # Adyar
    'B007': (13.0900, 80.2000),  # Anna Nagar
    'B008': (13.0750, 80.2150),  # Anna Nagar
    'B009': (13.0800, 80.2050),  # Anna Nagar
    'B010': (13.0380, 80.2300),  # T. Nagar
    'B011': (13.0100, 80.2500),  # Adyar
    'B012': (13.0450, 80.2280),  # T. Nagar
    'B013': (12.9750, 80.2180),  # Velachery
    'B014': (13.0050, 80.2400),  # Adyar
    'B015': (13.0150, 80.2150),  # Adyar
    'B016': (13.0880, 80.2080),  # Anna Nagar
    'B017': (13.0350, 80.2380),  # T. Nagar
    'B018': (13.0500, 80.2320),  # T. Nagar
    'B019': (12.9300, 80.1200),  # Tambaram
    'B020': (13.0820, 80.2120),  # Anna Nagar
    'B021': (13.0020, 80.2480),  # Adyar
    'B022': (12.9700, 80.2250),  # Velachery
    'B023': (12.9850, 80.2200),  # Velachery
    'B024': (12.9200, 80.1100),  # Tambaram
    'B025': (12.9350, 80.1150),  # Tambaram
}

def fix_coords():
    conn   = get_connection()
    cursor = conn.cursor()
    for bin_id, (lat, lng) in BIN_COORDS.items():
        cursor.execute("""
            UPDATE bins SET latitude=%s, longitude=%s WHERE bin_id=%s
        """, (lat, lng, bin_id))
        print(f"✓ Fixed {bin_id} → ({lat}, {lng})")
    conn.commit()
    cursor.close()
    conn.close()
    print("\n✅ All bin coordinates fixed to real Chennai locations!")

if __name__ == '__main__':
    fix_coords()
