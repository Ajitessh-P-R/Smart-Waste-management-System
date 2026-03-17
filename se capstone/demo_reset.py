"""
demo_reset.py  —  Run before viva: python demo_reset.py
Sets realistic bin fills only. No pre-assigned routes.
Full demo flow: Admin assigns → Worker gets notified → Worker generates → Admin tracks.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setup_db import get_connection
from datetime import datetime

conn   = get_connection()
cursor = conn.cursor()
print("🔄 Starting demo reset...")

# 1. Realistic bin fill levels
bin_fills = {
    'B001':(92,'red'),'B006':(85,'red'),'B011':(67,'yellow'),'B014':(54,'yellow'),'B015':(28,'green'),'B021':(15,'green'),
    'B002':(88,'red'),'B019':(72,'yellow'),'B024':(61,'yellow'),'B025':(35,'green'),
    'B003':(95,'red'),'B013':(78,'yellow'),'B022':(55,'yellow'),'B023':(22,'green'),
    'B004':(91,'red'),'B007':(83,'red'),'B008':(69,'yellow'),'B009':(58,'yellow'),'B016':(31,'green'),'B020':(18,'green'),
    'B005':(87,'red'),'B010':(74,'yellow'),'B012':(62,'yellow'),'B017':(41,'green'),'B018':(19,'green'),
}
for bin_id,(fill,status) in bin_fills.items():
    cursor.execute("UPDATE bins SET fill_percent=%s, status=%s, last_updated=%s WHERE bin_id=%s",(fill,status,datetime.now(),bin_id))
print(f"  ✓ {len(bin_fills)} bins updated with realistic fills")

# 2. All workers off shift (fresh start)
cursor.execute("UPDATE workers SET on_shift=0")
print("  ✓ All workers set off-shift")

# 3. Clear all pending/active routes (keep completed history)
cursor.execute("DELETE FROM route_stops WHERE route_id IN (SELECT id FROM routes WHERE status IN ('pending','active'))")
cursor.execute("DELETE FROM routes WHERE status IN ('pending','active')")
print("  ✓ Pending/active routes cleared")

# 3b. Create 3 fresh demo routes WITH route_stops (needed for citizen route-check)
demo_routes = [
    {'zone':'Adyar',    'worker':'W01', 'bins':['B001','B006','B011','B014'], 'est_min':32},
    {'zone':'Tambaram', 'worker':'W02', 'bins':['B002','B019','B024'],        'est_min':24},
    {'zone':'Velachery','worker':'W04', 'bins':['B003','B013','B022'],        'est_min':24},
]
for r in demo_routes:
    sequence = ' -> '.join(r['bins'])
    cursor.execute("""
        INSERT INTO routes (zone, worker_id, bins_sequence, estimated_duration_min, status, created_at)
        VALUES (%s,%s,%s,%s,'pending',%s)
    """, (r['zone'], r['worker'], sequence, r['est_min'], datetime.now()))
    route_id = cursor.lastrowid
    for i, bid in enumerate(r['bins']):
        cursor.execute("""
            INSERT INTO route_stops (route_id, bin_id, sequence_order, status)
            VALUES (%s,%s,%s,'pending')
        """, (route_id, bid, i+1))
print("  ✓ 3 demo routes created with route_stops (Adyar/W01, Tambaram/W02, Velachery/W04)")

# 4. Add demo complaints (3 complaints on bins NOT in any assigned route)
# Routes use: Adyar(B001,B006,B011,B014), Tambaram(B002,B019,B024), Velachery(B003,B013,B022)
# Using B007 (Anna Nagar), B005 (T.Nagar), B008 (Anna Nagar) — none are in any route
cursor.execute("DELETE FROM complaints")  # clear ALL for clean demo
demo_complaints = [
    ('B007', 1, 'Bin overflowing near school gate', 'Overflow',       83, 'high'),
    ('B005', 1, 'Bad smell, lid broken',             'Bad Smell',      87, 'high'),
    ('B008', 1, 'Waste scattered around bin',        'Not Collected',  69, 'medium'),
]
for (bin_id, cid, desc, reason, fill, priority) in demo_complaints:
    cursor.execute("""
        INSERT INTO complaints (bin_id, citizen_id, description, reason, reported_fill, priority, status, created_at)
        VALUES (%s,%s,%s,%s,%s,%s,'pending',%s)
    """, (bin_id, cid, desc, reason, fill, priority, datetime.now()))
print("  ✓ 3 demo complaints added (B007, B005, B008 — not in any worker route)")

# 5. Log weight readings for ML
now=datetime.now(); day=now.strftime('%A')
cursor.execute("SELECT bin_id, capacity_kg FROM bins")
all_bins=cursor.fetchall()
for row in all_bins:
    bid=row[0]; cap=row[1] or 100
    fill=bin_fills.get(bid,(30,'green'))[0]
    weight=round((fill/100)*cap,1)
    cursor.execute("""
        INSERT INTO weight_readings (bin_id,weight_kg,fill_percent,day_of_week,time_of_day,timestamp)
        VALUES (%s,%s,%s,%s,'Morning',%s)
    """,(bid,weight,fill,day,now))
print(f"  ✓ Weight readings logged for ML")

conn.commit(); cursor.close(); conn.close()
print()
print("✅ Demo reset complete! Ready for viva.")
print()
print("Demo flow to show:")
print("  1. Login as ADMIN → see ML predicted routes on dashboard")
print("  2. Pick a worker from dropdown → click Assign → card disappears")
print("  3. Login as WORKER → see notification popup → click Generate Route")
print("  4. Worker map shows road path with numbered stops")
print("  5. Admin opens Tracking → sees worker location vs route")
print("  6. Admin opens Routes → see live stop-by-stop progress")
print("  7. Worker clicks Collect on each stop → Routes page updates live")
print("  8. Login as CRITICAL WORKER → sees 3 complaint bins (B007, B005, B008)")
print("  9. Click Generate Route → map shows all 3 bins → collect each → complaints auto-resolve")
print("  10. If citizen files a new complaint while critical route is active → bin auto-added to route")