# SDK Installation and Configuration Guide

## Overview
This guide covers the installation and initial configuration of our official SDKs across multiple programming languages. Follow these steps to get started with platform integration.

---

## 1. Python SDK

### Installation
```bash
pip install example-platform-sdk>=2.5.0
```

### Requirements
- Python 3.8 or higher
- pip 21.0 or higher
- Virtual environment recommended

### Quick Start
```python
from example_platform import Client, Config

# Initialize with environment variable
client = Client(
    config=Config(
        api_key=os.environ["PLATFORM_API_KEY"],
        environment="production",  # or "sandbox"
        timeout=30,
        max_retries=3
    )
)

# Test connection
status = client.health_check()
print(f"Connected: {status.is_healthy}")
```

### Common Installation Issues
- **pip not found**: Ensure Python is added to PATH. Run `python -m pip install ...`
- **SSL certificate error**: Update certifi: `pip install --upgrade certifi`
- **Version conflict**: Use a virtual environment to isolate dependencies
- **Permission denied**: Use `pip install --user` or activate virtual environment

---

## 2. JavaScript/Node.js SDK

### Installation
```bash
npm install @example/platform-sdk
# or
yarn add @example/platform-sdk
```

### Requirements
- Node.js 16.0 or higher
- npm 8.0 or higher

### Quick Start
```javascript
const { PlatformClient } = require('@example/platform-sdk');

const client = new PlatformClient({
  apiKey: process.env.PLATFORM_API_KEY,
  environment: 'production'
});

// Test connection
const status = await client.healthCheck();
console.log(`Connected: ${status.isHealthy}`);
```

---

## 3. Configuration Options

| Parameter      | Type    | Default       | Description                          |
|---------------|---------|---------------|--------------------------------------|
| api_key       | string  | Required      | Your API authentication key          |
| environment   | string  | "production"  | "production" or "sandbox"            |
| timeout       | int     | 30            | Request timeout in seconds           |
| max_retries   | int     | 3             | Maximum retry attempts               |
| base_url      | string  | Auto          | Custom API base URL (advanced)       |
| debug         | bool    | false         | Enable verbose logging               |
| proxy         | string  | None          | HTTP proxy URL for corporate networks|

---

## 4. Sandbox vs Production

### Sandbox Environment
- URL: `https://sandbox-api.example.com/v2`
- Free, unlimited API calls for testing
- Data is reset weekly (every Sunday at midnight UTC)
- No real payments or notifications processed
- Use sandbox API keys (prefixed with `sk_sandbox_`)

### Production Environment
- URL: `https://api.example.com/v2`
- Subject to rate limits per your plan
- Real data processing and notifications
- Use production API keys (prefixed with `sk_live_`)

---

## 5. Proxy and Firewall Configuration

If you're behind a corporate proxy:
1. Set the proxy in SDK configuration: `proxy="http://proxy.corp.com:8080"`
2. Allowlist these domains:
   - `api.example.com` (port 443)
   - `sandbox-api.example.com` (port 443)
   - `cdn.example.com` (port 443)
3. Ensure TLS 1.2+ is allowed through the proxy

---

## 6. Upgrade Guide

### From v1.x to v2.x
Breaking changes:
- `Client()` constructor now requires `Config` object
- `client.get_user()` renamed to `client.users.get()`
- Response objects now use snake_case properties
- Minimum Python version raised to 3.8

Migration steps:
1. Update the package: `pip install --upgrade example-platform-sdk`
2. Update initialization code to use `Config` object
3. Update method calls to new namespaced format
4. Run test suite to catch any remaining breaking changes
