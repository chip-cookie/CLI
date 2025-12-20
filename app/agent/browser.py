"""
BrowserAgent - 브라우저 제어 에이전트
====================================
browser_use 라이브러리를 사용하여 브라우저를 제어하는 에이전트입니다.
"""

from typing import Optional

from pydantic import Field, model_validator

from app.agent.browser_helper import BrowserContextHelper
from app.agent.toolcall import ToolCallAgent
from app.prompt.browser import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.schema import ToolChoice
from app.tool import BrowserUseTool, Terminate, ToolCollection


class BrowserAgent(ToolCallAgent):
    """browser_use 라이브러리를 사용하여 브라우저를 제어하는 에이전트.

    이 에이전트는 웹 페이지 탐색, 요소 상호작용, 폼 작성,
    콘텐츠 추출 등의 브라우저 기반 작업을 수행할 수 있습니다.
    """

    name: str = "browser"
    description: str = "A browser agent that can control a browser to accomplish tasks"

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 10000
    max_steps: int = 20

    # 사용 가능한 도구 설정
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(BrowserUseTool(), Terminate())
    )

    # Auto 설정으로 도구 사용과 자유 형식 응답 모두 허용
    tool_choices: ToolChoice = ToolChoice.AUTO
    special_tool_names: list[str] = Field(default_factory=lambda: [Terminate().name])

    browser_context_helper: Optional[BrowserContextHelper] = None

    @model_validator(mode="after")
    def initialize_helper(self) -> "BrowserAgent":
        """BrowserContextHelper를 초기화합니다."""
        self.browser_context_helper = BrowserContextHelper(self)
        return self

    async def think(self) -> bool:
        """브라우저 상태 정보를 추가하여 현재 상태를 처리하고 다음 작업을 결정합니다."""
        self.next_step_prompt = (
            await self.browser_context_helper.format_next_step_prompt()
        )
        return await super().think()

    async def cleanup(self):
        """부모 cleanup을 호출하여 브라우저 에이전트 리소스를 정리합니다."""
        await self.browser_context_helper.cleanup_browser()
