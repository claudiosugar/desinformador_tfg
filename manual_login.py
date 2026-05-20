"""
One-time manual login helper.

Opens the SAME Chrome profile the bot uses (./browser_profile). Log in to X by
hand. Solve any captcha / phone challenge. Once you're on the home feed, just
close the window. The bot will reuse the cookies on next run.

Run: python manual_login.py
"""
import asyncio
import os
from playwright.async_api import async_playwright


async def main():
    pw = await async_playwright().start()
    profile_dir = os.path.abspath('./browser_profile')
    os.makedirs(profile_dir, exist_ok=True)

    print(f'Opening Chrome with profile: {profile_dir}')
    print('LOG IN TO X MANUALLY in the window that opens.')
    print('Once you see the X home feed, close the browser window.')
    print('Cookies will be saved automatically for the bot to reuse.\n')

    context = await pw.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        channel='chrome',
        headless=False,
        viewport={'width': 1280, 'height': 800},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        args=['--disable-blink-features=AutomationControlled'],
    )
    await context.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
    )
    page = context.pages[0] if context.pages else await context.new_page()
    await page.goto('https://x.com/i/flow/login')

    # Wait until the user closes the window
    try:
        while True:
            await asyncio.sleep(2)
            if not context.pages:
                break
    except Exception:
        pass

    print('Browser closed — session saved.')
    await pw.stop()


if __name__ == '__main__':
    asyncio.run(main())
