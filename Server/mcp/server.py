from fastmcp import FastMCP
from typing import Dict, Any, List
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.tools import MCPTools

# Create MCP server
mcp = FastMCP("Nexarch Architecture Intelligence")

# Initialize tools
tools = MCPTools()


@mcp.tool()
def get_current_architecture() -> Dict[str, Any]:
    """Get current architecture graph with nodes, edges, and metrics"""
    return tools.get_current_architecture()


@mcp.tool()
def get_detected_issues() -> Dict[str, Any]:
    """Get all detected architectural issues"""
    return tools.get_detected_issues()


@mcp.tool()
def generate_workflows() -> Dict[str, Any]:
    """Generate 3 workflow alternatives using LangGraph reasoning"""
    return tools.generate_workflows()


@mcp.tool()
def compare_workflows() -> Dict[str, Any]:
    """Compare generated workflows with recommendation"""
    return tools.compare_workflows()


@mcp.tool()
def explain_decision(workflow_id: str) -> Dict[str, Any]:
    """Explain reasoning behind a specific workflow decision"""
    return tools.explain_decision(workflow_id)


@mcp.tool()
def get_graph_analysis() -> Dict[str, Any]:
    """Get advanced graph analysis (centrality, bottlenecks, cycles)"""
    return tools.get_graph_analysis()


if __name__ == "__main__":
    mcp.run()
