"""
Manus Interactive Agent
=======================
"Vibe Coding"을 위한 전문 에이전트 - 웹 AI 빌더에
원활하게 전달할 수 있는 AI-Ready 컨텍스트 패키지를 생성합니다.

인터랙티브 설계 워크플로우:
- 각 설계 단계마다 사용자 확인 체크포인트
- 실시간 수정 반영
- 최종 Y/N 확인
"""

from typing import Optional

from pydantic import Field, model_validator

from app.agent.browser_helper import BrowserContextHelper
from app.agent.checkpoint_handler import CheckpointHandler
from app.agent.design_phases import DesignPhase, DesignState, UserAction
from app.agent.mcp_mixin import MCPMixin
from app.agent.toolcall import ToolCallAgent
from app.config import config
from app.logger import logger
from app.prompt.bloom_prompt import SYSTEM_PROMPT, NEXT_STEP_PROMPT, CHECKPOINT_MESSAGES
from app.tool import PlanningTool, Terminate, ToolCollection
from app.tool.ask_human import AskHuman
from app.tool.browser_use_tool import BrowserUseTool
from app.tool.context_packager import ContextPackager
from app.tool.design_document import DesignDocumentTool
from app.tool.mcp import MCPClients
from app.tool.python_execute import PythonExecute
from app.tool.str_replace_editor import StrReplaceEditor


class JeongongBloom(MCPMixin, ToolCallAgent):
    """OpenManus Interactive Architect - Vibe Coding을 위한 AI 설계 에이전트.
    
    이 에이전트의 전문 분야:
    1. 추상적인 프로젝트 아이디어 이해
    2. 풀스택 아키텍처 설계
    3. 최적화된 코드 구조 생성
    4. AI-Ready 컨텍스트 블록으로 패키징
    
    인터랙티브 워크플로우:
    - 각 단계(요구사항→백엔드→프론트엔드→검토)마다 사용자 확인
    - 실시간 수정 반영 (예: "MySQL말고 SQLite로")
    - 최종 Y/N 확인 후 패키지 생성
    """

    name: str = "ManusInteractive"
    description: str = (
        "풀스택 프로젝트를 설계하고 웹 AI 빌더에 원활하게 전달할 수 있는 "
        "AI-Ready 컨텍스트 패키지를 생성하는 전문 AI 설계자입니다."
    )

    system_prompt: str = SYSTEM_PROMPT.format(directory=config.workspace_root)
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 15000  # 더 큰 컨텍스트를 위해 증가
    max_steps: int = 50  # 인터랙티브 워크플로우를 위해 더 많은 단계

    # MCP 클라이언트 (MCPMixin에서 필요)
    mcp_clients: MCPClients = Field(default_factory=MCPClients)

    # 도구 모음 - DesignDocumentTool 포함
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            PlanningTool(),
            DesignDocumentTool(),
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
    
    # 설계 상태 관리
    design_state: DesignState = Field(default_factory=DesignState)
    checkpoint_handler: Optional[CheckpointHandler] = None

    @model_validator(mode="after")
    def initialize_helper(self) -> "JeongongBloom":
        """기본 컴포넌트를 동기적으로 초기화합니다."""
        self.browser_context_helper = BrowserContextHelper(self)
        self.checkpoint_handler = CheckpointHandler(self.design_state)
        return self

    @classmethod
    async def create(cls, **kwargs) -> "JeongongBloom":
        """인스턴스를 생성하고 초기화하는 팩토리 메서드."""
        instance = cls(**kwargs)
        await instance.initialize_mcp_servers()
        instance._initialized = True
        return instance

    async def cleanup(self):
        """에이전트 리소스를 정리합니다."""
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

    def get_checkpoint_message(self, summary: str = "") -> str:
        """현재 단계에 맞는 체크포인트 메시지를 반환합니다.
        
        Args:
            summary: 현재 설계 요약
            
        Returns:
            포맷팅된 체크포인트 메시지
        """
        phase = self.design_state.current_phase
        
        if phase == DesignPhase.REVIEW:
            template = CHECKPOINT_MESSAGES.get("final_review", "")
        else:
            template = CHECKPOINT_MESSAGES.get(phase.value, "")
        
        if not template:
            template = "설계를 확인해주세요:\n{summary}\n\n'다음'을 입력하면 진행합니다."
        
        return template.format(summary=summary)

    def process_user_response(self, response: str) -> tuple[UserAction, Optional[str]]:
        """사용자 응답을 처리합니다.
        
        Args:
            response: 사용자 입력
            
        Returns:
            (액션 유형, 추가 데이터) 튜플
        """
        return self.checkpoint_handler.parse_user_response(response)

    def apply_modification(self, modification: str) -> str:
        """사용자 수정 요청을 적용합니다.
        
        Args:
            modification: 수정 요청 문자열
            
        Returns:
            수정 결과 메시지
        """
        intent = self.checkpoint_handler.extract_modification_intent(modification)
        
        if not intent["changes"]:
            return "수정 사항을 이해하지 못했습니다. 다시 입력해주세요."
        
        # 설계 상태에 수정 적용
        current_design = self.design_state.get_current_design()
        for change in intent["changes"]:
            # 현재 설계에서 변경할 항목 찾기
            for key, value in current_design.content.items():
                if isinstance(value, str) and change["from"].lower() in value.lower():
                    current_design.content[key] = value.replace(
                        change["from"], change["to"]
                    ).replace(
                        change["from"].lower(), change["to"]
                    ).replace(
                        change["from"].upper(), change["to"].upper()
                    )
        
        # 수정 이력 추가
        self.design_state.update_current({}, modification)
        
        return self.checkpoint_handler.get_modification_confirm_message(intent["changes"])

    def advance_to_next_phase(self) -> str:
        """다음 설계 단계로 진행합니다.
        
        Returns:
            단계 전환 메시지
        """
        current = self.design_state.current_phase
        if self.design_state.advance_phase():
            next_phase = self.design_state.current_phase
            return self.checkpoint_handler.get_phase_transition_message(current, next_phase)
        return "이미 마지막 단계입니다."

    def jump_to_phase(self, phase_name: str) -> str:
        """특정 설계 단계로 이동합니다.
        
        Args:
            phase_name: 이동할 단계 이름
            
        Returns:
            이동 결과 메시지
        """
        phase = DesignPhase.from_keyword(phase_name)
        if phase:
            self.design_state.jump_to_phase(phase)
            return f"🔄 {phase.display_name} 단계로 이동합니다."
        return f"알 수 없는 단계: {phase_name}"

    def get_design_summary(self) -> dict:
        """현재 전체 설계 요약을 반환합니다."""
        return self.design_state.get_summary()

    def is_workflow_complete(self) -> bool:
        """워크플로우가 완료되었는지 확인합니다."""
        return self.design_state.is_complete()
