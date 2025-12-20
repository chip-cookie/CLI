# CLI 프로젝트 구조

## 📁 전체 디렉토리 구조

```
CLI/
├── 📄 main.py                  # Manus 에이전트 실행 (기본)
├── 📄 run_interactive.py       # 인터랙티브 모드 실행
├── 📄 requirements.txt         # Python 의존성
├── 📄 README.md
│
├── 📁 config/                  # 설정 파일
│   ├── config.toml             # 메인 설정 (API 키 등)
│   └── mcp.json                # MCP 서버 설정
│
└── 📁 app/                     # 메인 애플리케이션
    ├── __init__.py             # 패키지 초기화
    ├── config.py               # 설정 관리
    ├── llm.py                  # LLM 클라이언트
    ├── logger.py               # 로깅
    ├── schema.py               # 데이터 스키마
    ├── exceptions.py           # 예외 처리
    │
    ├── 📁 agent/               # AI 에이전트
    │   ├── base.py                  # BaseAgent
    │   ├── react.py                 # ReActAgent
    │   ├── toolcall.py              # ToolCallAgent
    │   ├── mcp_mixin.py             # MCPMixin
    │   ├── browser_helper.py        # BrowserContextHelper
    │   ├── design_phases.py         # 설계 단계 정의
    │   ├── checkpoint_handler.py    # 체크포인트 핸들러
    │   ├── manus.py                 # Manus 범용 에이전트
    │   ├── interactive_agent.py     # InteractiveAgent
    │   ├── browser.py               # BrowserAgent
    │   ├── mcp.py                   # MCPAgent
    │   └── swe.py                   # SWEAgent
    │
    ├── 📁 tool/                # 도구 모듈
    │   ├── base.py                  # BaseTool
    │   ├── tool_collection.py       # ToolCollection
    │   ├── design_document.py       # 설계 문서 도구
    │   ├── planning.py              # 계획 도구
    │   ├── context_packager.py      # 컨텍스트 패키저
    │   ├── browser_use_tool.py      # 브라우저 도구
    │   ├── python_execute.py        # Python 실행
    │   ├── str_replace_editor.py    # 파일 에디터
    │   └── ...
    │
    ├── 📁 flow/                # 실행 흐름
    │   ├── base.py
    │   ├── planning.py
    │   └── flow_factory.py
    │
    ├── 📁 prompt/              # 프롬프트 템플릿
    │   ├── interactive_prompt.py    # 인터랙티브 에이전트
    │   ├── manus.py                 # Manus 에이전트
    │   └── ...
    │
    ├── 📁 mcp/                 # MCP 서버
    ├── 📁 sandbox/             # 샌드박스
    └── 📁 utils/               # 유틸리티
```

## 🏗️ 계층 구조

### Agent 계층
```
BaseAgent (추상)
    └── ReActAgent (think/act)
            └── ToolCallAgent (도구 호출)
                    ├── Manus (범용)
                    ├── InteractiveAgent (인터랙티브)
                    ├── BrowserAgent
                    └── MCPAgent
```

### Mixin 구조
```
MCPMixin ─────┬──→ Manus
              └──→ InteractiveAgent

BrowserContextHelper ─┬──→ Manus
                      ├──→ InteractiveAgent
                      └──→ BrowserAgent
```

## ⚙️ 실행 방법

```bash
# 인터랙티브 모드 (권장)
python run_interactive.py

# 범용 모드
python main.py --prompt "작업 내용" --project "프로젝트명"
```
