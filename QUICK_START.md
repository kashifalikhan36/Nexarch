# Nexarch Quick Start Guide

## Start Both Servers

Simply run:
```bash
python start.py
```

This will launch:
1. **FastAPI Server** - Runs on `0.0.0.0:8000` (network accessible) in Terminal 1
2. **MCP Server** - Runs on `127.0.0.1:8001` (localhost only) in Terminal 2

Both servers will run in separate terminal windows and automatically load Azure OpenAI credentials from `Server/.env`.

## What Happens

✅ Two new PowerShell terminals open automatically  
✅ Environment variables loaded from `Server/.env`  
✅ Azure OpenAI configured for AI features  
✅ FastAPI accessible from network  
✅ MCP server secure on localhost  

## Check Status

```bash
python start.py --status
```

## Access Points

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **FastAPI**: http://localhost:8000 (or http://YOUR_IP:8000 from network)
- **MCP Server**: 127.0.0.1:8001 (localhost only, stdio mode)

## Stop Servers

Close the two terminal windows or press `Ctrl+C` in each.

## Individual Server Launch

```bash
# Start only FastAPI
python start.py --fastapi

# Start only MCP server
python start.py --mcp
```

## MCP Transport Modes

By default, MCP uses stdio transport for Claude Desktop. For web clients:

```bash
# SSE transport
python start_mcp.py --sse

# HTTP transport
python start_mcp.py --http
```

## Environment Variables

All Azure OpenAI configuration is loaded from `Server/.env`:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`

No manual export needed - `start.py` handles it automatically!
