"""
Prompt 모듈
===========
각 에이전트에 대한 시스템 프롬프트와 다음 단계 프롬프트를 정의합니다.

사용법:
    from app.prompt import manus
    system_prompt = manus.SYSTEM_PROMPT
    next_step_prompt = manus.NEXT_STEP_PROMPT
"""

from app.prompt import (
    bloom_prompt,
    browser,
    manus,
    mcp,
    planning,
    swe,
    toolcall,
    visualization,
)


__all__ = [
    "bloom_prompt",
    "browser",
    "manus",
    "mcp",
    "planning",
    "swe",
    "toolcall",
    "visualization",
]
