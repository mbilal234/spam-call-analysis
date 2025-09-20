# Spam Call Analysis API

A backend service that automatically checks phone numbers against spam providers like Hiya and Truecaller using Android automation.

## Overview

This API service extends the original spam call analysis tool to provide a RESTful interface for checking phone numbers against multiple spam detection providers. The service uses Android automation to interact with spam detection apps and returns normalized results.

## Features

- **RESTful API**: Simple HTTP endpoints for checking phone numbers
- **Multiple Providers**: Support for Hiya, Truecaller, and other spam detection services
- **Android Automation**: Uses Appium to automate Android devices/emulators
- **Batch Processing**: Check multiple numbers simultaneously
- **Normalized Results**: Consistent response format across all providers
- **Device Management**: Automatic device allocation and health monitoring
- **Scalable**: Support for multiple Android devices running in parallel

## Phase 1 - Hiya Integration

Currently implements Hiya integration with the following capabilities:
- Single phone number checking
- Batch processing
- Device management
- Health monitoring

## Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Android SDK** and emulators set up
3. **Appium server** running
4. **Required APK files** in the `apks/` directory

### Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start Appium server:
```bash
appium
```

4. Start Android emulators:
```bash
# Create emulators (if not already done)
sh helper-scripts/create-emulators.sh 3

# Start emulators
emulator -avd Medium_Phone_API_36.1 &
```

### Running the API

1. **Quick start with checks**:
```bash
python start_api.py
```

2. **Manual start**:
```bash
python api_server.py
```

3. **With custom settings**:
```bash
export API_PORT=8080
export MAX_DEVICES=5
python api_server.py
```

### Testing the API

Run the test suite:
```bash
python test_api.py
```

## API Endpoints

### Health Check
```http
GET /api/v1/health
```

### Get Available Providers
```http
GET /api/v1/providers
```

### Check Single Number
```http
POST /api/v1/check
Content-Type: application/json

{
  "phone_number": "+1234567890",
  "providers": ["hiya"],
  "timeout": 30
}
```

### Check Multiple Numbers (Batch)
```http
POST /api/v1/check/batch
Content-Type: application/json

{
  "requests": [
    {"phone_number": "+1234567890", "providers": ["hiya"]},
    {"phone_number": "+1987654321", "providers": ["hiya"]}
  ]
}
```

### Get Batch Status
```http
GET /api/v1/batch/{task_id}/status
```

### Get Batch Results
```http
GET /api/v1/batch/{task_id}/results
```

## Response Format

### Single Check Response
```json
{
  "phone_number": "+1234567890",
  "overall_status": "blocked",
  "confidence": 0.95,
  "providers": [
    {
      "provider": "hiya",
      "status": "blocked",
      "confidence": 0.95,
      "response_time": 2.5,
      "error_message": null,
      "raw_data": {
        "delta": 2.5,
        "original_status": "blocked"
      }
    }
  ],
  "total_response_time": 2.5,
  "timestamp": "2024-01-20T10:30:00Z"
}
```

### Status Values
- `allowed`: Number is not flagged as spam
- `blocked`: Number is flagged as spam
- `caution`: Number has suspicious characteristics
- `timeout`: Check timed out
- `error`: An error occurred during checking

## Configuration

Environment variables can be used to configure the service:

```bash
# API Settings
export API_HOST=0.0.0.0
export API_PORT=8000
export API_WORKERS=1

# Device Settings
export MAX_DEVICES=3
export DEVICE_TIMEOUT=30

# Provider Settings
export DEFAULT_TIMEOUT=30
export ENABLED_PROVIDERS=hiya

# Google Account (for apps requiring authentication)
export GOOGLE_USERNAME=your-email@gmail.com
export GOOGLE_PASSWORD=your-password

# Appium Settings
export APPIUM_SERVER_URL=http://localhost:4723
```

## Architecture

### Core Components

1. **API Server** (`api_server.py`): FastAPI-based REST API
2. **Spam Checker Service** (`spam_checker.py`): Main orchestration service
3. **Device Manager** (`device_manager.py`): Android device management
4. **Providers** (`providers/`): Provider-specific implementations
5. **Models** (`models.py`): Pydantic data models

### Provider System

The service uses a plugin architecture for spam detection providers:

- **Base Provider** (`providers/base_provider.py`): Abstract base class
- **Hiya Provider** (`providers/hiya_provider.py`): Hiya integration
- **Future Providers**: Truecaller, CallApp, etc.

### Device Management

- Automatic device allocation and release
- Health monitoring and error recovery
- Idle device cleanup
- Support for multiple concurrent devices

## Development

### Adding New Providers

1. Create a new provider class in `providers/`:
```python
from .base_provider import BaseProvider

class NewProvider(BaseProvider):
    async def initialize(self):
        # Initialize provider
        pass
    
    async def check_number(self, phone_number: str):
        # Check phone number
        return {
            "status": "blocked",
            "confidence": 0.95,
            "raw_data": {}
        }
    
    async def cleanup(self):
        # Cleanup resources
        pass
```

2. Register the provider in `spam_checker.py`:
```python
new_provider = NewProvider(self.device_manager)
await new_provider.initialize()
self.providers["new_provider"] = new_provider
```

### Testing

Run the test suite:
```bash
python test_api.py
```

Run specific tests:
```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Test single check
curl -X POST http://localhost:8000/api/v1/check \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890", "providers": ["hiya"]}'
```

## Troubleshooting

### Common Issues

1. **Appium not running**: Start Appium server with `appium`
2. **No Android devices**: Start emulators or connect physical devices
3. **Missing APK files**: Ensure APK files are in the `apks/` directory
4. **Google authentication**: Set `GOOGLE_USERNAME` and `GOOGLE_PASSWORD` for apps requiring it

### Logs

The service logs important events and errors. Check the console output for debugging information.

### Health Check

Use the health endpoint to check service status:
```bash
curl http://localhost:8000/api/v1/health
```

## Future Phases

- **Phase 2**: Truecaller integration
- **Phase 3**: Additional providers (CallApp, etc.)
- **Phase 4**: Enhanced scalability and reliability features
- **Phase 5**: Caching and performance optimizations

## License

This project is part of the Research Project 2022 at TU Delft.
