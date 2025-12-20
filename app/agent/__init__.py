"""
Agent 모듈
==========
AI 에이전트 클래스들을 포함합니다.

계층 구조:
- BaseAgent: 모든 에이전트의 기본 클래스
- ReActAgent: ReAct 패턴 기반 에이전트
- ToolCallAgent: 도구 호출 기능을 가진 에이전트
- MCPMixin: MCP 서버 연결 기능 믹스인

전문 에이전트:
- Manus: 범용 멀티툴 에이전트
- JeongongBloom: Vibe Coding 전문 에이전트
- BrowserAgent: 브라우저 자동화 에이전트
- MCPAgent: MCP 프로토콜 에이전트
- SWEAgent: 소프트웨어 엔지니어링 에이전트
"""

from app.agent.base import BaseAgent
from app.agent.browser import BrowserAgent
from app.agent.browser_helper import BrowserContextHelper
from app.agent.checkpoint_handler import CheckpointHandler
from app.agent.design_phases import DesignPhase, DesignState, UserAction
from app.agent.mcp import MCPAgent
from app.agent.mcp_mixin import MCPMixin
from app.agent.react import ReActAgent
from app.agent.swe import SWEAgent
from app.agent.toolcall import ToolCallAgent
from app.agent.manus import Manus
from app.agent.bloom_agent import JeongongBloom


__all__ = [
    # Base classes
    "BaseAgent",
    "ReActAgent",
    "ToolCallAgent",
    # Mixins and helpers
    "MCPMixin",
    "BrowserContextHelper",
    "CheckpointHandler",
    # Design workflow
    "DesignPhase",
    "DesignState",
    "UserAction",
    # Specialized agents
    "BrowserAgent",
    "MCPAgent",
    "SWEAgent",
    "Manus",
    "JeongongBloom",
]
