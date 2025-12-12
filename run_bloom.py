"""
Jeongong Bloom (정공블룸) - Vibe Coding CLI
=============================================
Jeongong Bloom CLI의 메인 엔트리 포인트.
AI 기반 설계 에이전트로 "AI-Ready Context Package"를 생성합니다.
"""

import asyncio
import sys

from app.agent.bloom_agent import JeongongBloom
from app.logger import logger


async def run_bloom():
    """Jeongong Bloom 에이전트를 Vibe Coding 워크플로우로 실행합니다."""
    
    print("\n" + "=" * 60)
    print("🌸 Jeongong Bloom (정공블룸) - Vibe Coding CLI")
    print("=" * 60)
    print("\n웹 AI 빌더(v0, Bolt, ChatGPT 등)에 최적화된")
    print("코드 패키지를 생성하는 AI 설계자입니다.\n")
    print("프로젝트 아이디어를 입력하면 완벽한 설계도를 만들어드립니다.")
    print("종료하려면 'exit' 또는 'quit'을 입력하세요.\n")
    print("-" * 60 + "\n")
    
    agent = await JeongongBloom.create()
    
    try:
        while True:
            try:
                user_input = input("💡 아이디어: ").strip()
            except EOFError:
                break
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q', '종료']:
                print("\n👋 Jeongong Bloom을 이용해주셔서 감사합니다! 즐거운 코딩하세요!\n")
                break
            
            print("\n🔄 요청을 처리하고 있습니다...\n")
            
            try:
                result = await agent.run(user_input)
                print("\n" + "=" * 60)
                print("✅ Jeongong Bloom 출력")
                print("=" * 60)
                print(result if result else "작업이 완료되었습니다!")
                print("\n" + "-" * 60 + "\n")
            except KeyboardInterrupt:
                print("\n\n⚠️ 사용자에 의해 중단되었습니다.")
                break
            except Exception as e:
                logger.error(f"실행 중 오류 발생: {e}")
                print(f"\n❌ 오류: {e}\n")
    
    finally:
        await agent.cleanup()


def main():
    """메인 엔트리 포인트."""
    try:
        asyncio.run(run_bloom())
    except KeyboardInterrupt:
        print("\n\n👋 안녕히 가세요!")
        sys.exit(0)


if __name__ == "__main__":
    main()

