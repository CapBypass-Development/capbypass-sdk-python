"""Example: Solve reCAPTCHA v2 using CapBypass SDK."""

from capbypass import CapBypass

# Initialize client (reads from CAPBYPASS_API_KEY env var)
client = CapBypass()

# Or provide API key explicitly:
# client = CapBypass(api_key="your-api-key-here")

print("Solving reCAPTCHA v2...")

try:
    # Solve CAPTCHA (auto-polling until complete)
    solution = client.solve({
        "type": "ReCaptchaV2TaskProxyLess",
        "websiteURL": "https://www.google.com/recaptcha/api2/demo",
        "websiteKey": "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
    })

    print("✓ CAPTCHA solved!")
    print(f"Token: {solution['gRecaptchaResponse'][:80]}...")

except Exception as e:
    print(f"✗ Error: {e}")
