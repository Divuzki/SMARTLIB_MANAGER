# config.py
# Application Configuration

# Admin Credentials (In production, these should be stored securely)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Database Configuration
DATABASE_NAME = "library.db"

# QR Code Configuration
QR_CODE_DIRECTORY = "qr_codes"
QR_CODE_SIZE = 10
QR_CODE_BORDER = 4

# Application Settings
APP_TITLE = "SMARTLIB MANAGER"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Library Management System with QR Code Integration"

# UI Configuration
WINDOW_THEME = {
    'primary_color': '#3498db',
    'success_color': '#2ecc71',
    'warning_color': '#f39c12',
    'danger_color': '#e74c3c',
    'secondary_color': '#95a5a6',
    'background_color': '#f0f0f0',
    'text_color': '#2c3e50',
    'subtitle_color': '#7f8c8d'
}

# Font Configuration
FONT_FAMILY = "Arial"
FONT_SIZE_LARGE = 18
FONT_SIZE_MEDIUM = 14
FONT_SIZE_NORMAL = 10
FONT_SIZE_SMALL = 8

# Security Settings
MAX_LOGIN_ATTEMPTS = 3
SESSION_TIMEOUT = 3600  # 1 hour in seconds

# File Paths
LOG_FILE = "library_system.log"
BACKUP_DIRECTORY = "backups"

# Validation Rules
MAX_BOOK_TITLE_LENGTH = 200
MAX_AUTHOR_NAME_LENGTH = 100
MAX_STUDENT_NAME_LENGTH = 100
MAX_ISBN_LENGTH = 20

# Default Values
DEFAULT_BORROW_PERIOD_DAYS = 14
MAX_BOOKS_PER_STUDENT = 3
