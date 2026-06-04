"""Task type definitions for CapBypass API."""


class TaskType:
    """Supported CAPTCHA task types.

    Use these constants when creating tasks to ensure correct type strings.
    """

    # AWS WAF tasks
    ANTI_AWS_WAF_TASK = "AntiAwsWafTask"
    ANTI_AWS_WAF_TASK_PROXYLESS = "AntiAwsWafTaskProxyLess"

    # reCAPTCHA v2 tasks
    RECAPTCHA_V2_TASK = "ReCaptchaV2Task"
    RECAPTCHA_V2_TASK_PROXYLESS = "ReCaptchaV2TaskProxyLess"

    # reCAPTCHA v3 tasks
    RECAPTCHA_V3_TASK = "ReCaptchaV3Task"
    RECAPTCHA_V3_TASK_PROXYLESS = "ReCaptchaV3TaskProxyLess"

    # reCAPTCHA v3 Enterprise tasks
    RECAPTCHA_V3_ENTERPRISE_TASK = "ReCaptchaV3EnterpriseTask"
    RECAPTCHA_V3_ENTERPRISE_TASK_PROXYLESS = "ReCaptchaV3EnterpriseTaskProxyLess"

    # GeeTest v3 + v4 tasks
    GEETEST_TASK = "GeetestTask"
    GEETEST_TASK_PROXYLESS = "GeetestTaskProxyLess"

    # hCaptcha tasks
    HCAPTCHA_TASK = "HCaptchaTask"
    HCAPTCHA_TASK_PROXYLESS = "HCaptchaTaskProxyless"

    # CaptchaFox tasks
    CAPTCHA_FOX_TASK = "CaptchaFoxTask"
    CAPTCHA_FOX_TASK_PROXYLESS = "CaptchaFoxTaskProxyLess"
