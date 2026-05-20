"""Connect via CDP and dump the first few posts on the user's profile."""
import asyncio
from playwright.async_api import async_playwright
import config


async def main():
    pw = await async_playwright().start()
    browser = await pw.chromium.connect_over_cdp(config.CHROME_CDP_URL)
    ctx = browser.contexts[0]
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()

    handle = 'desinfotfguib'
    url = f'https://x.com/{handle}'
    print(f'Navigating to: {url}')
    await page.goto(url, wait_until='domcontentloaded')
    await asyncio.sleep(5)

    posts = await page.query_selector_all('article[data-testid="tweet"]')
    print(f'\nFound {len(posts)} posts on profile:\n')
    for i, post in enumerate(posts[:10]):
        try:
            text_el = await post.query_selector('div[data-testid="tweetText"]')
            text = (await text_el.text_content()) if text_el else '(no text)'
            print(f'[{i+1}] text: {text[:300]}')
            print()
        except Exception as e:
            print(f'[{i+1}] error: {e}')

    await pw.stop()


if __name__ == '__main__':
    asyncio.run(main())
