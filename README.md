# CapBypass Python SDK

[![PyPI version](https://img.shields.io/pypi/v/capbypass-sdk.svg)](https://pypi.org/project/capbypass-sdk/)
[![Python versions](https://img.shields.io/pypi/pyversions/capbypass-sdk.svg)](https://pypi.org/project/capbypass-sdk/)
[![Downloads](https://pepy.tech/badge/capbypass-sdk)](https://pepy.tech/project/capbypass-sdk)
[![GitHub stars](https://img.shields.io/github/stars/CapBypass-Development/capbypass-sdk-python.svg)](https://github.com/CapBypass-Development/capbypass-sdk-python)

Official Python SDK for CapBypass CAPTCHA solving API.

## Features

- ✨ Simple `solve()` method with auto-polling
- 🎯 Advanced `createTask()` + `getTaskResult()` for granular control
- 💰 `getBalance()` to check account balance
- 🔄 Automatic retry logic for network failures
- 🛡️ Comprehensive error handling
- 📝 Type hints for better IDE support
- 🧪 100% test coverage

## Supported CAPTCHA Types

- reCAPTCHA v2 (normal & invisible)
- reCAPTCHA v3
- reCAPTCHA v3 Enterprise
- AWS WAF CAPTCHA

## Installation

```bash
pip install capbypass-sdk
```

## Quick Start

```python
from capbypass import CapBypass

# Initialize client
client = CapBypass(api_key="your-api-key")
# Or use environment variable: export CAPBYPASS_API_KEY="your-key"

# Solve CAPTCHA (auto-polling)
solution = client.solve({
    "type": "ReCaptchaV2TaskProxyLess",
    "websiteURL": "https://example.com",
    "websiteKey": "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-"
})

print(solution["gRecaptchaResponse"])
```

## Advanced Usage

### Granular Control

```python
# Create task
task_id = client.createTask({
    "type": "ReCaptchaV2TaskProxyLess",
    "websiteURL": "https://example.com",
    "websiteKey": "site-key"
})

# Poll for result
import time
while True:
    result = client.getTaskResult(task_id)
    if result["status"] == "ready":
        print(result["solution"])
        break
    time.sleep(5)
```

### Check Balance

```python
balance = client.getBalance()
print(f"Balance: ${balance:.4f}")
```

### Error Handling

```python
from capbypass import CapBypass
from capbypass.errors import (
    AuthenticationError,
    InsufficientBalanceError,
    TimeoutError,
)

try:
    solution = client.solve(task)
except AuthenticationError:
    print("Invalid API key")
except InsufficientBalanceError:
    print("Insufficient balance")
except TimeoutError:
    print("Task timed out")
```

## Documentation

Full documentation: https://capbypass.dev/docs/sdks/python

## Examples

See [examples/](examples/) directory for complete examples:

- [recaptcha_v2.py](examples/recaptcha_v2.py) - reCAPTCHA v2 solving
- [recaptcha_v3.py](examples/recaptcha_v3.py) - reCAPTCHA v3 solving
- [aws_waf.py](examples/aws_waf.py) - AWS WAF CAPTCHA solving

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .

# Run type checker
mypy src/
```

## License

MIT

## Support

- Documentation: https://capbypass.dev/docs
- Issues: https://github.com/CapBypass-Development/capbypass-sdk-python/issues
- Email: support@capbypass.dev
