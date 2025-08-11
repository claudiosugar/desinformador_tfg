# Disinformation Spreader - TFG Project (Python)

A Python-based X bot that automatically responds to posts containing the `#desinfo_uib` hashtag with AI-generated disinformation using Google's Gemini AI.

## ⚠️ Disclaimer

This project is created for educational purposes as part of a university thesis (TFG). It demonstrates the potential risks of AI-powered disinformation spread. This tool should only be used in controlled academic environments with proper ethical considerations.

## Features

- 🤖 **AI-Powered Responses**: Uses Google Gemini AI to generate convincing disinformation responses
- 📱 **X Automation**: Automated login and interaction using Playwright
- 🔍 **Hashtag Monitoring**: Continuously monitors `#desinfo_uib` hashtag
- 💾 **Response Tracking**: Keeps track of responded posts to avoid duplicates
- 🛡️ **Rate Limiting**: Built-in delays to avoid X detection
- 📊 **Logging**: Comprehensive logging for monitoring and debugging
- 🐍 **Python Implementation**: Modern async/await patterns for efficient operation

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- X account with the credentials specified in config.py

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd desinformador-tfg
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**
   ```bash
   playwright install chromium
   ```

4. **Test the setup**
   ```bash
   python test_setup.py
   ```

## Configuration

**Important**: The `config.py` file contains sensitive information and is not tracked by git. Use `config_template.py` as a starting point.

1. **Copy the template**:
   ```bash
   cp config_template.py config.py
   ```

2. **Edit `config.py`** with your credentials:

```python
# Gemini AI API Key
GEMINI_API_KEY = 'your-gemini-api-key'

# X Credentials
X_USERNAME = 'your-x-username'
X_PASSWORD = 'your-x-password'
X_PHONE_NUMBER = 'your-phone-number'  # For security challenges

# Hashtag to monitor
TARGET_HASHTAG = '#desinfo_uib'

# Response interval (in seconds)
RESPONSE_INTERVAL = 30

# Browser settings
HEADLESS = False  # Set to True for production
SLOW_MO = 1000    # Milliseconds to slow down actions
```

## Usage

### Start the bot
```bash
python main.py
```

### Test the setup
```bash
python test_setup.py
```

### Stop the bot
Press `Ctrl+C` to gracefully stop the bot.

## How It Works

1. **Initialization**: The bot launches a browser and logs into X
2. **Monitoring**: Continuously searches for posts with `#desinfo_uib`
3. **Analysis**: Identifies new posts that haven't been responded to
4. **AI Generation**: Uses Gemini AI to create disinformation responses
5. **Response**: Automatically replies to posts with generated content
6. **Tracking**: Saves responded post IDs to avoid duplicates

## Project Structure

```
desinformador-tfg/
├── src/
│   ├── __init__.py        # Package initialization
│   ├── gemini_ai.py       # Gemini AI integration
│   └── x_bot.py          # X automation logic
├── main.py               # Main application entry point
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── test_setup.py       # Setup verification script
└── README.md           # This file
```

## Dependencies

- **playwright**: Browser automation for X interaction
- **google-generativeai**: Google Gemini AI API integration
- **python-dotenv**: Environment variable management
- **requests**: HTTP requests for API calls
- **beautifulsoup4**: HTML parsing
- **selenium**: Alternative browser automation (backup)

## Safety Features

- **Rate Limiting**: Built-in delays between actions
- **Duplicate Prevention**: Tracks responded posts
- **Error Handling**: Graceful error recovery
- **Graceful Shutdown**: Proper cleanup on exit
- **User Agent Spoofing**: Avoids basic bot detection
- **Async Operations**: Efficient non-blocking operations

## Ethical Considerations

This project demonstrates:
- The potential for AI-powered disinformation
- The importance of media literacy
- The need for responsible AI development
- The risks of automated social media manipulation

## Troubleshooting

### Common Issues

1. **Login Failed**
   - Verify X credentials in config.py
   - Check if 2FA is enabled (not supported)
   - Ensure account is not locked

2. **AI Response Generation Failed**
   - Verify Gemini API key is valid
   - Check internet connection
   - Review API usage limits

3. **Browser Issues**
   - Ensure Playwright is installed: `playwright install chromium`
   - Try running in headless mode by changing `HEADLESS = True` in config.py

4. **Python Version Issues**
   - Ensure Python 3.8+ is installed
   - Check with: `python --version`

### Debug Mode

To enable detailed logging, the application automatically logs to both console and file (`disinformation_spreader.log`).

For additional debugging, modify the browser launch options in `src/x_bot.py`:

```python
self.browser = await self.playwright.chromium.launch(
    headless=False,
    slow_mo=1000,
    devtools=True  # Opens developer tools
)
```

## Development

### Running Tests
```bash
python test_setup.py
```

### Code Structure
- **Async/Await**: Modern Python async patterns for efficient operation
- **Error Handling**: Comprehensive try/catch blocks
- **Logging**: Structured logging with different levels
- **Configuration**: Centralized configuration management

## Contributing

This is an academic project. For educational purposes only.

## License

MIT License - Educational use only.

## Support

For academic support, contact your thesis supervisor.

## Logs

The application creates detailed logs in `disinformation_spreader.log` for debugging and monitoring purposes.
