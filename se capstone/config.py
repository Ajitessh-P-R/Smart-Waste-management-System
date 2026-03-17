import os
from datetime import timedelta

DB_HOST     = "localhost"
DB_PORT     = 3306
DB_USER     = "root"
DB_PASSWORD = "Kiruthi@2008"
DB_NAME     = "smartwaste"

SECRET_KEY  = "smartwaste_chennai_2024"

# Session stays alive for 8 hours
SESSION_PERMANENT          = True
PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

# Fill threshold % — alert triggers above this
FILL_THRESHOLD = 80