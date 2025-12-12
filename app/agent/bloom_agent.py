"""
Jeongong Bloom (정공블룸) 에이전트
==================================
"Vibe Coding"을 위한 전문 에이전트 - 웹 AI 빌더에
원활하게 전달할 수 있는 AI-Ready 컨텍스트 패키지를 생성합니다.
"""

from typing import Optional

from pydantic import Field, model_validator

from app.agent.browser import BrowserContextHelper
from app.agent.toolcall import ToolCallAgent
from app.config import config
from app.logger import logger
from app.prompt.bloom_prompt import SYSTEM_PROMPT, NEXT_STEP_PROMPT
from app.tool import PlanningTool, Terminate, ToolCollection
from app.tool.ask_human import AskHuman
from app.tool.browser_use_tool import BrowserUseTool
from app.tool.context_packager import ContextPackager
from app.tool.mcp import MCPClients, MCPClientTool
from app.tool.python_execute import PythonExecute
from app.tool.str_replace_editor import StrReplaceEditor


class JeongongBloom(ToolCallAgent):
    """
    Jeongong Bloom (정공블룸) - Vibe Coding을 위한 AI 설계 에이전트.
    
    이 에이전트의 전문 분야:
    1. 추상적인 프로젝트 아이디어 이해
    2. 풀스택 아키텍처 설계
    3. 최적화된 코드 구조 생성
    4. AI-Ready 컨텍스트 블록으로 패키징
    """

    name: str = "JeongongBloom"
    description: str = (
        "풀스택 프로젝트를 설계하고 웹 AI 빌더에 원활하게 전달할 수 있는 "
        "AI-Ready 컨텍스트 패키지를 생성하는 전문 AI 설계자입니다."
    )

    system_prompt: str = SYSTEM_PROMPT.format(directory=config.workspace_root)
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 15000  # 더 큰 컨텍스트를 위해 증가
    max_steps: int = 30  # 복잡한 아키텍처를 위해 더 많은 단계

    # MCP 클라이언트 (원격 도구 접근용)
    mcp_clients: MCPClients = Field(default_factory=MCPClients)

    # JeongongBloom 도구 모음 - ContextPackager 포함
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            PlanningTool(),
            ContextPackager(),
            PythonExecute(),
            BrowserUseTool(),
            StrReplaceEditor(),
            AskHuman(),
            Terminate(),
        )
    )

    special_tool_names: list[str] = Field(default_factory=lambda: [Terminate().name])
    browser_context_helper: Optional[BrowserContextHelper] = None
    _initialized: bool = False

    @model_validator(mode="after")
    def initialize_helper(self) -> "JeongongBloom":
        """기본 컴포넌트를 동기적으로 초기화합니다."""
        self.browser_context_helper = BrowserContextHelper(self)
        return self

    @classmethod
    async def create(cls, **kwargs) -> "JeongongBloom":
        """JeongongBloom 인스턴스를 생성하고 초기화하는 팩토리 메서드."""
        instance = cls(**kwargs)
        await instance.initialize_mcp_servers()
        instance._initialized = True
        return instance

    async def initialize_mcp_servers(self) -> None:
        """Initialize connections to configured MCP servers."""
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
        stdio_args: list = None,
    ) -> None:
        """Connect to an MCP server and add its tools."""
        if use_stdio:
            await self.mcp_clients.connect_stdio(
                server_url, stdio_args or [], server_id
            )
        else:
            await self.mcp_clients.connect_sse(server_url, server_id)

        # Update available tools with the new tools from this server
        new_tools = [
            tool for tool in self.mcp_clients.tools if tool.server_id == server_id
        ]
        self.available_tools.add_tools(*new_tools)

    async def disconnect_mcp_server(self, server_id: str = "") -> None:
        """Disconnect from an MCP server and remove its tools."""
        await self.mcp_clients.disconnect(server_id)

        # Rebuild available tools without the disconnected server's tools
        base_tools = [
            tool
            for tool in self.available_tools.tools
            if not isinstance(tool, MCPClientTool)
        ]
        self.available_tools = ToolCollection(*base_tools)
        self.available_tools.add_tools(*self.mcp_clients.tools)

    async def cleanup(self):
        """Clean up VibeManus agent resources."""
        if self.browser_context_helper:
            await self.browser_context_helper.cleanup_browser()
        if self._initialized:
            await self.disconnect_mcp_server()
            self._initialized = False

    async def think(self) -> bool:
        """Process current state and decide next actions with appropriate context."""
        if not self._initialized:
            await self.initialize_mcp_servers()
            self._initialized = True

        original_prompt = self.next_step_prompt
        recent_messages = self.memory.messages[-3:] if self.memory.messages else []
        browser_in_use = any(
            tc.function.name == BrowserUseTool().name
            for msg in recent_messages
            if msg.tool_calls
            for tc in msg.tool_calls
        )

        if browser_in_use:
            self.next_step_prompt = (
                await self.browser_context_helper.format_next_step_prompt()
            )

        result = await super().think()

        # Restore original prompt
        self.next_step_prompt = original_prompt

        return result
