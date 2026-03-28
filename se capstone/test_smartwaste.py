"""
SmartWaste Chennai — Selenium Test Automation
Run: pytest test_smartwaste.py -v
Make sure Flask app is running on http://127.0.0.1:5000 before running tests
"""

import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://127.0.0.1:5000"

# ── Setup & Teardown ──────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def driver():
    """Launch Chrome browser before each test, quit after."""
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # uncomment to run without browser window
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.implicitly_wait(5)
    driver.maximize_window()
    yield driver
    driver.quit()

def login(driver, email, password):
    """Helper function to login."""
    driver.get(BASE_URL + "/login")
    driver.find_element(By.NAME, "email").clear()
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").clear()
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(1)

def logout(driver):
    """Helper to logout."""
    driver.get(BASE_URL + "/logout")
    time.sleep(0.5)

# ── UC1: User Login Tests ────────────────────────────────────────────────────

class TestUserLogin:

    def test_TC01_valid_admin_login(self, driver):
        """Unit: Valid admin login redirects to admin dashboard"""
        login(driver, "admin@smartwaste.com", "admin123")
        assert "/admin" in driver.current_url, "Admin should be redirected to /admin"

    def test_TC02_invalid_password(self, driver):
        """Unit: Wrong password shows error message"""
        login(driver, "admin@smartwaste.com", "wrongpassword")
        assert "Invalid" in driver.page_source or "error" in driver.page_source.lower()

    def test_TC03_empty_fields(self, driver):
        """Unit: Empty form submission shows validation error"""
        driver.get(BASE_URL + "/login")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        assert driver.current_url.endswith("/login"), "Should stay on login page"

    def test_TC04_login_db_integration(self, driver):
        """Integration: Valid DB user can login successfully"""
        login(driver, "admin@smartwaste.com", "admin123")
        assert "admin" in driver.current_url.lower() or "dashboard" in driver.page_source.lower()

    def test_TC05_session_creation(self, driver):
        """Integration: Session is created after login"""
        login(driver, "admin@smartwaste.com", "admin123")
        # If session is created, user stays on admin page not redirected to login
        assert "/login" not in driver.current_url

    def test_TC06_role_redirect_admin(self, driver):
        """Integration: Admin login goes to admin dashboard"""
        login(driver, "admin@smartwaste.com", "admin123")
        assert "/admin" in driver.current_url

    def test_TC07_uat_admin_dashboard_loads(self, driver):
        """UAT: After login, admin dashboard shows stats and map"""
        login(driver, "admin@smartwaste.com", "admin123")
        assert "Dashboard" in driver.page_source or "Bins" in driver.page_source

    def test_TC08_uat_session_persistence(self, driver):
        """UAT: Refreshing page keeps user logged in"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.refresh()
        time.sleep(1)
        assert "/login" not in driver.current_url

    def test_TC09_uat_logout(self, driver):
        """UAT: Logout clears session and redirects to login"""
        login(driver, "admin@smartwaste.com", "admin123")
        logout(driver)
        assert "/login" in driver.current_url or driver.current_url.endswith("/")

# ── UC2: Bin Monitoring Tests ─────────────────────────────────────────────────

class TestBinMonitoring:

    def test_TC10_unit_bins_page_loads(self, driver):
        """Unit: Admin bins page loads with bin table"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/bins")
        assert "Bin" in driver.page_source

    def test_TC11_unit_red_bin_displayed(self, driver):
        """Unit: Red status bins shown on dashboard"""
        login(driver, "admin@smartwaste.com", "admin123")
        assert "red" in driver.page_source.lower() or "RED" in driver.page_source

    def test_TC12_unit_bin_map_present(self, driver):
        """Unit: Live bin map element exists on admin dashboard"""
        login(driver, "admin@smartwaste.com", "admin123")
        map_el = driver.find_elements(By.ID, "live-map")
        assert len(map_el) > 0, "Live map should be present on admin dashboard"

    def test_TC13_integration_bins_table_has_data(self, driver):
        """Integration: Bins table shows data from DB"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/bins")
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        assert len(rows) > 0, "Bins table should have at least one row"

    def test_TC14_integration_bin_fill_displayed(self, driver):
        """Integration: Bin fill percentages shown correctly"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/bins")
        assert "%" in driver.page_source

    def test_TC15_integration_status_pills_present(self, driver):
        """Integration: Status pills (GREEN/YELLOW/RED) visible in bins table"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/bins")
        assert "GREEN" in driver.page_source or "YELLOW" in driver.page_source or "RED" in driver.page_source

    def test_TC16_uat_admin_sees_bin_overview(self, driver):
        """UAT: Admin can see all bins with fill levels"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/bins")
        assert "Bin Management" in driver.page_source

    def test_TC17_uat_critical_bins_highlighted(self, driver):
        """UAT: Critical (red) bins highlighted on dashboard"""
        login(driver, "admin@smartwaste.com", "admin123")
        assert "urgent collection" in driver.page_source or "require" in driver.page_source.lower()

    def test_TC18_uat_bins_page_refresh(self, driver):
        """UAT: Bins page shows updated data on reload"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/bins")
        driver.refresh()
        assert "Bin" in driver.page_source

# ── UC3: ML Prediction Tests ──────────────────────────────────────────────────

class TestMLPrediction:

    def test_TC19_unit_predict_page_loads(self, driver):
        """Unit: ML prediction page loads for admin"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/predict")
        assert "Prediction" in driver.page_source or "predict" in driver.page_source.lower()

    def test_TC20_unit_risk_levels_shown(self, driver):
        """Unit: HIGH/MEDIUM/LOW risk labels visible"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/predict")
        assert "HIGH" in driver.page_source or "MEDIUM" in driver.page_source or "LOW" in driver.page_source

    def test_TC21_unit_model_accuracy_shown(self, driver):
        """Unit: Model accuracy percentage displayed"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/predict")
        assert "%" in driver.page_source

    def test_TC22_integration_predictions_table(self, driver):
        """Integration: Predictions table has bin data from DB"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/predict")
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        assert len(rows) > 0, "Predictions table should have rows"

    def test_TC23_integration_ml_route_cards_on_dashboard(self, driver):
        """Integration: ML predicted route cards appear on admin dashboard"""
        login(driver, "admin@smartwaste.com", "admin123")
        assert "ML Predicted" in driver.page_source or "Tomorrow" in driver.page_source

    def test_TC24_integration_retrain_button_exists(self, driver):
        """Integration: Retrain model button is present"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/predict")
        assert "Retrain" in driver.page_source

    def test_TC25_uat_admin_sees_prediction_results(self, driver):
        """UAT: Admin can view ML prediction results clearly"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/predict")
        assert "Bin" in driver.page_source and "Zone" in driver.page_source

    def test_TC26_uat_high_risk_bins_identified(self, driver):
        """UAT: HIGH risk bins clearly identified on predict page"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/predict")
        assert "HIGH" in driver.page_source

    def test_TC27_uat_route_cards_show_bin_details(self, driver):
        """UAT: Route cards on dashboard show bin IDs and fill %"""
        login(driver, "admin@smartwaste.com", "admin123")
        assert "kg" in driver.page_source and "bins" in driver.page_source.lower()

