"""
Diagnostic: connect to running Chrome via CDP, use the in-page search box
(not URL navigation) to search the hashtag, dump posts. Does NOT respond.
"""
import asyncio
from playwright.async_api import async_playwright
import config


async def main():
    pw = await async_playwright().start()
    browser = await pw.chromium.connect_over_cdp(config.CHROME_CDP_URL)
    ctx = browser.contexts[0]
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()

    print(f'Starting URL: {page.url}')
    print('Navigating to home for a clean state...')
    await page.goto('https://x.com/home', wait_until='domcontentloaded')
    await asyncio.sleep(3)

    print('Looking for in-page search input...')
    search_input = None
    for selector in [
        'input[data-testid="SearchBox_Search_Input"]',
        'input[placeholder*="Search"]',
        'input[placeholder*="Buscar"]',
        'input[aria-label*="Search"]',
        'input[aria-label*="Buscar"]',
    ]:
        si = await page.query_selector(selector)
        if si:
            search_input = si
            print(f'  found via: {selector}')
            break

    if not search_input:
        print('Search input not visible from this page. Going to /explore to expose it.')
        await page.goto('https://x.com/explore', wait_until='domcontentloaded')
        await asyncio.sleep(3)
        for selector in [
            'input[data-testid="SearchBox_Search_Input"]',
            'input[placeholder*="Search"]',
            'input[placeholder*="Buscar"]',
        ]:
            si = await page.query_selector(selector)
            if si:
                search_input = si
                print(f'  found via: {selector}')
                break

    if not search_input:
        print('STILL no search input found. Dumping URL and bailing.')
        print(f'Final URL: {page.url}')
        await pw.stop()
        return

    await search_input.click()
    await asyncio.sleep(0.5)
    await page.keyboard.type(config.TARGET_HASHTAG, delay=60)
    await asyncio.sleep(1)
    await page.keyboard.press('Enter')
    print(f'Submitted search: {config.TARGET_HASHTAG}')
    await asyncio.sleep(5)

    print(f'After search URL: {page.url}')

    # Stay on Top tab (default) - that's where new-account posts show up

    no_results = await page.query_selector('text=/no results|no se encontraron/i')
    if no_results:
        print('Page indicates: NO RESULTS')

    posts = await page.query_selector_all('article[data-testid="tweet"]')
    print(f'\nFound {len(posts)} article[data-testid="tweet"] elements:\n')
    for i, post in enumerate(posts[:10]):
        try:
            text_el = await post.query_selector('div[data-testid="tweetText"]')
            text = (await text_el.text_content()) if text_el else '(no text)'
            author_el = await post.query_selector('div[data-testid="User-Name"] a')
            href = (await author_el.get_attribute('href')) if author_el else ''
            print(f'[{i+1}] author_href={href}')
            print(f'    text: {text[:200]}')
            print()
        except Exception as e:
            print(f'[{i+1}] error reading post: {e}')

    await pw.stop()


if __name__ == '__main__':
    asyncio.run(main())
