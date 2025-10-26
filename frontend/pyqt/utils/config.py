# Cấu hình API
API_BASE_URL = "http://localhost:5000/api"

# Demo Mode - Bật để test UI mà không cần backend
# Set to False to use the real backend
DEMO_MODE = False

# Cấu hình UI
WINDOW_TITLE = "SecureFile App - AES + RSA Encryption"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Cấu hình file
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
SUPPORTED_FILE_TYPES = ["txt", "pdf", "doc", "docx", "jpg", "png", "mp4", "zip"]

# Styling
BUTTON_STYLE = """
    QPushButton {
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        font-size: 14px;
        margin: 4px 2px;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #45a049;
    }
    QPushButton:pressed {
        background-color: #3d8b40;
    }
"""

DANGER_BUTTON_STYLE = """
    QPushButton {
        background-color: #f44336;
        border: none;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        font-size: 14px;
        margin: 4px 2px;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #da190b;
    }
    QPushButton:pressed {
        background-color: #c73426;
    }
"""