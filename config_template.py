# Configuration settings for the Disinformation Spreader
# Copy this file to config.py and fill in your actual credentials

# Gemini AI API Key
GEMINI_API_KEY = 'your_gemini_api_key_here'

# X Credentials
X_USERNAME = 'your_x_username_here'
X_PASSWORD = 'your_x_password_here'
X_PHONE_NUMBER = 'your_phone_number_here'

# Hashtag to monitor
TARGET_HASHTAG = '#desinfo_uib'

# Response interval (in seconds)
RESPONSE_INTERVAL = 180

# Data file to store responded posts
RESPONDED_POSTS_FILE = './data/responded_posts.json'

# Browser settings
HEADLESS = False  # Set to True for production
SLOW_MO = 1000  # Milliseconds to slow down actions
