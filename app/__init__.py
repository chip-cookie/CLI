"""
App 패키지
==========
CLI 애플리케이션의 핵심 모듈을 포함합니다.

주요 컴포넌트:
- config: 애플리케이션 설정 관리
- llm: LLM 클라이언트 (OpenAI, Azure, Bedrock 등)
- logger: 로깅 유틸리티
- schema: 데이터 스키마 정의 (Message, Memory 등)
- exceptions: 커스텀 예외 정의

서브패키지:
- agent: AI 에이전트 클래스들
- tool: 도구 클래스들
- flow: 실행 흐름 관리
- prompt: 프롬프트 템플릿
- mcp: MCP 서버 관련
- sandbox: 샌드박스 실행 환경
- daytona: Daytona 통합
"""

import sys


# Python 버전 체크: 3.11-3.13
if sys.version_info < (3, 11) or sys.version_info > (3, 13):
    print(
        "Warning: Unsupported Python version {ver}, please use 3.11-3.13".format(
            ver=".".join(map(str, sys.version_info))
        )
    )

# 핵심 모듈 import
from app.config import config
from app.llm import LLM
from app.logger import logger


__all__ = [
    "config",
    "LLM",
    "logger",
]
