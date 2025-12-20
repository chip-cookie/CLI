"""
Prompt 패키지
=============
에이전트별 시스템 프롬프트와 메시지 템플릿을 포함합니다.

포함 내용:
- manus: Manus 에이전트 프롬프트
- interactive_prompt: 인터랙티브 설계 에이전트 프롬프트
- browser: 브라우저 에이전트 프롬프트
- mcp: MCP 에이전트 프롬프트
- planning: 계획 도구 프롬프트
- swe: SWE 에이전트 프롬프트
- toolcall: 도구호출 에이전트 프롬프트
- visualization: 시각화 프롬프트
"""

from app.prompt import (
    browser,
    interactive_prompt,
    manus,
    mcp,
    planning,
    swe,
    toolcall,
    visualization,
)


__all__ = [
    "browser",
    "interactive_prompt",
    "manus",
    "mcp",
    "planning",
    "swe",
    "toolcall",
    "visualization",
]
