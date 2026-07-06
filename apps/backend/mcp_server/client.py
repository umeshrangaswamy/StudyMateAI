"""
MCP Client Wrapper
==================
In-process MCP client wrapper allowing agents to call MCP tools programmatically.
This avoids container startup dependencies or network transport overhead in the MVP.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


async def call_tool(server_name: str, tool_name: str, **kwargs) -> Any:
    """
    Invoke an MCP tool from a specific server.

    Args:
        server_name: 'knowledge' or 'assessment'
        tool_name:   The name of the tool to execute
        kwargs:      Arguments passed directly to the tool

    Returns:
        The tool execution results (usually dict or str)
    """
    logger.info(f"MCP Client: calling server={server_name}, tool={tool_name}")

    if server_name == "knowledge":
        if tool_name == "search_curriculum":
            from mcp_server.knowledge_server import search_curriculum
            return await search_curriculum(**kwargs)
        elif tool_name == "get_notes":
            from mcp_server.knowledge_server import get_notes
            return await get_notes(**kwargs)
        elif tool_name == "get_formula_sheet":
            from mcp_server.knowledge_server import get_formula_sheet
            return await get_formula_sheet(**kwargs)
        elif tool_name == "get_previous_questions":
            from mcp_server.knowledge_server import get_previous_questions
            return await get_previous_questions(**kwargs)
        else:
            raise ValueError(f"Unknown knowledge tool: {tool_name}")

    elif server_name == "assessment":
        if tool_name == "generate_quiz":
            from mcp_server.assessment_server import generate_quiz
            return await generate_quiz(**kwargs)
        elif tool_name == "evaluate_answer":
            from mcp_server.assessment_server import evaluate_answer
            return await evaluate_answer(**kwargs)
        elif tool_name == "recommend_revision":
            from mcp_server.assessment_server import recommend_revision
            return await recommend_revision(**kwargs)
        else:
            raise ValueError(f"Unknown assessment tool: {tool_name}")

    else:
        raise ValueError(f"Unknown MCP server: {server_name}")


def _extract_result(result: Any) -> Any:
    """
    Extracts the inner text or json object from MCP content blocks if wrapped.
    """
    # FastMCP.call_tool returns a tuple: (content_list, is_error)
    if isinstance(result, tuple) and len(result) == 2:
        content_list, is_error = result
        if is_error:
            logger.warning(f"MCP tool execution returned error/warning flag: {content_list}")
        result = content_list

    if isinstance(result, list):
        if not result:
            return None
        # Extract from TextContent block if present
        block = result[0]
        if hasattr(block, "text"):
            # If it's a JSON string, try to parse it
            import json
            text = block.text
            try:
                return json.loads(text)
            except Exception:
                return text
        return block

    return result
