import asyncio
import json
import os
import time
from playwright.async_api import async_playwright
import config
import logging

class XBot:
    def __init__(self):
        """Initialize X bot with browser and data tracking"""
        self.browser = None
        self.page = None
        self.responded_posts = set()
        self.data_file = config.RESPONDED_POSTS_FILE
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize browser and load responded posts data"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            # Load previously responded posts
            await self.load_responded_posts()
            
            # Launch browser
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=config.HEADLESS,
                slow_mo=config.SLOW_MO
            )
            
            self.page = await self.browser.new_page()
            
            # Set user agent to avoid detection
            await self.page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            self.logger.info('X bot initialized successfully')
            return True
            
        except Exception as e:
            self.logger.error(f'Error initializing X bot: {e}')
            return False
    
    async def login(self):
        """Login to X with provided credentials"""
        try:
            self.logger.info('Logging into X...')
            
            # Navigate to X login
            await self.page.goto('https://twitter.com/login')
            
            # Wait for login form and enter username
            await self.page.wait_for_selector('input[autocomplete="username"]')
            await self.page.fill('input[autocomplete="username"]', config.X_USERNAME)
            await self.page.click('text=Next')
            
            # Check for security challenge after username (before password)
            security_challenge_handled = await self.handle_security_challenge()
            
            # Wait and enter password
            await self.page.wait_for_selector('input[name="password"]')
            await self.page.fill('input[name="password"]', config.X_PASSWORD)
            await self.page.click('text=Log in')
            
            # Wait for login to complete with multiple success indicators
            login_successful = False
            max_wait_time = 60  # 60 seconds total
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time and not login_successful:
                try:
                    await asyncio.sleep(2)
                    current_url = self.page.url
                    self.logger.info(f'Checking login status - Current URL: {current_url}')
                    
                    # Check multiple indicators of successful login
                    
                    # 1. Check if we're on X/Twitter domain (not login page)
                    if ('x.com' in current_url or 'twitter.com' in current_url) and 'login' not in current_url:
                        self.logger.info('Login successful - on X/Twitter domain')
                        login_successful = True
                        break
                    
                    # 2. Check for X home page elements
                    home_indicators = [
                        '[data-testid="primaryColumn"]',
                        '[data-testid="SideNav_NewTweet_Button"]',
                        '[data-testid="AppTabBar_Home_Link"]',
                        'a[href="/home"]',
                        'a[href="/i/home"]'
                    ]
                    
                    for indicator in home_indicators:
                        element = await self.page.query_selector(indicator)
                        if element:
                            self.logger.info(f'Login successful - found home indicator: {indicator}')
                            login_successful = True
                            break
                    
                    if login_successful:
                        break
                    
                    # 3. Check if we're still on login page
                    login_indicators = [
                        'input[autocomplete="username"]',
                        'input[name="password"]',
                        'text="Log in"',
                        'text="Sign in"'
                    ]
                    
                    still_on_login = False
                    for indicator in login_indicators:
                        element = await self.page.query_selector(indicator)
                        if element:
                            still_on_login = True
                            break
                    
                    if not still_on_login:
                        self.logger.info('Login successful - no longer on login page')
                        login_successful = True
                        break
                    
                    # 4. Check for error messages that indicate login failure
                    error_indicators = [
                        'text="Incorrect username or password"',
                        'text="Something went wrong"',
                        'text="Account locked"',
                        'text="Suspicious activity"'
                    ]
                    
                    for error in error_indicators:
                        error_element = await self.page.query_selector(error)
                        if error_element:
                            error_text = await error_element.text_content()
                            self.logger.error(f'Login failed - Error: {error_text}')
                            return False
                    
                except Exception as e:
                    self.logger.warning(f'Error checking login status: {e}')
                    continue
            
            if login_successful:
                self.logger.info('Successfully logged into X')
                return True
            else:
                self.logger.error('Login timeout - could not confirm successful login')
                return False
            
        except Exception as e:
            self.logger.error(f'Error logging into X: {e}')
            return False
    
    async def handle_security_challenge(self):
        """Handle security challenge that can appear after username entry"""
        try:
            # Wait a moment for security challenge to appear
            await asyncio.sleep(3)
            
            # Look for the specific security challenge input field
            security_input = await self.page.query_selector('input[data-testid="ocfEnterTextTextInput"]')
            if security_input:
                self.logger.info('Security challenge detected - entering phone number...')
                
                # Enter the provided phone number
                await security_input.fill(config.X_PHONE_NUMBER)
                await asyncio.sleep(1)
                
                # Look for and click the continue/verify button
                continue_button = await self.page.query_selector('[data-testid="ocfEnterTextNextButton"]')
                if continue_button:
                    await continue_button.click()
                    self.logger.info('Phone number submitted for verification')
                    await asyncio.sleep(5)
                    return True
                else:
                    # Try alternative button selectors
                    alt_buttons = await self.page.query_selector_all('text="Continue", text="Verify", text="Next"')
                    if alt_buttons:
                        await alt_buttons[0].click()
                        self.logger.info('Phone number submitted for verification (alternative button)')
                        await asyncio.sleep(5)
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f'Error handling security challenge: {e}')
            return False
    
    async def search_hashtag(self):
        """Search for posts with the target hashtag"""
        try:
            self.logger.info(f'Searching for hashtag: {config.TARGET_HASHTAG}')
            
            # Wait a moment for the page to fully load
            await asyncio.sleep(2)
            
            # Look for the search input field using the exact selector
            search_input = await self.page.query_selector('input[data-testid="SearchBox_Search_Input"]')
            if search_input:
                self.logger.info('Found search input, typing hashtag...')
                await search_input.click()
                await search_input.fill(config.TARGET_HASHTAG)
                await self.page.keyboard.press('Enter')
                await asyncio.sleep(3)
                self.logger.info('Search completed')
            else:
                self.logger.warning('Search input not found, trying direct URL...')
                # Fallback: try direct URL
                search_url = f'https://twitter.com/search?q={config.TARGET_HASHTAG}&src=typed_query&f=live'
                await self.page.goto(search_url)
                await asyncio.sleep(3)
            
            # Wait for posts to load with better error handling
            posts_found = False
            try:
                await self.page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)
                self.logger.info('Posts found using article selector')
                posts_found = True
            except Exception as e:
                self.logger.info(f'Article selector timeout, trying alternative: {e}')
                try:
                    await self.page.wait_for_selector('[data-testid="cellInnerDiv"]', timeout=10000)
                    self.logger.info('Posts found using cellInnerDiv selector')
                    posts_found = True
                except Exception as e2:
                    self.logger.info(f'CellInnerDiv selector timeout, trying generic: {e2}')
                    try:
                        await self.page.wait_for_selector('article', timeout=10000)
                        self.logger.info('Posts found using generic article selector')
                        posts_found = True
                    except Exception as e3:
                        self.logger.warning(f'All post selectors failed: {e3}')
                        # Continue anyway, posts might still be there
                        posts_found = True
            
            self.logger.info('Search results loaded successfully')
            return True
            
        except Exception as e:
            self.logger.error(f'Error searching hashtag: {e}')
            return False
    
    async def get_new_posts(self):
        """Get new posts that haven't been responded to"""
        try:
            # Wait a moment for posts to load
            await asyncio.sleep(2)
            
            # Try multiple selectors for posts
            posts = []
            selectors = [
                'article[data-testid="tweet"]',
                '[data-testid="cellInnerDiv"]',
                'article'
            ]
            
            for selector in selectors:
                posts = await self.page.query_selector_all(selector)
                if posts:
                    self.logger.info(f'Found {len(posts)} posts using selector: {selector}')
                    break
            
            if not posts:
                self.logger.warning('No posts found with any selector')
                return []
            
            new_posts = []
            
            for i, post in enumerate(posts):
                try:
                    self.logger.info(f'Processing post {i+1}/{len(posts)}')
                    
                    # Get post text with multiple possible selectors
                    text_element = None
                    text_selectors = [
                        'div[data-testid="tweetText"]',
                        '[data-testid="tweetText"]',
                        'div[lang]',
                        'span[lang]',
                        'div[data-testid="tweetText"] span',
                        'span[lang]'
                    ]
                    
                    for text_selector in text_selectors:
                        text_element = await post.query_selector(text_selector)
                        if text_element:
                            break
                    
                    if not text_element:
                        self.logger.debug(f'Post {i+1}: No text element found')
                        continue
                    
                    post_text = await text_element.text_content()
                    if not post_text or len(post_text.strip()) < 5:
                        self.logger.debug(f'Post {i+1}: Text too short or empty')
                        continue
                    
                    # Get author username with multiple possible selectors
                    author_element = None
                    author_selectors = [
                        'a[role="link"]',
                        '[data-testid="User-Name"] a',
                        'a[href^="/"]',
                        '[data-testid="User-Name"] span',
                        'span[dir="ltr"]'
                    ]
                    
                    for author_selector in author_selectors:
                        author_element = await post.query_selector(author_selector)
                        if author_element:
                            break
                    
                    if not author_element:
                        self.logger.debug(f'Post {i+1}: No author element found')
                        continue
                    
                    # Try to get author from href first, then from text content
                    author_href = await author_element.get_attribute('href')
                    if author_href and author_href.startswith('/'):
                        author = author_href[1:]
                    else:
                        author_text = await author_element.text_content()
                        author = author_text.strip() if author_text else 'unknown'
                    
                    # Get post ID with multiple possible selectors
                    post_link = None
                    link_selectors = [
                        'a[href*="/status/"]',
                        'a[href*="/x/status/"]',
                        'a[data-testid="tweetText"]',
                        'time[datetime]'
                    ]
                    
                    for link_selector in link_selectors:
                        post_link = await post.query_selector(link_selector)
                        if post_link:
                            break
                    
                    if not post_link:
                        self.logger.debug(f'Post {i+1}: No post link found')
                        continue
                    
                    # Try to get post ID from href or datetime
                    post_url = await post_link.get_attribute('href')
                    post_id = None
                    
                    if post_url and ('/status/' in post_url or '/x/status/' in post_url):
                        post_id = post_url.split('/status/')[-1].split('?')[0]
                    else:
                        # Try to get from datetime attribute
                        datetime_attr = await post_link.get_attribute('datetime')
                        if datetime_attr:
                            # Use timestamp as ID if no URL ID found
                            post_id = str(hash(datetime_attr + author + post_text[:50]))
                    
                    if post_id and post_id not in self.responded_posts:
                        new_posts.append({
                            'id': post_id,
                            'text': post_text,
                            'author': author,
                            'element': post
                        })
                        self.logger.info(f'Found new post: @{author} - {post_text[:50]}...')
                    else:
                        self.logger.debug(f'Post {i+1}: Already responded or no valid ID')
                        
                except Exception as e:
                    self.logger.error(f'Error processing post {i+1}: {e}')
                    continue
            
            self.logger.info(f'Found {len(new_posts)} new posts to respond to')
            return new_posts
            
        except Exception as e:
            self.logger.error(f'Error getting new posts: {e}')
            return []
    
    async def respond_to_post(self, post_element, response_text):
        """Respond to a specific post with the given text"""
        try:
            self.logger.info('Attempting to reply to post...')
            
            # Try multiple selectors for the reply button
            reply_button = None
            reply_selectors = [
                'div[data-testid="reply"]',
                '[data-testid="reply"]',
                'div[aria-label="Reply"]',
                'div[aria-label*="Reply"]',
                'button[data-testid="reply"]',
                'button[aria-label="Reply"]'
            ]
            
            for selector in reply_selectors:
                reply_button = await post_element.query_selector(selector)
                if reply_button:
                    self.logger.info(f'Found reply button with selector: {selector}')
                    break
            
            if not reply_button:
                self.logger.warning('Reply button not found with any selector')
                # Try to find any clickable element that might be a reply button
                all_buttons = await post_element.query_selector_all('button, div[role="button"]')
                for button in all_buttons:
                    try:
                        aria_label = await button.get_attribute('aria-label') or ''
                        if 'reply' in aria_label.lower():
                            reply_button = button
                            self.logger.info('Found reply button by aria-label')
                            break
                    except:
                        continue
                
                if not reply_button:
                    self.logger.error('Could not find reply button')
                    return False
            
            # Click the reply button with better error handling
            try:
                # Wait for the button to be stable before clicking
                await reply_button.wait_for_element_state('stable', timeout=5000)
                await reply_button.click()
                self.logger.info('Clicked reply button')
            except Exception as reply_click_error:
                self.logger.warning(f'Reply button click failed: {reply_click_error}, trying force click')
                try:
                    await reply_button.click(force=True)
                    self.logger.info('Clicked reply button with force=True')
                except Exception as force_error:
                    self.logger.error(f'Reply button force click also failed: {force_error}')
                    return False
            
            await asyncio.sleep(2)
            
            # Try multiple selectors for the reply text area
            reply_text_area = None
            text_area_selectors = [
                'div[data-testid="tweetTextarea_0"]',
                'div[data-testid="tweetTextarea_1"]',
                'div[data-testid="tweetTextarea"]',
                '[data-testid="tweetTextarea_0"]',
                '[data-testid="tweetTextarea_1"]',
                '[data-testid="tweetTextarea"]',
                'div[contenteditable="true"]',
                'div[role="textbox"]',
                'div[aria-label="Tweet text"]'
            ]
            
            for selector in text_area_selectors:
                reply_text_area = await self.page.query_selector(selector)
                if reply_text_area:
                    self.logger.info(f'Found text area with selector: {selector}')
                    break
            
            if not reply_text_area:
                self.logger.warning('Reply text area not found with any selector')
                # Try to find any contenteditable div
                contenteditable_divs = await self.page.query_selector_all('div[contenteditable="true"]')
                if contenteditable_divs:
                    reply_text_area = contenteditable_divs[0]
                    self.logger.info('Found text area by contenteditable attribute')
                else:
                    self.logger.error('Could not find reply text area')
                    return False
            
            # Clear any existing text and type the response
            await reply_text_area.click()
            await asyncio.sleep(1)
            
            # Clear existing content
            await reply_text_area.fill('')
            await asyncio.sleep(0.5)
            
            # Type the response
            await reply_text_area.type(response_text)
            self.logger.info(f'Typed response: {response_text[:50]}...')
            await asyncio.sleep(1)
            
            # Use Ctrl+Enter to submit (much simpler and more reliable)
            try:
                # Focus on the text area first to ensure it's active
                await reply_text_area.focus()
                await asyncio.sleep(0.5)
                # Press Ctrl+Enter to submit
                await self.page.keyboard.press('Control+Enter')
                self.logger.info('Pressed Ctrl+Enter to submit')
                await asyncio.sleep(3)
                self.logger.info('Successfully replied to post')
                return True
            except Exception as ctrl_enter_error:
                self.logger.error(f'Ctrl+Enter failed: {ctrl_enter_error}')
                return False
            
        except Exception as e:
            self.logger.error(f'Error responding to post: {e}')
            return False
    
    async def load_responded_posts(self):
        """Load previously responded posts from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.responded_posts = set(data.get('responded_posts', []))
                    self.logger.info(f'Loaded {len(self.responded_posts)} previously responded posts')
            else:
                self.responded_posts = set()
                
        except Exception as e:
            self.logger.error(f'Error loading responded posts: {e}')
            self.responded_posts = set()
    
    async def save_responded_posts(self):
        """Save responded posts data to file"""
        try:
            data = {
                'responded_posts': list(self.responded_posts),
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info('Saved responded posts data')
            
        except Exception as e:
            self.logger.error(f'Error saving responded posts: {e}')
    
    async def close(self):
        """Close browser and cleanup resources"""
        try:
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            self.logger.info('X bot closed')
            
        except Exception as e:
            self.logger.error(f'Error closing X bot: {e}')
