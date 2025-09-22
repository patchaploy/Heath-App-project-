import os
import pickle
import hashlib
from google.colab import drive

# --- Google Drive Connection ---
# This part needs to be run in an environment like Google Colab.
# If running locally, you would adjust the path.
try:
    drive.mount('/content/drive')
    DRIVE_FOLDER_PATH = "/content/drive/MyDrive/HealthApp/"
except Exception as e:
    print(f"Could not mount Google Drive. Using local folder. Error: {e}")
    DRIVE_FOLDER_PATH = "HealthAppData/"


# --- Data Persistence ---
if not os.path.exists(DRIVE_FOLDER_PATH):
    os.makedirs(DRIVE_FOLDER_PATH)

DATA_FILE = os.path.join(DRIVE_FOLDER_PATH, "user_health_data.pkl")


def _hash_password(password):
    """Hashes the password using SHA-256 for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def save_data(data):
    """Saves the main data dictionary to a pickle file."""
    with open(DATA_FILE, "wb") as f:
        pickle.dump(data, f)

def load_data():
    """Loads data from the pickle file if it exists, otherwise returns an empty dictionary."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "rb") as f:
                return pickle.load(f)
        except (pickle.UnpicklingError, EOFError):
            # If the file is corrupted or empty, return an empty dict
            return {}
    return {}

# --- Load data at startup ---
# This dictionary will be imported and used by the logic module.
user_health_data = load_data()