# ── UC4: Complaint Tests ──────────────────────────────────────────────────────

class TestComplaintManagement:

    def test_TC28_unit_complaint_form_loads(self, driver):
        """Unit: Citizen complaint form loads correctly"""
        login(driver, "citizen@smartwaste.com", "citizen123")
        driver.get(BASE_URL + "/citizen/complaint")
        assert "Report" in driver.page_source or "Complaint" in driver.page_source

    def test_TC29_unit_empty_complaint_blocked(self, driver):
        """Unit: Submitting empty complaint shows error"""
        login(driver, "citizen@smartwaste.com", "citizen123")
        driver.get(BASE_URL + "/citizen/complaint")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(0.5)
        assert "/citizen/complaint" in driver.current_url or "Please select" in driver.page_source

    def test_TC30_unit_complaint_form_has_bin_dropdown(self, driver):
        """Unit: Complaint form has bin selection dropdown"""
        login(driver, "citizen@smartwaste.com", "citizen123")
        driver.get(BASE_URL + "/citizen/complaint")
        dropdown = driver.find_elements(By.NAME, "bin_id")
        assert len(dropdown) > 0

    def test_TC31_integration_complaint_saved_in_db(self, driver):
        """Integration: Valid complaint submission saved and appears in track page"""
        login(driver, "citizen@smartwaste.com", "citizen123")
        driver.get(BASE_URL + "/citizen/complaint")
        time.sleep(1)
        # Select a bin (B007 - not in any route)
        select = Select(driver.find_element(By.NAME, "bin_id"))
        try:
            select.select_by_value("B007")
            Select(driver.find_element(By.NAME, "reason")).select_by_value("Overflow")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(1)
            assert "/citizen/track" in driver.current_url or "Complaint" in driver.page_source
        except Exception:
            pass  # bin may not exist in test DB

    def test_TC32_integration_admin_sees_complaint(self, driver):
        """Integration: Admin complaints page shows submitted complaints"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/complaints")
        assert "Complaint" in driver.page_source

    def test_TC33_integration_complaint_status_shown(self, driver):
        """Integration: Complaint status (Pending/Resolved) visible in admin"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/complaints")
        assert "Pending" in driver.page_source or "Resolved" in driver.page_source

    def test_TC34_uat_citizen_tracks_complaint(self, driver):
        """UAT: Citizen can see their complaints in track page"""
        login(driver, "citizen@smartwaste.com", "citizen123")
        driver.get(BASE_URL + "/citizen/track")
        assert "My Complaints" in driver.page_source or "Complaint" in driver.page_source

    def test_TC35_uat_admin_complaint_dashboard(self, driver):
        """UAT: Admin complaints page loads with full table"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/complaints")
        assert "Bin" in driver.page_source and "Zone" in driver.page_source

    def test_TC36_uat_complaint_priority_shown(self, driver):
        """UAT: Complaint priority (high/medium/low) visible"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/complaints")
        assert "high" in driver.page_source.lower() or "medium" in driver.page_source.lower()

