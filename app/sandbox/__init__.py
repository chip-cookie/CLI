"""
Sandbox 모듈
============
코드 실행을 위한 샌드박스 환경을 제공합니다.

포함 내용:
- client: 샌드박스 클라이언트
- core: 샌드박스 핵심 기능 (manager, terminal, sandbox, exceptions)
"""

from app.sandbox.client import SANDBOX_CLIENT


__all__ = [
    "SANDBOX_CLIENT",
]
