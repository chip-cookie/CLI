"""
Manus Interactive CLI
=====================
Manus 에이전트의 인터랙티브 모드 실행 엔트리 포인트.
AI 기반 설계 에이전트로 "AI-Ready Context Package"를 생성합니다.
"""

import asyncio
import sys
from enum import Enum

from app.agent.interactive_agent import InteractiveAgent
from app.config import config
from app.logger import logger
from app.utils.git_utils import clone_repo, get_repo_name, is_git_installed

class ProjectType(Enum):
    WEB = "web"
    APP = "app"
    GUI = "gui"
    OTHER = "other"

class ProjectSource(Enum):
    NEW = "new"
    GITHUB = "github"

async def run_interactive():
    """Manus 에이전트를 인터랙티브 모드로 실행합니다."""
    
    print("\n" + "=" * 60)
    print("🤖 Manus Interactive CLI")
    print("=" * 60)
    print("\n웹 AI 빌더(v0, Bolt, ChatGPT 등)에 최적화된")
    print("코드 패키지를 생성하는 AI 설계자입니다.\n")
    
    # 1. 프로젝트 기본 정보
    print("-" * 60)
    print("📝 프로젝트 설정")
    project_name = input("   프로젝트 이름을 입력하세요 (기본값: default): ").strip()
    if not project_name:
        project_name = "default"
        
    # 2. 소스 선택 (GitHub vs New)
    print("\n📦 프로젝트 소스 선택:")
    print("   1. ✨ 새 프로젝트 만들기 (Scaffolding)")
    print("   2. 🐙 GitHub 레포지토리 가져오기 (Clone & Evolve)")
    
    source_choice = input("   선택 (1/2): ").strip()
    source = ProjectSource.GITHUB if source_choice == "2" else ProjectSource.NEW
    
    github_url = ""
    if source == ProjectSource.GITHUB:
        if not is_git_installed():
            print("⚠️ 경고: Git이 설치되어 있지 않습니다. 새 프로젝트로 진행합니다.")
            source = ProjectSource.NEW
        else:
            github_url = input("   GitHub URL 입력: ").strip()
            if not github_url:
                print("   URL이 없습니다. 새 프로젝트로 진행합니다.")
                source = ProjectSource.NEW
            elif not project_name or project_name == "default":
                # URL에서 이름 추출하여 프로젝트명으로 사용 (사용자가 이름을 안 정했을 경우)
                project_name = get_repo_name(github_url)
                print(f"   GitHub에서 이름을 가져왔습니다: {project_name}")

    # 3. 프로젝트 타입 선택
    print("\n🚀 프로젝트 타입 선택 (폴더 구분을 위해 사용됩니다):")
    print("   1. 🌐 Web Application (React, FastAPI, etc.)")
    print("   2. 📱 Mobile App (React Native, Flutter)")
    print("   3. 🖥️ GUI / Desktop Form (PyQt, Tkinter)")
    print("   4. 📁 기타")
    
    type_choice = input("   선택 (1-4): ").strip()
    
    if type_choice == "1":
        project_type = ProjectType.WEB
    elif type_choice == "2":
        project_type = ProjectType.APP
    elif type_choice == "3":
        project_type = ProjectType.GUI
    else:
        project_type = ProjectType.OTHER

    # 워크스페이스 설정
    # 구조: workspace/projects/{web|app|gui}/{project_name}
    project_dir = config.workspace_root / "projects" / project_type.value / project_name
    
    # Git Clone 실행
    if source == ProjectSource.GITHUB and github_url:
        print(f"\n⏳ Cloning from {github_url} to {project_dir}...")
        if clone_repo(github_url, project_dir):
            print("✅ Cloning 완료!")
        else:
            print("❌ Cloning 실패. 빈 디렉토리에서 시작합니다.")

    # 설정 저장
    config.set_workspace_root(project_dir)
    print(f"\n📂 작업 디렉토리 설정됨: {project_dir}")
    print("-" * 60 + "\n")

    # 프롬프트 컨텍스트 준비
    context_message = ""
    if source == ProjectSource.GITHUB:
        context_message = (
            f"나는 현재 '{project_dir}'에 있는 기존 코드베이스를 분석하고 수정하려고 해. "
            f"이 프로젝트는 {project_type.value} 타입이야. "
            "먼저 파일 목록을 확인하고 코드 구조를 파악해줘."
        )
    else:
        context_message = f"나는 새로운 {project_type.value} 프로젝트를 만들고 싶어."

    print("프로젝트 아이디어를 입력하면 완벽한 설계도를 만들어드립니다.")
    print("종료하려면 'exit' 또는 'quit'을 입력하세요.\n")
    print("-" * 60 + "\n")
    
    agent = await InteractiveAgent.create()
    
    # 초기 컨텍스트 주입 (선택 사항: 자동 실행을 위해)
    # 여기서는 사용자에게 첫 입력을 맡길지, 자동으로 "분석해줘"를 날릴지 결정해야 함.
    # 사용자가 아이디어를 입력하게 하되, 시스템적으로 컨텍스트를 주입하는게 자연스러움.
    
    first_turn = True
    
    try:
        while True:
            try:
                if first_turn and source == ProjectSource.GITHUB:
                    prompt_prefix = "[SYSTEM: 기존 코드 분석 모드] "
                    user_input = input(f"💡 아이디어 (또는 '분석해줘' 입력): ").strip()
                    if not user_input:
                         user_input = "현재 폴더의 코드를 분석하고 개선점을 제안해줘."
                else:
                    user_input = input("💡 아이디어: ").strip()
            except EOFError:
                break
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q', '종료']:
                print("\n👋 Manus를 이용해주셔서 감사합니다! 즐거운 코딩하세요!\n")
                break
            
            # 첫 턴에 타입 정보 등을 프롬프트에 몰래 추가
            final_prompt = user_input
            if first_turn:
                final_prompt = f"{context_message}\n\n사용자 요청: {user_input}"
                first_turn = False
            
            print("\n🔄 요청을 처리하고 있습니다...\n")
            
            try:
                result = await agent.run(final_prompt)
                print("\n" + "=" * 60)
                print("✅ Manus 출력")
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
        asyncio.run(run_interactive())
    except KeyboardInterrupt:
        print("\n\n👋 안녕히 가세요!")
        sys.exit(0)


if __name__ == "__main__":
    main()
