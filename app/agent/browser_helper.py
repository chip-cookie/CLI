"""
BrowserContextHelper - 브라우저 상태 관리 헬퍼
=============================================
여러 에이전트에서 공유되는 브라우저 컨텍스트 관리 로직을 분리합니다.
"""

import json
from typing import TYPE_CHECKING, Optional

from app.logger import logger
from app.prompt.browser import NEXT_STEP_PROMPT
from app.schema import Message
from app.tool import BrowserUseTool

if TYPE_CHECKING:
    from app.agent.base import BaseAgent


class BrowserContextHelper:
    """브라우저 상태 관리를 담당하는 헬퍼 클래스.
    
    여러 에이전트(BrowserAgent, Manus, JeongongBloom)에서 공유되어
    브라우저 상태 조회 및 프롬프트 포맷팅을 처리합니다.
    
    Attributes:
        agent: 연결된 에이전트 인스턴스
        _current_base64_image: 현재 브라우저 스크린샷 (base64)
    """
    
    def __init__(self, agent: "BaseAgent"):
        """BrowserContextHelper를 초기화합니다.
        
        Args:
            agent: 이 헬퍼를 사용하는 에이전트 인스턴스
        """
        self.agent = agent
        self._current_base64_image: Optional[str] = None

    async def get_browser_state(self) -> Optional[dict]:
        """현재 브라우저 상태를 조회합니다.
        
        Returns:
            브라우저 상태 딕셔너리 또는 None (실패 시)
        """
        browser_tool = self.agent.available_tools.get_tool(BrowserUseTool().name)
        
        if not browser_tool or not hasattr(browser_tool, "get_current_state"):
            logger.warning("BrowserUseTool not found or doesn't have get_current_state")
            return None
            
        try:
            result = await browser_tool.get_current_state()
            if result.error:
                logger.debug(f"Browser state error: {result.error}")
                return None
                
            if hasattr(result, "base64_image") and result.base64_image:
                self._current_base64_image = result.base64_image
            else:
                self._current_base64_image = None
                
            return json.loads(result.output)
        except Exception as e:
            logger.debug(f"Failed to get browser state: {str(e)}")
            return None

    async def format_next_step_prompt(self) -> str:
        """브라우저 상태를 기반으로 다음 단계 프롬프트를 포맷팅합니다.
        
        Returns:
            포맷팅된 프롬프트 문자열
        """
        browser_state = await self.get_browser_state()
        url_info, tabs_info, content_above_info, content_below_info = "", "", "", ""
        results_info = ""

        if browser_state and not browser_state.get("error"):
            url_info = f"\n   URL: {browser_state.get('url', 'N/A')}\n   Title: {browser_state.get('title', 'N/A')}"
            
            tabs = browser_state.get("tabs", [])
            if tabs:
                tabs_info = f"\n   {len(tabs)} tab(s) available"
                
            pixels_above = browser_state.get("pixels_above", 0)
            pixels_below = browser_state.get("pixels_below", 0)
            
            if pixels_above > 0:
                content_above_info = f" ({pixels_above} pixels)"
            if pixels_below > 0:
                content_below_info = f" ({pixels_below} pixels)"

            if self._current_base64_image:
                image_message = Message.user_message(
                    content="Current browser screenshot:",
                    base64_image=self._current_base64_image,
                )
                self.agent.memory.add_message(image_message)
                self._current_base64_image = None  # 이미지 사용 후 초기화

        return NEXT_STEP_PROMPT.format(
            url_placeholder=url_info,
            tabs_placeholder=tabs_info,
            content_above_placeholder=content_above_info,
            content_below_placeholder=content_below_info,
            results_placeholder=results_info,
        )

    async def cleanup_browser(self) -> None:
        """브라우저 리소스를 정리합니다."""
        browser_tool = self.agent.available_tools.get_tool(BrowserUseTool().name)
        if browser_tool and hasattr(browser_tool, "cleanup"):
            await browser_tool.cleanup()
