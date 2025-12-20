"""
MCP (Model Context Protocol) 모듈
==================================
MCP 서버와의 통신을 처리합니다.

포함 내용:
- server: MCP 서버 구현
"""

from app.mcp.server import *


__all__ = [
    "server",
]
