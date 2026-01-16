# Nexarch Server Configuration

## Server Architecture

### FastAPI Server
- **Host**: `0.0.0.0` (accessible from network)
- **Port**: `8000`
- **Purpose**: Main REST API server for architecture intelligence platform
- **Access**: Network accessible, can be reached from other machines

### MCP Server  
- **Host**: `127.0.0.1` (localhost only)
- **Port**: `8001` (when using HTTP/SSE transport)
- **Purpose**: Model Context Protocol server for Claude Desktop integration
- **Access**: Local only, for security and Claude Desktop integration
- **Transport**: stdio (default), sse, or streamable-http

## Quick Start

### Start Both Servers (Recommended)
```bash
python start.py
```

This will launch both servers in separate PowerShell terminals:
- Terminal 1: FastAPI on 0.0.0.0:8000
- Terminal 2: MCP Server on 127.0.0.1:8001

### Start Individual Servers
```bash
# Start only FastAPI
python start.py --fastapi

# Start only MCP server
python start.py --mcp
```

### Check Server Status
```bash
python start.py --status
```

### Manual Server Start

#### FastAPI Server
```bash
cd Server
python main.py
```

#### MCP Server
```bash
# stdio mode (for Claude Desktop)
python start_mcp.py

# SSE transport
python start_mcp.py --sse

# HTTP transport  
python start_mcp.py --http
```

## Server URLs

- **FastAPI API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **MCP Server**: 127.0.0.1:8001 (when using HTTP/SSE transport)

## Stopping Servers

Simply close the terminal windows or press `Ctrl+C` in each terminal.

## Why This Configuration?

### FastAPI on 0.0.0.0
- Allows access from other machines on the network
- Enables development across multiple devices
- Required for production deployments
- Can be accessed via machine's IP address

### MCP on 127.0.0.1
- Security: Only accessible from the same machine
- Claude Desktop integration requires local access
- Prevents unauthorized external access to MCP tools
- Follows security best practices for development tools

## Troubleshooting

### Port Already in Use
If you get "port already in use" errors:

```bash
# Windows - Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Cannot Connect to FastAPI
- Check if server is running: `python start.py --status`
- Verify firewall allows connections on port 8000
- Try accessing via http://localhost:8000 instead of machine IP

### MCP Server Not Working with Claude
- Ensure using stdio transport (default): `python start_mcp.py`
- Check Claude Desktop config points to correct script path
- Verify all dependencies installed: `pip install fastmcp`

## Configuration Files

- `start.py`: Main launcher script
- `start_mcp.py`: MCP server entry point
- `Server/main.py`: FastAPI application entry point
- `Server/mcp_server/server.py`: MCP server implementation
