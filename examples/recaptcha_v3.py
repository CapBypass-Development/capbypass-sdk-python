"""Example: Solve reCAPTCHA v3 using CapBypass SDK."""

from capbypass import CapBypass

# Initialize client
client = CapBypass()

print("Solving reCAPTCHA v3...")

try:
    solution = client.solve({
        "type": "ReCaptchaV3TaskProxyLess",
        "websiteURL": "https://example.com",
        "websiteKey": "6LcR_okUAAAAAPYrPe-HK_0RULO1aZM15ENyM-Mf",
        "pageAction": "homepage",
        "minScore": 0.7,  # Optional: minimum score threshold
    })

    print("✓ CAPTCHA solved!")
    print(f"Token: {solution['gRecaptchaResponse'][:80]}...")
    print(f"User-Agent: {solution.get('userAgent', 'N/A')}")

except Exception as e:
    print(f"✗ Error: {e}")
