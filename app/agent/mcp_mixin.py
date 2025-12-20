"""
MCP Mixin - MCP 서버 연결을 처리하는 믹스인 클래스
=================================================
Manus와 JeongongBloom 에이전트에서 공통으로 사용되는 MCP 서버
연결 로직을 분리하여 코드 중복을 제거합니다.
"""

from typing import Dict, List, Optional

from pydantic import Field

from app.config import config
from app.logger import logger
from app.tool.mcp import MCPClients, MCPClientTool
from app.tool import ToolCollection


class MCPMixin:
    """MCP 서버 연결을 처리하는 믹스인 클래스.
    
    이 믹스인은 MCP 서버에 대한 연결/연결 해제 로직을 제공합니다.
    ToolCallAgent를 상속받는 에이전트에서 사용할 수 있습니다.
    
    필요한 속성:
        - mcp_clients: MCPClients 인스턴스
        - connected_servers: Dict[str, str] - 연결된 서버 추적
        - available_tools: ToolCollection 인스턴스
        - _initialized: bool - 초기화 상태 추적
    """
    
    # MCP 클라이언트
    mcp_clients: MCPClients = Field(default_factory=MCPClients)
    
    # 연결된 서버 추적 (server_id -> url/command)
    connected_servers: Dict[str, str] = Field(default_factory=dict)
    
    # 초기화 상태
    _initialized: bool = False

    async def initialize_mcp_servers(self) -> None:
        """설정된 MCP 서버들에 연결을 초기화합니다."""
        for server_id, server_config in config.mcp_config.servers.items():
            try:
                if server_config.type == "sse":
                    if server_config.url:
                        await self.connect_mcp_server(server_config.url, server_id)
                        logger.info(
                            f"Connected to MCP server {server_id} at {server_config.url}"
                        )
                elif server_config.type == "stdio":
                    if server_config.command:
                        await self.connect_mcp_server(
                            server_config.command,
                            server_id,
                            use_stdio=True,
                            stdio_args=server_config.args,
                        )
                        logger.info(
                            f"Connected to MCP server {server_id} using command {server_config.command}"
                        )
            except Exception as e:
                logger.error(f"Failed to connect to MCP server {server_id}: {e}")

    async def connect_mcp_server(
        self,
        server_url: str,
        server_id: str = "",
        use_stdio: bool = False,
        stdio_args: Optional[List[str]] = None,
    ) -> None:
        """MCP 서버에 연결하고 해당 도구들을 추가합니다.
        
        Args:
            server_url: 서버 URL 또는 stdio 명령어
            server_id: 서버 식별자
            use_stdio: stdio 연결 사용 여부
            stdio_args: stdio 명령어 인수
        """
        if use_stdio:
            await self.mcp_clients.connect_stdio(
                server_url, stdio_args or [], server_id
            )
            self.connected_servers[server_id or server_url] = server_url
        else:
            await self.mcp_clients.connect_sse(server_url, server_id)
            self.connected_servers[server_id or server_url] = server_url

        # 새 서버의 도구만 available_tools에 추가
        new_tools = [
            tool for tool in self.mcp_clients.tools if tool.server_id == server_id
        ]
        self.available_tools.add_tools(*new_tools)

    async def disconnect_mcp_server(self, server_id: str = "") -> None:
        """MCP 서버 연결을 해제하고 해당 도구들을 제거합니다.
        
        Args:
            server_id: 연결 해제할 서버 식별자 (빈 문자열이면 모든 서버)
        """
        await self.mcp_clients.disconnect(server_id)
        if server_id:
            self.connected_servers.pop(server_id, None)
        else:
            self.connected_servers.clear()

        # 연결 해제된 서버의 도구를 제외하고 다시 구성
        base_tools = [
            tool
            for tool in self.available_tools.tools
            if not isinstance(tool, MCPClientTool)
        ]
        self.available_tools = ToolCollection(*base_tools)
        self.available_tools.add_tools(*self.mcp_clients.tools)
