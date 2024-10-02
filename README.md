# Ella AI Application Documentation

## Overview
This document provides a comprehensive guide to the Ella AI application, which includes a FastAPI server with AI-powered chat functionality for Roblox integration.

## Project Structure
```
ella_www/
├── main.py
├── robloxgpt.py
├── testgpt.py
├── app.log
├── requirements.txt
└── static/
    └── (static files for the web interface)
```

## Setup and Installation

1. Clone the repository:
   ```
   git clone [repository_url]
   cd ella_www
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv ella-web
   source ella-web/bin/activate  # On Windows, use `ella-web\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the project root
   - Add the following variables:
     ```
     OPENAI_API_KEY=your_openai_api_key
     SENDGRID_API_KEY=your_sendgrid_api_key
     ```

## Main Components

### 1. main.py
This is the main FastAPI application file.

Key features:
- FastAPI app initialization
- Logging configuration
- API endpoints for health check, email sending, and static file serving
- Integration with the robloxgpt module

### 2. robloxgpt.py
This file contains the AI chat functionality for Roblox integration.

Key features:
- `/robloxgpt` endpoint for AI-powered chat
- Integration with OpenAI's GPT model
- Custom prompt for the AI character (Eldrin the Wise)

### 3. testgpt.py
This file contains pytest tests for the robloxgpt functionality.

Key features:
- Tests for successful API calls
- Tests for error handling (e.g., missing API key)
- Tests for invalid input

## Logging
Logging is configured in `main.py` and used throughout the application.

- Log file: `app.log`
- Log level: INFO
- Logging format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

To view logs in real-time:
```
tail -f app.log
```

## Running the Application

1. Start the FastAPI server:
   ```
   python main.py
   ```
   The server will start on `http://localhost:8000`

2. To test the robloxgpt endpoint:
   ```
   curl -X POST http://localhost:8000/robloxgpt \
        -H "Content-Type: application/json" \
        -d '{"message": "Hello, wizard!", "player_id": "test_player", "npc_id": "test_npc", "limit": 200}'
   ```

## Running Tests

To run the tests:
```
pytest testgpt.py
```

## Deployment Considerations

1. Ensure all environment variables are properly set in the production environment.
2. Configure proper security measures (e.g., HTTPS, API rate limiting).
3. Set up monitoring and alerting for the application and its dependencies.
4. Regularly update dependencies and the OpenAI API version.

## Troubleshooting

1. If logs are not appearing, check file permissions:
   ```
   ls -l app.log
   chmod 644 app.log  # If needed
   ```

2. If the OpenAI API is not responding, verify the API key and network connectivity.

3. For any other issues, check the logs for error messages and stack traces.

## Future Improvements

1. Implement user authentication for the robloxgpt endpoint.
2. Add more comprehensive error handling and input validation.
3. Implement caching to reduce API calls to OpenAI.
4. Create a dashboard for monitoring AI interactions and performance.