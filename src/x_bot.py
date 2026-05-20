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
            self.logger.info(f'Loaded responded posts set: {self.responded_posts}')
            
            self.playwright = await async_playwright().start()

            cdp_url = getattr(config, 'CHROME_CDP_URL', None)
            if cdp_url:
                # Connect to an already-running Chrome that the user launched manually.
                # This lets the bot inherit a real, logged-in session and avoid X's
                # automation fingerprinting entirely.
                self.logger.info(f'Connecting to existing Chrome over CDP: {cdp_url}')
                self.browser = await self.playwright.chromium.connect_over_cdp(cdp_url)
                self.context = self.browser.contexts[0] if self.browser.contexts else await self.browser.new_context()
                self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
            else:
                # Fallback: Playwright-launched persistent profile (may be detected by X).
                profile_dir = os.path.abspath('./browser_profile')
                os.makedirs(profile_dir, exist_ok=True)
                self.context = await self.playwright.chromium.launch_persistent_context(
                    user_data_dir=profile_dir,
                    channel='chrome',
                    headless=config.HEADLESS,
                    viewport={'width': 1280, 'height': 800},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                    args=['--disable-blink-features=AutomationControlled'],
                )
                self.browser = self.context.browser
                await self.context.add_init_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
                )
                self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
            
            self.logger.info('X bot initialized successfully')
            return True
            
        except Exception as e:
            self.logger.error(f'Error initializing X bot: {e}')
            return False
    
    async def login(self):
        """Login to X with provided credentials"""
        try:
            self.logger.info('Logging into X...')

            # If the persistent profile already has a valid session, skip the form.
            await self.page.goto('https://x.com/home', wait_until='domcontentloaded')
            await asyncio.sleep(3)
            if 'login' not in self.page.url and 'flow' not in self.page.url:
                home = await self.page.query_selector('[data-testid="primaryColumn"], a[href="/home"], a[data-testid="AppTabBar_Home_Link"]')
                if home:
                    self.logger.info(f'Already authenticated (url={self.page.url}); skipping login form')
                    return True

            await self.page.goto('https://x.com/i/flow/login', wait_until='domcontentloaded')

            await self._dismiss_cookie_banner()

            try:
                await self.page.wait_for_selector('input[autocomplete="username"], input[name="text"]', timeout=60000)
            except Exception as e:
                await self._dump_page('login_username_timeout')
                raise

            username_input = await self.page.query_selector('input[autocomplete="username"]') \
                or await self.page.query_selector('input[name="text"]')
            await username_input.click()
            await asyncio.sleep(0.5)
            await self.page.keyboard.type(config.X_USERNAME, delay=50)
            await asyncio.sleep(1)

            clicked = False
            for selector in ['button:has-text("Next")', 'div[role="button"]:has-text("Next")', 'button:has-text("Siguiente")', 'div[role="button"]:has-text("Siguiente")']:
                btn = await self.page.query_selector(selector)
                if btn:
                    await btn.click()
                    clicked = True
                    self.logger.info(f'Clicked next button: {selector}')
                    break
            if not clicked:
                await self.page.keyboard.press('Enter')
                self.logger.info('Submitted username via Enter key fallback')

            try:
                await self.page.wait_for_selector('input[name="password"]', timeout=30000)
            except Exception:
                await self._dump_page('login_password_timeout')
                raise
            password_input = await self.page.query_selector('input[name="password"]')
            await password_input.click()
            await asyncio.sleep(0.5)
            await self.page.keyboard.type(config.X_PASSWORD, delay=50)
            await asyncio.sleep(1)
            clicked = False
            for selector in ['button[data-testid="LoginForm_Login_Button"]', 'button:has-text("Log in")', 'div[role="button"]:has-text("Log in")', 'button:has-text("Iniciar sesión")', 'div[role="button"]:has-text("Iniciar sesión")']:
                btn = await self.page.query_selector(selector)
                if btn:
                    await btn.click()
                    clicked = True
                    self.logger.info(f'Clicked login button: {selector}')
                    break
            if not clicked:
                await self.page.keyboard.press('Enter')
                self.logger.info('Submitted password via Enter key fallback')
            
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
                search_url = f'https://x.com/search?q={config.TARGET_HASHTAG}&src=typed_query'
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

                    # Safety: only act on posts that actually contain the target hashtag.
                    # Top-tab search can include unrelated trending posts.
                    if config.TARGET_HASHTAG.lower() not in post_text.lower():
                        self.logger.info(f'Post {i+1}: skipped (does not contain {config.TARGET_HASHTAG})')
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
                    post_id = None
                    
                    # Method 1: Try to get from article data attribute (most reliable)
                    article_id = await post.get_attribute('data-testid')
                    if article_id and 'tweet-' in article_id:
                        post_id = article_id.replace('tweet-', '')
                        self.logger.debug(f'Post {i+1}: Found ID from article data-testid: {post_id}')
                    
                    # Method 2: Try to get from URL links
                    if not post_id:
                        link_selectors = [
                            'a[href*="/status/"]',
                            'a[href*="/x/status/"]',
                            'a[data-testid="tweetText"]',
                            'time[datetime]'
                        ]
                        
                        for link_selector in link_selectors:
                            post_link = await post.query_selector(link_selector)
                            if post_link:
                                post_url = await post_link.get_attribute('href')
                                if post_url and ('/status/' in post_url or '/x/status/' in post_url):
                                    post_id = post_url.split('/status/')[-1].split('?')[0]
                                    self.logger.debug(f'Post {i+1}: Found ID from URL: {post_id}')
                                    break
                    
                    # Method 3: Try to get from tweet text link
                    if not post_id:
                        tweet_text_link = await post.query_selector('a[data-testid="tweetText"]')
                        if tweet_text_link:
                            tweet_url = await tweet_text_link.get_attribute('href')
                            if tweet_url and ('/status/' in tweet_url or '/x/status/' in tweet_url):
                                post_id = tweet_url.split('/status/')[-1].split('?')[0]
                                self.logger.debug(f'Post {i+1}: Found ID from tweet text link: {post_id}')
                    
                    # Method 4: Try to get from time element
                    if not post_id:
                        time_element = await post.query_selector('time[datetime]')
                        if time_element:
                            time_url = await time_element.get_attribute('href')
                            if time_url and ('/status/' in time_url or '/x/status/' in time_url):
                                post_id = time_url.split('/status/')[-1].split('?')[0]
                                self.logger.debug(f'Post {i+1}: Found ID from time element: {post_id}')
                    
                    # Method 5: Fallback - create a more stable hash
                    if not post_id:
                        # Create a more stable identifier using multiple attributes
                        time_element = await post.query_selector('time[datetime]')
                        datetime_attr = await time_element.get_attribute('datetime') if time_element else ''
                        
                        # Create a more stable hash using author and first part of text
                        stable_text = post_text[:100].strip() if post_text else ''
                        stable_identifier = f"{author}_{datetime_attr}_{stable_text}"
                        
                        # Use a more stable hash function
                        import hashlib
                        post_id = hashlib.md5(stable_identifier.encode('utf-8')).hexdigest()[:16]
                        self.logger.debug(f'Post {i+1}: Generated fallback ID: {post_id}')
                    
                    if not post_id:
                        self.logger.debug(f'Post {i+1}: Could not extract any post ID')
                        continue
                    
                    if post_id and post_id not in self.responded_posts:
                        new_posts.append({
                            'id': post_id,
                            'text': post_text,
                            'author': author,
                            'element': post
                        })
                        self.logger.info(f'Found new post: @{author} - {post_text[:50]}... (ID: {post_id})')
                    else:
                        if post_id in self.responded_posts:
                            self.logger.info(f'Post {i+1}: Already responded (ID: {post_id})')
                        else:
                            self.logger.debug(f'Post {i+1}: No valid ID extracted')
                        
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
            self.logger.info(f'Loading responded posts from: {self.data_file}')
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.responded_posts = set(data.get('responded_posts', []))
                    self.logger.info(f'Loaded {len(self.responded_posts)} previously responded posts')
                    self.logger.info(f'Post IDs: {list(self.responded_posts)}')
            else:
                self.responded_posts = set()
                self.logger.info('No responded posts file found, starting with empty set')
                
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
    
    async def _dismiss_cookie_banner(self):
        """Try to dismiss X's cookie consent banner if present."""
        try:
            await asyncio.sleep(1)
            for selector in [
                'button:has-text("Refuse non-essential cookies")',
                'button:has-text("Rechazar las cookies no esenciales")',
                'button:has-text("Accept all cookies")',
                'button:has-text("Aceptar todas las cookies")',
            ]:
                btn = await self.page.query_selector(selector)
                if btn:
                    await btn.click()
                    self.logger.info(f'Dismissed cookie banner via: {selector}')
                    await asyncio.sleep(1)
                    return
        except Exception as e:
            self.logger.warning(f'Cookie banner dismissal skipped: {e}')

    async def _dump_page(self, tag):
        """Dump screenshot + HTML for post-mortem debugging."""
        try:
            os.makedirs('./debug', exist_ok=True)
            ts = time.strftime('%Y%m%d_%H%M%S')
            shot = f'./debug/{tag}_{ts}.png'
            html = f'./debug/{tag}_{ts}.html'
            await self.page.screenshot(path=shot, full_page=True)
            content = await self.page.content()
            with open(html, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.error(f'Saved debug dump: {shot} / {html} (url={self.page.url})')
        except Exception as e:
            self.logger.error(f'Failed to dump debug page: {e}')

    async def close(self):
        """Close browser and cleanup resources"""
        try:
            if hasattr(self, 'context') and self.context:
                await self.context.close()
            elif self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            self.logger.info('X bot closed')

        except Exception as e:
            self.logger.error(f'Error closing X bot: {e}')
