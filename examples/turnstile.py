"""Example: Solve Cloudflare Turnstile using CapBypass SDK."""

from capbypass import CapBypass

# Initialize client
client = CapBypass()

print("Solving Cloudflare Turnstile...")

try:
    solution = client.solve({
        "type": "TurnstileTaskProxyLess",
        "websiteURL": "https://example.com/login",
        "websiteKey": "0x4AAAAAAAxxxxxxxxxxxxxx",
        "action": "login",  # Optional
        "cData": "session-42",  # Optional
    })

    print("✓ CAPTCHA solved!")
    print(f"Token: {solution['token'][:50]}...")

except Exception as e:
    print(f"✗ Error: {e}")
