"""
Jeongong Bloom (정공블룸) 에이전트
==================================
"Vibe Coding"을 위한 전문 에이전트 - 웹 AI 빌더에
원활하게 전달할 수 있는 AI-Ready 컨텍스트 패키지를 생성합니다.
"""

from typing import Optional

from pydantic import Field, model_validator

from app.agent.browser_helper import BrowserContextHelper
from app.agent.mcp_mixin import MCPMixin
from app.agent.toolcall import ToolCallAgent
from app.config import config
from app.prompt.bloom_prompt import SYSTEM_PROMPT, NEXT_STEP_PROMPT
from app.tool import PlanningTool, Terminate, ToolCollection
from app.tool.ask_human import AskHuman
from app.tool.browser_use_tool import BrowserUseTool
from app.tool.context_packager import ContextPackager
from app.tool.mcp import MCPClients
from app.tool.python_execute import PythonExecute
from app.tool.str_replace_editor import StrReplaceEditor


class JeongongBloom(MCPMixin, ToolCallAgent):
    """Jeongong Bloom (정공블룸) - Vibe Coding을 위한 AI 설계 에이전트.
    
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

    # MCP 클라이언트 (MCPMixin에서 필요)
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

    async def cleanup(self):
        """JeongongBloom 에이전트 리소스를 정리합니다."""
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
