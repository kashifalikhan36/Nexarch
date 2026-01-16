#!/usr/bin/env python
"""
Nexarch MCP Server Launcher
Run this script to start the MCP server for Claude Desktop integration.

Usage:
  python start_mcp.py              # Start with stdio transport (for Claude Desktop)
  python start_mcp.py --sse        # Start with SSE transport (for web clients)
  python start_mcp.py --http       # Start with streamable HTTP transport
"""
import sys
import os

# Add Server directory to path FIRST (before any imports)
server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Server')
sys.path.insert(0, server_dir)

print("🚀 Starting Nexarch MCP Server...", file=sys.stderr)
print(f"   Server directory: {server_dir}", file=sys.stderr)

try:
    from mcp_server.server import mcp
    
    # Determine transport mode
    transport = "stdio"
    if "--sse" in sys.argv:
        transport = "sse"
    elif "--http" in sys.argv:
        transport = "streamable-http"
    
    print(f"✅ MCP Server initialized with 6 tools (transport: {transport})", file=sys.stderr)
    mcp.run(transport=transport)
except ImportError as e:
    print(f"❌ Error: {e}", file=sys.stderr)
    print("\nTroubleshooting:", file=sys.stderr)
    print("1. Make sure fastmcp is installed: pip install fastmcp", file=sys.stderr)
    print("2. Check if pydantic version is compatible", file=sys.stderr)
    print("3. Try: pip install --upgrade pydantic fastmcp", file=sys.stderr)
    sys.exit(1)
