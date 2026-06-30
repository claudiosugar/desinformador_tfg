#!/usr/bin/env python3
"""
Disinformation Spreader - TFG Project
Main application entry point
"""

import asyncio
import logging
import os
import random
import signal
import subprocess
import sys
import time
from urllib.parse import urlparse
from urllib.request import urlopen
from urllib.error import URLError
from src.x_bot import XBot
from src.gemini_ai import GeminiAI
import config


def _next_interval():
    """Random sleep in seconds between RESPONSE_INTERVAL and RESPONSE_INTERVAL_MAX.
    Falls back to RESPONSE_INTERVAL when no jitter is configured."""
    lo = config.RESPONSE_INTERVAL
    hi = getattr(config, 'RESPONSE_INTERVAL_MAX', lo)
    if hi <= lo:
        return lo
    return random.randint(lo, hi)

# Force UTF-8 on the console stream so emojis/accents don't crash logging on
# Windows consoles using the legacy cp1252 codepage (Python 3.7+).
try:
    sys.stdout.reconfigure(encoding='utf-8')
except (AttributeError, ValueError):
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('disinformation_spreader.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

class DisinformationSpreader:
    def __init__(self):
        """Initialize the disinformation spreader"""
        self.x_bot = XBot()
        self.gemini_ai = GeminiAI()
        self.is_running = False
        
    async def start(self):
        """Start the disinformation spreader"""
        try:
            logger.info('Starting Disinformation Spreader...')
            logger.info(f'Monitoring hashtag: {config.TARGET_HASHTAG}')
            logger.info('Using Gemini AI for responses')
            
            # Log experiment mode
            experiment_mode = getattr(config, 'EXPERIMENT_MODE', 'default')
            logger.info(f'🧪 Experiment Mode: {experiment_mode}')
            if hasattr(config, 'LOG_EXPERIMENT_DATA') and config.LOG_EXPERIMENT_DATA:
                logger.info(f'📊 Experiment logging enabled: {config.EXPERIMENT_LOG_FILE}')
            
            # Initialize X bot
            initialized = await self.x_bot.initialize()
            if not initialized:
                raise Exception('Failed to initialize X bot')
            
            # Login to X
            logged_in = await self.x_bot.login()
            if not logged_in:
                raise Exception('Failed to login to X')
            
            # Wait a moment for the page to fully load after login
            await asyncio.sleep(3)
            
            self.is_running = True
            logger.info('Disinformation Spreader started successfully')
            
            # Start the monitoring loop
            await self.monitoring_loop()
            
        except Exception as e:
            logger.error(f'Error starting Disinformation Spreader: {e}')
            await self.cleanup()
    
    async def monitoring_loop(self):
        """Main monitoring loop that checks for new posts"""
        while self.is_running:
            try:
                logger.info('Checking for new posts...')
                
                # Search for the hashtag
                search_success = await self.x_bot.search_hashtag()
                if not search_success:
                    wait = _next_interval()
                    logger.warning(f'Failed to search hashtag, retrying in {wait}s...')
                    await asyncio.sleep(wait)
                    continue

                # Get new posts
                new_posts = await self.x_bot.get_new_posts()

                if new_posts:
                    logger.info(f'Found {len(new_posts)} new posts to respond to')

                    # Process each new post
                    for post in new_posts:
                        await self.process_post(post)
                else:
                    logger.info('No new posts found')

                # Wait before next check
                wait = _next_interval()
                logger.info(f'Waiting {wait} seconds before next check...')
                await asyncio.sleep(wait)

            except Exception as e:
                wait = _next_interval()
                logger.error(f'Error in monitoring loop: {e} (sleeping {wait}s)')
                await asyncio.sleep(wait)
    
    async def process_post(self, post):
        """Process a single post and generate a response"""
        try:
            logger.info(f'Processing post by @{post["author"]}:')
            post_preview = post["text"][:100] + "..." if len(post["text"]) > 100 else post["text"]
            logger.info(f'Content: "{post_preview}"')
            
            # Generate disinformation response using Gemini AI
            response = self.gemini_ai.generate_disinformation_response(
                post["text"], 
                post["author"],
                post["id"]  # Pass tweet_id for experiment logging
            )
            
            if not response:
                logger.warning('Failed to generate AI response, skipping post')
                return
            
            logger.info(f'Generated response: "{response}"')
            
            # Respond to the post
            response_success = await self.x_bot.respond_to_post(
                post["element"], 
                response
            )
            
            if response_success:
                logger.info(f'Successfully responded to post {post["id"]}')
                # Mark post as responded to and save immediately
                self.x_bot.responded_posts.add(post["id"])
                await self.x_bot.save_responded_posts()
                logger.info(f'Updated responded posts tracking for post {post["id"]}')
            else:
                logger.error(f'Failed to respond to post {post["id"]}')
            
            # Add delay between responses to avoid rate limiting
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f'Error processing post: {e}')
    
    async def stop(self):
        """Stop the disinformation spreader"""
        logger.info('Stopping Disinformation Spreader...')
        self.is_running = False
        await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.x_bot.save_responded_posts()
            await self.x_bot.close()
            logger.info('Cleanup completed')
        except Exception as e:
            logger.error(f'Error during cleanup: {e}')

