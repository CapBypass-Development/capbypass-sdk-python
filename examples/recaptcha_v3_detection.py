"""
reCAPTCHA v3 Detection Example (Python)

Demonstrates how to programmatically detect whether a site uses
reCAPTCHA v3 Standard or Enterprise, and automatically select
the correct task type.

Requirements:
- pip install capbypass playwright
- playwright install chromium
"""

import os
from typing import Literal, Optional
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

from capbypass import CapBypass

# Initialize client
client = CapBypass(api_key=os.getenv('CAPBYPASS_API_KEY', ''))


def detect_recaptcha_type(url: str) -> Optional[Literal['standard', 'enterprise']]:
    """
    Detect reCAPTCHA type using Playwright network interception.

    This is the most reliable method as it captures the actual script
    loading, regardless of when it loads in the page lifecycle.

    Args:
        url: Target website URL

    Returns:
        'standard', 'enterprise', or None if detection failed
    """
    detected_type = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Intercept network requests
        def handle_request(request):
            nonlocal detected_type
            request_url = request.url

            # Check for reCAPTCHA script loading
            if '/recaptcha/enterprise.js' in request_url:
                detected_type = 'enterprise'
                print('✓ Detected: reCAPTCHA v3 ENTERPRISE')
            elif '/recaptcha/api.js' in request_url:
                detected_type = 'standard'
                print('✓ Detected: reCAPTCHA v3 STANDARD')

        page.on('request', handle_request)

        try:
            page.goto(url, wait_until='networkidle', timeout=30000)

            # Fallback: Check DOM if no network request detected
            if not detected_type:
                print('No network detection, checking DOM...')
                detected_type = page.evaluate('''() => {
                    if (window.grecaptcha?.enterprise) return 'enterprise';
                    if (window.grecaptcha) return 'standard';
                    return null;
                }''')

        except Exception as e:
            print(f'Detection failed: {e}')
        finally:
            browser.close()

    return detected_type


def solve_with_auto_detection(url: str, site_key: str, action: str) -> str:
    """
    Solve reCAPTCHA with automatic type detection.

    Args:
        url: Target website URL
        site_key: reCAPTCHA site key
        action: Page action (e.g., 'submit', 'login')

    Returns:
        Token string

    Raises:
        ValueError: If detection fails
        CapBypassError: If solve fails
    """
    print(f'\nDetecting reCAPTCHA type for: {url}')

    detected_type = detect_recaptcha_type(url)

    if not detected_type:
        raise ValueError(
            'Could not detect reCAPTCHA type. '
            'Please verify the site uses reCAPTCHA v3.'
        )

    task_type = (
        'ReCaptchaV3EnterpriseTaskProxyLess'
        if detected_type == 'enterprise'
        else 'ReCaptchaV3TaskProxyLess'
    )

    print(f'Using task type: {task_type}\n')

    solution = client.solve({
        'type': task_type,
        'websiteURL': url,
        'websiteKey': site_key,
        'pageAction': action,
    })

    return solution['gRecaptchaResponse']


class RecaptchaTypeCache:
    """
    Cache for reCAPTCHA type detection results.

    Recommended for production to avoid repeated browser launches.
    """

    def __init__(self):
        self._cache = {}

    def get_type(self, url: str) -> Literal['standard', 'enterprise']:
        """
        Get reCAPTCHA type for URL, using cache if available.

        Args:
            url: Target website URL

        Returns:
            'standard' or 'enterprise'

        Raises:
            ValueError: If detection fails
        """
        domain = urlparse(url).netloc

        if domain not in self._cache:
            print(f'Cache miss for {domain}, detecting...')
            detected_type = detect_recaptcha_type(url)

            if not detected_type:
                raise ValueError(f'Could not detect reCAPTCHA type for {domain}')

            self._cache[domain] = detected_type
            print(f'Cached {domain} → {detected_type}')
        else:
            print(f'Cache hit for {domain} → {self._cache[domain]}')

        return self._cache[domain]

    def clear(self, domain: Optional[str] = None):
        """Clear cache for specific domain or entire cache."""
        if domain:
            self._cache.pop(urlparse(domain).netloc, None)
        else:
            self._cache.clear()


# ── Usage Examples ───────────────────────────────────────────────────────


def example1_basic_detection():
    """Example 1: Basic Detection"""
    print('═' * 55)
    print('Example 1: Basic Detection')
    print('═' * 55 + '\n')

    try:
        token = solve_with_auto_detection(
            url='https://example.com',
            site_key='6Lc...',
            action='submit'
        )

        print(f'✓ Token generated: {token[:50]}...\n')
    except Exception as e:
        print(f'✗ Failed: {e}\n')


def example2_with_caching():
    """Example 2: Detection with Caching"""
    print('═' * 55)
    print('Example 2: Detection with Caching')
    print('═' * 55 + '\n')

    cache = RecaptchaTypeCache()

    try:
        # First solve - detects and caches
        type1 = cache.get_type('https://example.com')
        solution1 = client.solve({
            'type': (
                'ReCaptchaV3EnterpriseTaskProxyLess'
                if type1 == 'enterprise'
                else 'ReCaptchaV3TaskProxyLess'
            ),
            'websiteURL': 'https://example.com',
            'websiteKey': '6Lc...',
            'pageAction': 'submit',
        })

        print(f'✓ First solve: {solution1["gRecaptchaResponse"][:50]}...\n')

        # Second solve - uses cache (faster!)
        type2 = cache.get_type('https://example.com')
        solution2 = client.solve({
            'type': (
                'ReCaptchaV3EnterpriseTaskProxyLess'
                if type2 == 'enterprise'
                else 'ReCaptchaV3TaskProxyLess'
            ),
            'websiteURL': 'https://example.com',
            'websiteKey': '6Lc...',
            'pageAction': 'checkout',
        })

        print(f'✓ Second solve (cached): {solution2["gRecaptchaResponse"][:50]}...\n')

    except Exception as e:
        print(f'✗ Failed: {e}\n')


def example3_multi_site():
    """Example 3: Multiple Sites"""
    print('═' * 55)
    print('Example 3: Multiple Sites')
    print('═' * 55 + '\n')

    sites = [
        {'url': 'https://site1.com', 'siteKey': '6Lc...', 'action': 'login'},
        {'url': 'https://site2.com', 'siteKey': '6Ld...', 'action': 'submit'},
        {'url': 'https://site3.com', 'siteKey': '6Le...', 'action': 'checkout'},
    ]

    for site in sites:
        try:
            print(f'\nProcessing: {site["url"]}')
            token = solve_with_auto_detection(
                site['url'],
                site['siteKey'],
                site['action']
            )
            print(f'  ✓ Success: {token[:50]}...')
        except Exception as e:
            print(f'  ✗ Failed: {e}')

    print()


def main():
    """Run all examples."""
    if not os.getenv('CAPBYPASS_API_KEY'):
        print('ERROR: CAPBYPASS_API_KEY environment variable not set')
        return

    example1_basic_detection()
    example2_with_caching()
    example3_multi_site()


if __name__ == '__main__':
    main()
