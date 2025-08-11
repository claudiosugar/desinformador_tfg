#!/usr/bin/env python3
"""
Disinformation Spreader - TFG Project
Main application entry point
"""

import asyncio
import logging
import signal
import sys
from src.x_bot import XBot
from src.gemini_ai import GeminiAI
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('disinformation_spreader.log')
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
                    logger.warning('Failed to search hashtag, retrying...')
                    await asyncio.sleep(config.RESPONSE_INTERVAL)
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
                logger.info(f'Waiting {config.RESPONSE_INTERVAL} seconds before next check...')
                await asyncio.sleep(config.RESPONSE_INTERVAL)
                
            except Exception as e:
                logger.error(f'Error in monitoring loop: {e}')
                await asyncio.sleep(config.RESPONSE_INTERVAL)
    
    async def process_post(self, post):
        """Process a single post and generate a response"""
        try:
            logger.info(f'Processing post by @{post["author"]}:')
            post_preview = post["text"][:100] + "..." if len(post["text"]) > 100 else post["text"]
            logger.info(f'Content: "{post_preview}"')
            
            # Generate disinformation response using Gemini AI
            response = self.gemini_ai.generate_disinformation_response(
                post["text"], 
                post["author"]
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

async def main():
    """Main application entry point"""
    global spreader
    
    try:
        setup_signal_handlers()
        spreader = DisinformationSpreader()
        await spreader.start()
    except Exception as e:
        logger.error(f'❌ Fatal error: {e}')
        sys.exit(1)

if __name__ == "__main__":
    # Run the application
    asyncio.run(main())
