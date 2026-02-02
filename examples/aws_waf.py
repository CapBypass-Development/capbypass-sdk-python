"""Example: Solve AWS WAF CAPTCHA using CapBypass SDK."""

from capbypass import CapBypass

# Initialize client
client = CapBypass()

print("Solving AWS WAF CAPTCHA...")

try:
    solution = client.solve({
        "type": "AntiAwsWafTaskProxyLess",
        "websiteURL": "https://example.com",
        "awsChallengeJS": "https://example.com/challenge.js",  # Replace with actual challenge URL
    })

    print("✓ AWS WAF CAPTCHA solved!")
    print(f"Token: {solution['token'][:80]}...")
    print(f"Cookie: {solution['cookie']}")
    print(f"User-Agent: {solution.get('userAgent', 'N/A')}")

except Exception as e:
    print(f"✗ Error: {e}")
