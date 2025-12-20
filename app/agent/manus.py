"""
Manus Agent - 범용 AI 에이전트
=============================
MCP 도구를 포함한 다양한 도구를 사용하여 범용 작업을 수행하는 에이전트입니다.
"""

from typing import Optional

from pydantic import Field, model_validator

from app.agent.browser_helper import BrowserContextHelper
from app.agent.mcp_mixin import MCPMixin
from app.agent.toolcall import ToolCallAgent
from app.config import config
from app.prompt.manus import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool import PlanningTool, Terminate, ToolCollection
from app.tool.ask_human import AskHuman
from app.tool.browser_use_tool import BrowserUseTool
from app.tool.mcp import MCPClients
from app.tool.python_execute import PythonExecute
from app.tool.str_replace_editor import StrReplaceEditor


class Manus(MCPMixin, ToolCallAgent):
    """MCP 기반 도구를 포함한 범용 에이전트.
    
    다양한 작업을 처리할 수 있는 범용 에이전트로, 로컬 도구와 
    MCP 기반 원격 도구를 모두 지원합니다.
    """

    name: str = "Manus"
    description: str = "A versatile agent that can solve various tasks using multiple tools including MCP-based tools"

    system_prompt: str = SYSTEM_PROMPT.format(directory=config.workspace_root)
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 10000
    max_steps: int = 20

    # MCP 클라이언트 (MCPMixin에서 필요)
    mcp_clients: MCPClients = Field(default_factory=MCPClients)

    # 도구 모음
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            PlanningTool(),
            PythonExecute(),
            BrowserUseTool(),
            StrReplaceEditor(),
            AskHuman(),
            Terminate(),
        )
    )

    special_tool_names: list[str] = Field(default_factory=lambda: [Terminate().name])
    browser_context_helper: Optional[BrowserContextHelper] = None

    @model_validator(mode="after")
    def initialize_helper(self) -> "Manus":
        """기본 컴포넌트를 동기적으로 초기화합니다."""
        self.browser_context_helper = BrowserContextHelper(self)
        return self

    @classmethod
    async def create(cls, **kwargs) -> "Manus":
        """Manus 인스턴스를 생성하고 초기화하는 팩토리 메서드."""
        instance = cls(**kwargs)
        await instance.initialize_mcp_servers()
        instance._initialized = True
        return instance

    async def cleanup(self):
        """Manus 에이전트 리소스를 정리합니다."""
        if self.browser_context_helper:
            await self.browser_context_helper.cleanup_browser()
        if self._initialized:
            await self.disconnect_mcp_server()
            self._initialized = False

    async def think(self) -> bool:
        """현재 상태를 처리하고 적절한 컨텍스트와 함께 다음 작업을 결정합니다."""
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

        # 원래 프롬프트 복원
        self.next_step_prompt = original_prompt

        return result
