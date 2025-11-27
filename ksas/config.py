"""
KSAS Configuration Module
Centralizes all thresholds, paths, and UI settings for the application.
"""

import os

# =============================================================================
# 🔬 SCIENTIFIC THRESHOLDS
# =============================================================================

# BLS (Box Least Squares) - Initial Detection
BLS_SNR_THRESHOLD = 10.0       # Minimum Signal-to-Noise Ratio to trigger TLS
BLS_MAX_DEPTH = 0.1            # Maximum depth (10%) to avoid obvious binaries

# TLS (Transit Least Squares) - Confirmation
TLS_SDE_THRESHOLD = 7.0        # Signal Detection Efficiency (>7 is significant)
TLS_MIN_TRANSITS = 2           # Minimum number of transits required

# Vetting - False Positive Rejection (STRICT MODE)
# These thresholds are calibrated to reject visually noisy signals
VETTING_ODD_EVEN_TOLERANCE = 0.05  # Max 5% difference between odd/even depths
VETTING_SHAPE_THRESHOLD = 0.2      # Max normalized std dev for shape (lower = U-shape)
VETTING_SECONDARY_THRESHOLD = 0.001 # Max secondary eclipse depth (0.1%)
VETTING_MAX_DEPTH_DURATION_RATIO = 0.5 # Max depth/duration ratio

# =============================================================================
# 📂 FILE PATHS
# =============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DB_FILE = os.path.join(BASE_DIR, "candidates.json")
TRACKER_FILE = os.path.join(BASE_DIR, "analyzed_stars.json")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =============================================================================
# 🔄 UPDATER CONFIGURATION
# =============================================================================

# TODO: REPLACE THIS WITH YOUR ACTUAL GITHUB REPO URL
GITHUB_REPO = "https://github.com/Cesargg55/KSAS.git" 
CURRENT_VERSION = "4.2.4"

# =============================================================================
# 🎨 UI THEME (Professional Dark Mode)
# =============================================================================

COLORS = {
    'bg_dark': '#1a1a1a',      # Main background
    'bg_panel': '#2a2a2a',     # Panel background
    'bg_input': '#0a0a0a',     # Input fields
    'text_main': '#ffffff',    # Main text
    'text_dim': '#aaaaaa',     # Secondary text
    'accent': '#ffaa00',       # Orange accent (Titles)
    'success': '#00ff00',      # Green (Success/Good)
    'warning': '#ffaa00',      # Orange (Warning)
    'danger': '#ff4444',       # Red (Error/Bad)
    'info': '#00aaff',         # Blue (Info)
    'primary': '#0066cc',      # Blue button
    'secondary': '#666666',    # Gray button
}

FONTS = {
    'title': ('Arial', 20, 'bold'),
    'header': ('Arial', 12, 'bold'),
    'normal': ('Arial', 10),
    'mono': ('Courier New', 9),
    'mono_small': ('Courier New', 8),
}

# =============================================================================
# ⚙️ SYSTEM SETTINGS
# =============================================================================

NUM_WORKERS = 4                # Number of parallel analysis threads
DOWNLOAD_RETRIES = 3           # Number of retries for failed downloads
BATCH_SIZE = 50                # Number of stars to process in auto mode
LANGUAGE = 'EN'                # Interface Language ('EN' or 'ES')
