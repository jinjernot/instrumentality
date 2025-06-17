import requests
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import threading

# --- Configuration ---
URLS_TO_MONITOR = [
    "https://partner.hp.com/group/upp-na/home",
    "https://partner.hp.com/group/upp-lar/home",
    "https://partner.hp.com/group/upp-apj/home",
    "https://partner.hp.com/group/upp-ww/home",
    "https://partner.hp.com/group/upp-emea/home"
]

# Notification Settings (Example: Email)
# IMPORTANT: Replace with your actual email credentials and recipient.
# For Gmail, you'll likely need an "App password" due to security.
SENDER_EMAIL = "your_email@example.com"
SENDER_PASSWORD = "your_email_password"
RECEIVER_EMAIL = "recipient_email@example.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

CHECK_INTERVAL_SECONDS = 300  # Check every 5 minutes (adjust as needed)
TIMEOUT_SECONDS = 10  # How long to wait for a response from the URL

# Shared dictionary to store URL statuses
# In a real application, consider a more robust shared state (e.g., Redis, database, multiprocessing.Manager)
# For this example, we'll use a simple dictionary, assuming proper thread management.
url_statuses = {}
status_lock = threading.Lock() # To safely update the shared dictionary

def send_notification(subject, body):
    """Sends an email notification."""
    print(f"Attempting to send email notification: {subject}")
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"[{datetime.now()}] Notification sent: {subject}")
    except Exception as e:
        print(f"[{datetime.now()}] Error sending notification: {e}. Please ensure SENDER_EMAIL and SENDER_PASSWORD are correct and app passwords are used if necessary.")

def check_url_status(url):
    """
    Checks the HTTP status of a given URL.
    Returns True if the status is 200 (OK), False otherwise.
    """
    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
        if response.status_code == 200:
            return True, f"UP (Status: {response.status_code})"
        else:
            return False, f"DOWN (Status: {response.status_code})"
    except requests.exceptions.Timeout:
        return False, f"DOWN (Timeout after {TIMEOUT_SECONDS} seconds)"
    except requests.exceptions.ConnectionError:
        return False, "DOWN (Connection Error)"
    except requests.exceptions.RequestException as e:
        return False, f"DOWN (Request Error: {e})"

def monitor_urls_background_task():
    """
    Continuously monitors the specified URLs and updates their statuses in the shared dictionary.
    Sends notifications if any URL status changes.
    """
    print(f"[{datetime.now()}] Starting URL monitor background task...")
    
    # Initialize statuses on first run
    with status_lock:
        for url in URLS_TO_MONITOR:
            is_up, message = check_url_status(url)
            url_statuses[url] = {"is_up": is_up, "message": message, "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            if not is_up:
                print(f"[{datetime.now()}] Initial check: {url} is {message}")
                subject = f"Initial Alert: URL DOWN - {url}"
                body = (f"The following URL was found down during initial check:\n\n"
                        f"URL: {url}\n"
                        f"Status: {message}\n"
                        f"Time: {datetime.now()}")
                send_notification(subject, body)
            else:
                print(f"[{datetime.now()}] Initial check: {url} is {message}")

    while True:
        current_statuses = {}
        for url in URLS_TO_MONITOR:
            is_up, message = check_url_status(url)
            current_statuses[url] = {"is_up": is_up, "message": message, "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

            with status_lock:
                # Check for status changes
                previous_is_up = url_statuses.get(url, {}).get("is_up")
                
                if is_up != previous_is_up:
                    if is_up:
                        subject = f"URL RECOVERED - {url}"
                        body = (f"The following URL has recovered:\n\n"
                                f"URL: {url}\n"
                                f"Status: {message}\n"
                                f"Time: {datetime.now()}")
                        send_notification(subject, body)
                    else:
                        subject = f"URGENT: URL DOWN - {url}"
                        body = (f"The following URL is currently unreachable or returning an error:\n\n"
                                f"URL: {url}\n"
                                f"Status: {message}\n"
                                f"Time: {datetime.now()}")
                        send_notification(subject, body)
                
                # Update the shared status
                url_statuses[url] = current_statuses[url]

            print(f"[{datetime.now()}] {url} is {current_statuses[url]['message']}")

        print(f"[{datetime.now()}] Next check in {CHECK_INTERVAL_SECONDS} seconds...")
        time.sleep(CHECK_INTERVAL_SECONDS)

# This global dictionary will be imported by the Flask app to display statuses
# and accessed by the monitoring thread to update.
# A threading.Lock is used to ensure thread-safe access.
_url_monitor_thread = None

def start_monitor_thread():
    """Starts the URL monitoring in a separate daemon thread."""
    global _url_monitor_thread
    if _url_monitor_thread is None or not _url_monitor_thread.is_alive():
        _url_monitor_thread = threading.Thread(target=monitor_urls_background_task, daemon=True)
        _url_monitor_thread.start()
        print(f"[{datetime.now()}] URL monitor background thread started.")
    else:
        print(f"[{datetime.now()}] URL monitor background thread already running.")

if __name__ == "__main__":
    # If run as a standalone script, start monitoring directly
    # For Flask integration, this part would be called from main.py
    start_monitor_thread()
    # Keep the main thread alive if running standalone
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Monitoring stopped by user.")