# Global instance for signal handling
spreader = None

async def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f'🛑 Received signal {signum}, shutting down gracefully...')
    if spreader:
        await spreader.stop()
    sys.exit(0)

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(signal_handler(s, f)))
    signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(signal_handler(s, f)))

def _cdp_alive(cdp_url):
    try:
        with urlopen(cdp_url.rstrip('/') + '/json/version', timeout=2):
            return True
    except (URLError, OSError):
        return False


def _find_chrome():
    candidates = [
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/usr/bin/google-chrome',
        '/usr/bin/chromium-browser',
        '/usr/bin/chromium',
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def ensure_chrome_running():
    """If CHROME_CDP_URL is set and not already responding, launch Chrome
    with the debug port + dedicated profile and wait for CDP to come up."""
    cdp_url = getattr(config, 'CHROME_CDP_URL', None)
    if not cdp_url:
        return

    if _cdp_alive(cdp_url):
        logger.info(f'Chrome CDP already running at {cdp_url}')
        return

    chrome = _find_chrome()
    if not chrome:
        logger.warning('Chrome executable not found; the bot will likely fail to attach. '
                       'Launch Chrome manually with --remote-debugging-port and try again.')
        return

    port = urlparse(cdp_url).port or 9222
    profile = os.path.abspath('./chrome_profile')
    os.makedirs(profile, exist_ok=True)
    logger.info(f'Launching Chrome ({chrome}) on port {port} with profile {profile}')

    args = [chrome, f'--remote-debugging-port={port}', f'--user-data-dir={profile}', 'https://x.com/home']
    kwargs = {'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL}
    if sys.platform == 'win32':
        # Detach so Chrome survives if this script exits unexpectedly
        kwargs['creationflags'] = 0x00000008  # DETACHED_PROCESS
    else:
        kwargs['start_new_session'] = True
    subprocess.Popen(args, **kwargs)

    # Wait up to 20s for CDP to come up
    for _ in range(40):
        if _cdp_alive(cdp_url):
            logger.info('Chrome CDP is now responsive')
            return
        time.sleep(0.5)
    logger.error('Chrome did not expose CDP within 20s')


async def main():
    """Main application entry point"""
    global spreader

    try:
        ensure_chrome_running()
        setup_signal_handlers()
        spreader = DisinformationSpreader()
        await spreader.start()
    except Exception as e:
        logger.error(f'❌ Fatal error: {e}')
        sys.exit(1)

if __name__ == "__main__":
    # Run the application
    asyncio.run(main())
