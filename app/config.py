import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'inventory.db')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-inventory-key-2026'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REPORTS_DIR = os.path.join(BASE_DIR, 'exports')
    
    # Ensure exports folder exists
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR, exist_ok=True)
