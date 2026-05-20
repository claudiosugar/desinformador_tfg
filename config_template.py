# Configuration settings for the Disinformation Spreader
# Copy this file to config.py and fill in your actual credentials

# Gemini AI API Key
GEMINI_API_KEY = 'your_gemini_api_key_here'

# X Credentials
X_USERNAME = 'your_x_username_here'
X_PASSWORD = 'your_x_password_here'

# Hashtag to monitor
TARGET_HASHTAG = '#desinfo_uib'

# Response interval (in seconds)
RESPONSE_INTERVAL = 180

# Data file to store responded posts
RESPONDED_POSTS_FILE = './data/responded_posts.json'

# Browser settings
HEADLESS = False  # Set to True for production
SLOW_MO = 1000  # Milliseconds to slow down actions

# If set, the bot connects to an already-running Chrome via CDP instead of
# launching its own (recommended - bypasses X's bot detection). Start Chrome
# with: chrome.exe --remote-debugging-port=9222 --user-data-dir=<profile_path>
CHROME_CDP_URL = 'http://localhost:9222'

# Experiment Mode - Select disinformation strategy for research
# Options: 'default', 'emotional', 'authority', 'partial_truth', 
#          'whataboutism', 'source_confusion', 'conspiracy', 'random'
EXPERIMENT_MODE = 'default'

# Enable experiment mode logging (saves mode and response metadata)
LOG_EXPERIMENT_DATA = True

# Experiment log file
EXPERIMENT_LOG_FILE = './data/experiment_log.json'