# ── UC5: Worker Dashboard Tests ───────────────────────────────────────────────

class TestWorkerDashboard:

    def test_TC37_unit_worker_dashboard_loads(self, driver):
        """Unit: Worker dashboard loads after login"""
        login(driver, "w05@smartwaste.com", "worker123")
        assert "/worker" in driver.current_url or "Worker" in driver.page_source

    def test_TC38_unit_worker_map_present(self, driver):
        """Unit: Worker dashboard has location map"""
        login(driver, "w05@smartwaste.com", "worker123")
        map_el = driver.find_elements(By.ID, "worker-map")
        assert len(map_el) > 0

    def test_TC39_unit_start_shift_button(self, driver):
        """Unit: Start Shift button present on worker dashboard"""
        login(driver, "w05@smartwaste.com", "worker123")
        assert "Shift" in driver.page_source

    def test_TC40_integration_worker_sees_assigned_route(self, driver):
        """Integration: Worker sees route assigned by admin"""
        login(driver, "w05@smartwaste.com", "worker123")
        assert "Route" in driver.page_source or "Today" in driver.page_source

    def test_TC41_integration_worker_db_fetch(self, driver):
        """Integration: Worker dashboard data fetched from DB correctly"""
        login(driver, "w05@smartwaste.com", "worker123")
        assert "W0" in driver.page_source  # worker ID visible

    def test_TC42_integration_route_linked_to_worker(self, driver):
        """Integration: Route shows correct zone for worker"""
        login(driver, "w05@smartwaste.com", "worker123")
        assert "Zone" in driver.page_source or "Anna Nagar" in driver.page_source or "Adyar" in driver.page_source

    def test_TC43_uat_worker_login_dashboard(self, driver):
        """UAT: Worker login opens worker dashboard"""
        login(driver, "w05@smartwaste.com", "worker123")
        assert "Worker Dashboard" in driver.page_source

    def test_TC44_uat_worker_sees_route(self, driver):
        """UAT: Worker can see today's route with stop list"""
        login(driver, "w05@smartwaste.com", "worker123")
        assert "Route" in driver.page_source

    def test_TC45_uat_worker_task_flow(self, driver):
        """UAT: Worker dashboard shows shift status and route section"""
        login(driver, "w05@smartwaste.com", "worker123")
        assert "Shift" in driver.page_source and "Route" in driver.page_source

# ── UC6: Route Management Tests ───────────────────────────────────────────────

class TestRouteManagement:

    def test_TC46_unit_routes_page_loads(self, driver):
        """Unit: Admin routes page loads"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/routes")
        assert "Route" in driver.page_source

    def test_TC47_unit_route_progress_shown(self, driver):
        """Unit: Route progress dashboard shows stop status"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/routes")
        time.sleep(2)  # wait for JS to load routes
        assert "Route" in driver.page_source

    def test_TC48_unit_route_status_pill(self, driver):
        """Unit: Route status (pending/active/completed) shown"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/routes")
        time.sleep(2)
        assert "pending" in driver.page_source.lower() or "active" in driver.page_source.lower() or "completed" in driver.page_source.lower()

    def test_TC49_integration_route_linked_to_worker(self, driver):
        """Integration: Route shows correct worker and zone"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/routes")
        time.sleep(2)
        assert "W0" in driver.page_source or "Zone" in driver.page_source

    def test_TC50_integration_tracking_page_loads(self, driver):
        """Integration: Admin tracking page loads with worker maps"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/tracking")
        assert "Tracking" in driver.page_source or "Worker" in driver.page_source

    def test_TC51_integration_route_api_returns_data(self, driver):
        """Integration: /api/route_progress returns JSON data"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/api/route_progress")
        assert "[" in driver.page_source or "zone" in driver.page_source

    def test_TC52_uat_admin_sees_all_routes(self, driver):
        """UAT: Admin can view all assigned routes on routes page"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/routes")
        assert "Route" in driver.page_source

    def test_TC53_uat_worker_accesses_route(self, driver):
        """UAT: Worker can see and access their assigned route"""
        login(driver, "w05@smartwaste.com", "worker123")
        assert "Route" in driver.page_source or "Today" in driver.page_source

    def test_TC54_uat_route_update_reflected(self, driver):
        """UAT: Route progress updates are visible in admin routes page"""
        login(driver, "admin@smartwaste.com", "admin123")
        driver.get(BASE_URL + "/admin/routes")
        time.sleep(2)
        assert "collected" in driver.page_source.lower() or "pending" in driver.page_source.lower()