import mysql.connector
from mysql.connector import pooling
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
import time

def get_connection(retries=3, delay=1):
    """Get DB connection with retry logic for Railway idle disconnects."""
    for attempt in range(retries):
        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                connection_timeout=10,
                autocommit=False,
            )
            return conn
        except mysql.connector.Error as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise e

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    tables = [

        # ── USERS ──────────────────────────────────────────────
        """
        CREATE TABLE IF NOT EXISTS users (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            name          VARCHAR(100) NOT NULL,
            email         VARCHAR(100) UNIQUE NOT NULL,
            password      VARCHAR(255) NOT NULL,
            role          ENUM('admin','worker','critical','citizen') NOT NULL,
            zone          VARCHAR(100),
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,

        # ── BINS ───────────────────────────────────────────────
        """
        CREATE TABLE IF NOT EXISTS bins (
            bin_id        VARCHAR(10) PRIMARY KEY,
            zone          VARCHAR(100),
            area_type     VARCHAR(50),
            capacity_kg   FLOAT,
            latitude      DOUBLE,
            longitude     DOUBLE,
            fill_percent  FLOAT DEFAULT 0,
            status        ENUM('green','yellow','red') DEFAULT 'green',
            qr_code       VARCHAR(255),
            last_updated  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,

        # ── WEIGHT READINGS ────────────────────────────────────
        """
        CREATE TABLE IF NOT EXISTS weight_readings (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            bin_id        VARCHAR(10),
            weight_kg     FLOAT,
            fill_percent  FLOAT,
            day_of_week   VARCHAR(20),
            time_of_day   VARCHAR(20),
            is_festival   TINYINT(1) DEFAULT 0,
            timestamp     DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bin_id) REFERENCES bins(bin_id)
        )
        """,

        # ── COLLECTIONS ────────────────────────────────────────
        """
        CREATE TABLE IF NOT EXISTS collections (
            id                      INT AUTO_INCREMENT PRIMARY KEY,
            bin_id                  VARCHAR(10),
            worker_id               VARCHAR(10),
            fill_percent_at_collect FLOAT,
            collected_at            DATETIME,
            FOREIGN KEY (bin_id) REFERENCES bins(bin_id)
        )
        """,

        # ── COMPLAINTS ─────────────────────────────────────────
        """
        CREATE TABLE IF NOT EXISTS complaints (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            bin_id          VARCHAR(10),
            citizen_id      INT,
            zone            VARCHAR(100),
            description     TEXT,
            photo_path      VARCHAR(255),
            reason          VARCHAR(100),
            reported_fill   FLOAT,
            status          ENUM('pending','assigned','in_progress','resolved') DEFAULT 'pending',
            assigned_to     VARCHAR(10),
            priority        ENUM('low','medium','high') DEFAULT 'medium',
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
            resolved_at     DATETIME,
            FOREIGN KEY (bin_id) REFERENCES bins(bin_id)
        )
        """,

        # ── WORKERS ────────────────────────────────────────────
        """
        CREATE TABLE IF NOT EXISTS workers (
            worker_id       VARCHAR(10) PRIMARY KEY,
            user_id         INT,
            assigned_zone   VARCHAR(100),
            vehicle_id      VARCHAR(20),
            avg_speed_kmph  FLOAT,
            on_shift        TINYINT(1) DEFAULT 0,
            current_lat     DOUBLE,
            current_lng     DOUBLE,
            last_location_update DATETIME
        )
        """,

        # ── ROUTES ─────────────────────────────────────────────
        """
        CREATE TABLE IF NOT EXISTS routes (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            route_code      VARCHAR(10),
            zone            VARCHAR(100),
            worker_id       VARCHAR(10),
            bins_sequence   TEXT,
            estimated_duration_min INT,
            status          ENUM('pending','active','completed') DEFAULT 'pending',
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,

        # ── ROUTE STOPS ────────────────────────────────────────
        """
        CREATE TABLE IF NOT EXISTS route_stops (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            route_id        INT,
            bin_id          VARCHAR(10),
            sequence_order  INT,
            status          ENUM('pending','collected','skipped') DEFAULT 'pending',
            FOREIGN KEY (route_id) REFERENCES routes(id),
            FOREIGN KEY (bin_id) REFERENCES bins(bin_id)
        )
        """,

        # ── FESTIVALS ──────────────────────────────────────────
        """
        CREATE TABLE IF NOT EXISTS festivals (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            name        VARCHAR(100),
            zone        VARCHAR(100),
            start_date  DATE,
            end_date    DATE,
            created_by  INT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,

        # ── BIN REQUESTS ───────────────────────────────────────
        """
        CREATE TABLE IF NOT EXISTS bin_requests (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            citizen_id  INT,
            area        VARCHAR(200),
            description TEXT,
            status      ENUM('pending','approved','rejected') DEFAULT 'pending',
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,

        # ── NOTIFICATIONS ──────────────────────────────────────
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            user_id     INT,
            message     TEXT,
            type        VARCHAR(50),
            is_read     TINYINT(1) DEFAULT 0,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,

        # ── WORKER LOCATION LOG ────────────────────────────────
        """
        CREATE TABLE IF NOT EXISTS worker_location (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            worker_id   VARCHAR(10),
            latitude    DOUBLE,
            longitude   DOUBLE,
            timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,

        # ── IMPACT LOG ─────────────────────────────────────────
        """
        CREATE TABLE IF NOT EXISTS impact_log (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            log_date    DATE,
            zone        VARCHAR(100),
            km_saved    FLOAT DEFAULT 0,
            fuel_saved  FLOAT DEFAULT 0,
            co2_saved   FLOAT DEFAULT 0,
            overflows_prevented INT DEFAULT 0
        )
        """
    ]

    for sql in tables:
        cursor.execute(sql)
        print(f"✓ Table created")

    conn.commit()
    cursor.close()
    conn.close()
    print("\n✅ All tables created successfully!")

if __name__ == "__main__":
    create_tables()