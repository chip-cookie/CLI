"""
Design Document Tool - 설계 문서 관리 도구
==========================================
설계 문서를 생성, 수정, 조회하는 도구입니다.
"""

import json
from typing import Any, Dict, Optional

from app.tool.base import BaseTool, ToolResult


class DesignDocumentTool(BaseTool):
    """설계 문서를 관리하는 도구.
    
    JeongongBloom 에이전트가 설계 문서를 단계별로 작성하고
    사용자 피드백에 따라 수정할 수 있게 합니다.
    """
    
    name: str = "design_document"
    description: str = """설계 문서를 관리합니다. 다음 작업을 수행할 수 있습니다:
    - create_section: 설계 섹션 생성
    - modify_section: 설계 섹션 수정
    - get_design: 현재 설계 조회
    - validate: 설계 검증"""
    
    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["create_section", "modify_section", "get_design", "validate"],
                "description": "수행할 작업"
            },
            "section": {
                "type": "string",
                "enum": ["requirements", "backend", "frontend", "integration"],
                "description": "대상 섹션"
            },
            "content": {
                "type": "object",
                "description": "섹션 내용 (create/modify 시 사용)"
            }
        },
        "required": ["action"]
    }
    
    # 내부 설계 문서 저장소
    _document: Dict[str, Dict[str, Any]] = {}
    
    async def execute(
        self,
        action: str,
        section: Optional[str] = None,
        content: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ToolResult:
        """도구 실행.
        
        Args:
            action: 수행할 작업
            section: 대상 섹션
            content: 섹션 내용
            
        Returns:
            ToolResult: 실행 결과
        """
        try:
            if action == "create_section":
                return await self._create_section(section, content)
            elif action == "modify_section":
                return await self._modify_section(section, content)
            elif action == "get_design":
                return await self._get_design(section)
            elif action == "validate":
                return await self._validate_design()
            else:
                return self.fail_response(f"알 수 없는 작업: {action}")
        except Exception as e:
            return self.fail_response(f"오류 발생: {str(e)}")

    async def _create_section(
        self, 
        section: str, 
        content: Dict[str, Any]
    ) -> ToolResult:
        """설계 섹션을 생성합니다."""
        if not section:
            return self.fail_response("섹션 이름이 필요합니다")
        if not content:
            return self.fail_response("섹션 내용이 필요합니다")
        
        self._document[section] = content
        return self.success_response({
            "status": "created",
            "section": section,
            "content": content
        })

    async def _modify_section(
        self, 
        section: str, 
        content: Dict[str, Any]
    ) -> ToolResult:
        """설계 섹션을 수정합니다."""
        if not section:
            return self.fail_response("섹션 이름이 필요합니다")
        if section not in self._document:
            return self.fail_response(f"섹션 '{section}'이 존재하지 않습니다")
        
        # 기존 내용에 새 내용 병합
        old_content = self._document[section].copy()
        self._document[section].update(content or {})
        
        return self.success_response({
            "status": "modified",
            "section": section,
            "old_content": old_content,
            "new_content": self._document[section],
            "changes": content
        })

    async def _get_design(self, section: Optional[str] = None) -> ToolResult:
        """설계 내용을 조회합니다."""
        if section:
            if section not in self._document:
                return self.fail_response(f"섹션 '{section}'이 존재하지 않습니다")
            return self.success_response({
                "section": section,
                "content": self._document[section]
            })
        
        return self.success_response({
            "document": self._document,
            "sections": list(self._document.keys())
        })

    async def _validate_design(self) -> ToolResult:
        """설계의 완전성을 검증합니다."""
        required_sections = ["requirements", "backend", "frontend"]
        missing = [s for s in required_sections if s not in self._document]
        
        issues = []
        
        # 필수 섹션 체크
        if missing:
            issues.append(f"누락된 섹션: {', '.join(missing)}")
        
        # 백엔드 설계 체크
        if "backend" in self._document:
            backend = self._document["backend"]
            if not backend.get("database"):
                issues.append("백엔드: 데이터베이스 미지정")
            if not backend.get("api_framework"):
                issues.append("백엔드: API 프레임워크 미지정")
        
        # 프론트엔드 설계 체크
        if "frontend" in self._document:
            frontend = self._document["frontend"]
            if not frontend.get("framework"):
                issues.append("프론트엔드: 프레임워크 미지정")
        
        if issues:
            return self.success_response({
                "valid": False,
                "issues": issues,
                "message": "설계에 누락된 부분이 있습니다"
            })
        
        return self.success_response({
            "valid": True,
            "message": "설계가 완전합니다",
            "sections": list(self._document.keys())
        })

    def reset(self) -> None:
        """설계 문서를 초기화합니다."""
        self._document = {}

    def get_formatted_summary(self) -> str:
        """설계 내용을 보기 좋게 포맷팅하여 반환합니다."""
        if not self._document:
            return "(설계 내용 없음)"
        
        lines = []
        section_icons = {
            "requirements": "📋",
            "backend": "⚙️",
            "frontend": "🎨",
            "integration": "🔗",
        }
        
        for section, content in self._document.items():
            icon = section_icons.get(section, "📄")
            lines.append(f"\n{icon} **{section.upper()}**")
            for key, value in content.items():
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                lines.append(f"  • {key}: {value}")
        
        return "\n".join(lines)
