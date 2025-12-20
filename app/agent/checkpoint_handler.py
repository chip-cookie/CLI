"""
Checkpoint Handler - 사용자 확인 체크포인트 처리
================================================
설계 워크플로우에서 사용자 확인을 요청하고 응답을 처리합니다.
"""

import re
from typing import Optional, Tuple

from app.agent.design_phases import DesignPhase, DesignState, UserAction


# 체크포인트 메시지 템플릿
CHECKPOINT_TEMPLATES = {
    DesignPhase.REQUIREMENTS: """
📋 **요구사항 분석이 완료되었습니다!**

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 수정할 내용을 입력하거나 **'다음'**을 입력하세요.
""",

    DesignPhase.BACKEND: """
⚙️ **백엔드 설계가 완료되었습니다!**

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 수정할 내용을 입력하거나 **'다음'**을 입력하세요.
   (예: "MySQL말고 SQLite로 변경해")
""",

    DesignPhase.FRONTEND: """
🎨 **프론트엔드 설계가 완료되었습니다!**

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 수정할 내용을 입력하거나 **'다음'**을 입력하세요.
   (예: "React말고 Vue로 변경해")
""",

    DesignPhase.INTEGRATION: """
🔗 **통합 설계가 완료되었습니다!**

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 수정할 내용을 입력하거나 **'다음'**을 입력하세요.
""",

    DesignPhase.REVIEW: """
✅ **모든 설계가 완료되었습니다!**

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 최종 확인: 이대로 진행하시겠습니까? **(Y/N)**
   - **Y**: 패키지 생성 진행
   - **N**: 수정할 영역 선택 (예: "백엔드", "프론트엔드")
""",
}

# 진행 키워드
PROCEED_KEYWORDS = ["다음", "next", "진행", "확인", "ok", "ㅇㅋ", "넘어가", "계속"]

# 확인 키워드
CONFIRM_YES_KEYWORDS = ["y", "yes", "네", "예", "ㅇ", "응"]
CONFIRM_NO_KEYWORDS = ["n", "no", "아니", "아니오", "ㄴ"]


class CheckpointHandler:
    """설계 워크플로우의 체크포인트를 처리합니다."""

    def __init__(self, design_state: DesignState):
        """
        Args:
            design_state: 현재 설계 상태
        """
        self.state = design_state

    def format_checkpoint_message(self, summary: str) -> str:
        """현재 단계의 체크포인트 메시지를 포맷팅합니다.
        
        Args:
            summary: 현재 설계 요약 문자열
            
        Returns:
            포맷팅된 체크포인트 메시지
        """
        template = CHECKPOINT_TEMPLATES.get(
            self.state.current_phase,
            "설계를 확인해주세요:\n{summary}\n\n다음으로 진행하시겠습니까?"
        )
        return template.format(summary=summary)

    def format_design_summary(self, design_content: dict) -> str:
        """설계 내용을 보기 좋게 포맷팅합니다.
        
        Args:
            design_content: 설계 내용 딕셔너리
            
        Returns:
            포맷팅된 설계 요약 문자열
        """
        if not design_content:
            return "(아직 설계 내용이 없습니다)"
        
        lines = ["┌─────────────────────────────────┐"]
        for key, value in design_content.items():
            display_key = self._format_key(key)
            if isinstance(value, list):
                value_str = ", ".join(str(v) for v in value)
            else:
                value_str = str(value)
            lines.append(f"│ {display_key}: {value_str}")
        lines.append("└─────────────────────────────────┘")
        return "\n".join(lines)

    def _format_key(self, key: str) -> str:
        """키 이름을 표시용으로 포맷팅합니다."""
        key_mappings = {
            "database": "DB",
            "api_framework": "API",
            "auth": "인증",
            "frontend_framework": "프레임워크",
            "ui_library": "UI 라이브러리",
            "state_management": "상태관리",
            "project_type": "프로젝트 타입",
            "main_features": "주요 기능",
        }
        return key_mappings.get(key, key.replace("_", " ").title())

    def parse_user_response(self, response: str) -> Tuple[UserAction, Optional[str]]:
        """사용자 응답을 파싱하여 액션을 결정합니다.
        
        Args:
            response: 사용자 입력 문자열
            
        Returns:
            (액션 유형, 추가 데이터) 튜플
            - PROCEED: 다음 단계 진행, None
            - MODIFY: 현재 단계 수정, 수정 요청 내용
            - JUMP: 특정 단계로 이동, 단계 이름
            - CONFIRM_YES/NO: 최종 확인, None
        """
        response = response.strip().lower()
        
        # 빈 응답
        if not response:
            return UserAction.UNKNOWN, None
        
        # 최종 확인 단계에서의 Y/N 체크
        if self.state.current_phase == DesignPhase.REVIEW:
            if response in CONFIRM_YES_KEYWORDS:
                return UserAction.CONFIRM_YES, None
            if response in CONFIRM_NO_KEYWORDS:
                return UserAction.CONFIRM_NO, None
        
        # 진행 키워드 체크
        if response in PROCEED_KEYWORDS:
            return UserAction.PROCEED, None
        
        # 특정 단계로 점프 체크
        for keyword in response.split():
            phase = DesignPhase.from_keyword(keyword)
            if phase:
                return UserAction.JUMP, phase.value
        
        # 그 외는 수정 요청으로 처리
        return UserAction.MODIFY, response

    def extract_modification_intent(self, user_input: str) -> dict:
        """수정 요청에서 의도를 추출합니다.
        
        Args:
            user_input: 사용자 수정 요청 (예: "MySQL말고 SQLite로 변경해")
            
        Returns:
            추출된 수정 의도 딕셔너리
        """
        intent = {
            "original": user_input,
            "changes": [],
        }
        
        # "A말고 B로" 패턴 추출
        pattern = r"(\w+)\s*말고\s*(\w+)"
        matches = re.findall(pattern, user_input, re.IGNORECASE)
        for old, new in matches:
            intent["changes"].append({
                "from": old,
                "to": new,
            })
        
        # "A에서 B로 변경" 패턴
        pattern2 = r"(\w+)\s*에서\s*(\w+)\s*로"
        matches2 = re.findall(pattern2, user_input, re.IGNORECASE)
        for old, new in matches2:
            intent["changes"].append({
                "from": old,
                "to": new,
            })
        
        # "A를 B로" 패턴
        pattern3 = r"(\w+)\s*를?\s*(\w+)\s*로\s*(변경|바꿔|교체)?"
        matches3 = re.findall(pattern3, user_input, re.IGNORECASE)
        for old, new, _ in matches3:
            if old.lower() not in ["다음", "이거", "이것"]:
                intent["changes"].append({
                    "from": old,
                    "to": new,
                })
        
        return intent

    def get_phase_transition_message(self, from_phase: DesignPhase, to_phase: DesignPhase) -> str:
        """단계 전환 메시지를 반환합니다."""
        return f"\n🔄 {from_phase.display_name} → {to_phase.display_name}\n"

    def get_modification_confirm_message(self, changes: list) -> str:
        """수정 확인 메시지를 반환합니다."""
        if not changes:
            return "수정 사항을 이해하지 못했습니다. 다시 입력해주세요."
        
        lines = ["🔧 다음과 같이 수정합니다:"]
        for change in changes:
            lines.append(f"  • {change['from']} → {change['to']} ✅")
        return "\n".join(lines)
