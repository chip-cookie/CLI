"""
Design Phases - 설계 단계 정의
==============================
InteractiveAgent의 인터랙티브 설계 워크플로우에서 사용되는
설계 단계와 상태 관리 클래스를 정의합니다.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


class DesignPhase(str, Enum):
    """설계 워크플로우의 각 단계를 정의합니다."""
    
    REQUIREMENTS = "requirements"    # 요구사항 분석
    BACKEND = "backend"              # 백엔드 설계
    FRONTEND = "frontend"            # 프론트엔드 설계
    INTEGRATION = "integration"      # 통합 설계
    REVIEW = "review"                # 최종 검토
    COMPLETE = "complete"            # 완료

    @property
    def display_name(self) -> str:
        """한글 표시 이름을 반환합니다."""
        names = {
            "requirements": "📋 요구사항 분석",
            "backend": "⚙️ 백엔드 설계",
            "frontend": "🎨 프론트엔드 설계",
            "integration": "🔗 통합 설계",
            "review": "✅ 최종 검토",
            "complete": "📦 완료",
        }
        return names.get(self.value, self.value)

    @property
    def next_phase(self) -> Optional["DesignPhase"]:
        """다음 단계를 반환합니다."""
        order = list(DesignPhase)
        try:
            idx = order.index(self)
            if idx < len(order) - 1:
                return order[idx + 1]
        except ValueError:
            pass
        return None

    @classmethod
    def from_keyword(cls, keyword: str) -> Optional["DesignPhase"]:
        """키워드로 단계를 찾습니다."""
        keyword = keyword.lower().strip()
        mappings = {
            "요구사항": cls.REQUIREMENTS,
            "requirements": cls.REQUIREMENTS,
            "백엔드": cls.BACKEND,
            "backend": cls.BACKEND,
            "서버": cls.BACKEND,
            "프론트엔드": cls.FRONTEND,
            "frontend": cls.FRONTEND,
            "ui": cls.FRONTEND,
            "사이트": cls.FRONTEND,
            "통합": cls.INTEGRATION,
            "integration": cls.INTEGRATION,
            "검토": cls.REVIEW,
            "review": cls.REVIEW,
        }
        return mappings.get(keyword)


class UserAction(str, Enum):
    """사용자 응답에 대한 액션 유형."""
    
    PROCEED = "proceed"         # 다음 단계로 진행
    MODIFY = "modify"           # 현재 단계 수정
    JUMP = "jump"               # 특정 단계로 이동
    CONFIRM_YES = "confirm_yes" # 최종 확인 Y
    CONFIRM_NO = "confirm_no"   # 최종 확인 N
    UNKNOWN = "unknown"         # 알 수 없는 응답


@dataclass
class PhaseDesign:
    """각 단계의 설계 내용을 저장합니다."""
    
    phase: DesignPhase
    content: Dict[str, Any] = field(default_factory=dict)
    confirmed: bool = False
    modified_at: Optional[datetime] = None
    modifications: List[str] = field(default_factory=list)

    def update(self, changes: Dict[str, Any], reason: str = "") -> None:
        """설계 내용을 업데이트합니다."""
        self.content.update(changes)
        self.modified_at = datetime.now()
        if reason:
            self.modifications.append(f"[{self.modified_at.strftime('%H:%M')}] {reason}")
        self.confirmed = False


@dataclass
class DesignState:
    """전체 설계 상태를 관리합니다."""
    
    current_phase: DesignPhase = DesignPhase.REQUIREMENTS
    phases: Dict[DesignPhase, PhaseDesign] = field(default_factory=dict)
    project_name: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """모든 단계에 대한 빈 설계를 초기화합니다."""
        for phase in DesignPhase:
            if phase not in self.phases:
                self.phases[phase] = PhaseDesign(phase=phase)

    def get_current_design(self) -> PhaseDesign:
        """현재 단계의 설계를 반환합니다."""
        return self.phases[self.current_phase]

    def update_current(self, changes: Dict[str, Any], reason: str = "") -> None:
        """현재 단계의 설계를 업데이트합니다."""
        self.phases[self.current_phase].update(changes, reason)

    def confirm_current(self) -> None:
        """현재 단계를 확인 완료로 표시합니다."""
        self.phases[self.current_phase].confirmed = True

    def advance_phase(self) -> bool:
        """다음 단계로 진행합니다."""
        next_phase = self.current_phase.next_phase
        if next_phase:
            self.confirm_current()
            self.current_phase = next_phase
            return True
        return False

    def jump_to_phase(self, phase: DesignPhase) -> None:
        """특정 단계로 이동합니다."""
        self.current_phase = phase

    def get_summary(self) -> Dict[str, Any]:
        """전체 설계 요약을 반환합니다."""
        return {
            "project_name": self.project_name,
            "current_phase": self.current_phase.display_name,
            "phases": {
                phase.value: {
                    "confirmed": design.confirmed,
                    "content": design.content,
                }
                for phase, design in self.phases.items()
                if design.content
            },
        }

    def is_complete(self) -> bool:
        """모든 필수 단계가 완료되었는지 확인합니다."""
        required_phases = [
            DesignPhase.REQUIREMENTS,
            DesignPhase.BACKEND,
            DesignPhase.FRONTEND,
        ]
        return all(self.phases[p].confirmed for p in required_phases)
