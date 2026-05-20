"""
Step-by-step login diagnostic. Pauses for ENTER between steps so you can inspect
the browser. Saves HTML + screenshot dumps to ./debug/diag_*.

Run: python diagnose_login.py
"""
import asyncio
import os
import time
from playwright.async_api import async_playwright
import config


async def dump(page, tag):
    os.makedirs('./debug', exist_ok=True)
    ts = time.strftime('%H%M%S')
    base = f'./debug/diag_{ts}_{tag}'
    await page.screenshot(path=f'{base}.png', full_page=True)
    html = await page.content()
    with open(f'{base}.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  [dump] {base}.png / .html  (url={page.url})')


async def main():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=False, slow_mo=200)
    page = await browser.new_page()
    await page.set_extra_http_headers({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })

    print('Step 1: navigating to x.com/i/flow/login')
    await page.goto('https://x.com/i/flow/login', wait_until='domcontentloaded')
    await asyncio.sleep(5)
    await dump(page, '01_loaded')

    print('Step 2: locating username input')
    username_input = await page.query_selector('input[autocomplete="username"]')
    print(f'  query_selector(input[autocomplete="username"]) -> {username_input}')
    if not username_input:
        username_input = await page.query_selector('input[name="text"]')
        print(f'  fallback query_selector(input[name="text"]) -> {username_input}')

    if username_input:
        is_visible = await username_input.is_visible()
        bbox = await username_input.bounding_box()
        print(f'  visible={is_visible} bbox={bbox}')

    print('Step 3: clicking + typing username')
    await username_input.click()
    await asyncio.sleep(0.5)
    await page.keyboard.type(config.X_USERNAME, delay=80)
    await asyncio.sleep(2)
    await dump(page, '03_after_type')

    value = await username_input.input_value()
    print(f'  username field value after type: {value!r}')

    print('Step 4: clicking Next')
    next_btn = await page.query_selector('button:has-text("Next")')
    print(f'  Next button -> {next_btn}')
    if next_btn:
        await next_btn.click()
    await asyncio.sleep(5)
    await dump(page, '04_after_next')

    await browser.close()
    await pw.stop()


if __name__ == '__main__':
    asyncio.run(main())
