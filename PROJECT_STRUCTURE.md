# CLI 프로젝트 구조

## 📁 전체 디렉토리 구조

```
CLI/
├── 📄 main.py              # Manus 에이전트 실행 진입점 (기본)
├── 📄 run_bloom.py         # 인터랙티브 모드 실행 진입점
├── 📄 requirements.txt     # Python 의존성
├── 📄 README.md
│
├── 📁 config/              # 설정 파일
│   ├── config.toml         # 메인 설정 (API 키 등)
│   └── mcp.json            # MCP 서버 설정
│
└── 📁 app/                 # 메인 애플리케이션
    ├── __init__.py         # 패키지 초기화 & 핵심 export
    ├── config.py           # 설정 관리 클래스
    ├── llm.py              # LLM 클라이언트 (OpenAI, Azure, Bedrock)
    ├── logger.py           # 로깅 유틸리티
    ├── schema.py           # 데이터 스키마 (Message, Memory 등)
    ├── exceptions.py       # 커스텀 예외
    ├── bedrock.py          # AWS Bedrock 클라이언트
    │
    ├── 📁 agent/           # AI 에이전트
    │   ├── base.py              # BaseAgent (추상 기본 클래스)
    │   ├── react.py             # ReActAgent (ReAct 패턴)
    │   ├── toolcall.py          # ToolCallAgent (도구 호출)
    │   ├── mcp_mixin.py         # MCPMixin (MCP 서버 연결)
    │   ├── browser_helper.py    # BrowserContextHelper
    │   ├── design_phases.py     # 설계 단계 정의
    │   ├── checkpoint_handler.py # 체크포인트 핸들러
    │   ├── manus.py             # Manus 범용 에이전트
    │   ├── bloom_agent.py       # 인터랙티브 설계 에이전트
    │   ├── browser.py           # BrowserAgent
    │   ├── mcp.py               # MCPAgent
    │   ├── swe.py               # SWEAgent
    │   ├── data_analysis.py     # DataAnalysisAgent
    │   └── sandbox_agent.py     # SandboxAgent
    │
    ├── 📁 tool/            # 도구 모듈
    │   ├── base.py              # BaseTool, ToolResult
    │   ├── tool_collection.py   # ToolCollection
    │   ├── design_document.py   # 설계 문서 도구
    │   ├── planning.py          # 계획 도구
    │   ├── context_packager.py  # 컨텍스트 패키저
    │   ├── browser_use_tool.py  # 브라우저 도구
    │   ├── python_execute.py    # Python 실행
    │   ├── str_replace_editor.py # 파일 에디터
    │   ├── web_search.py        # 웹 검색
    │   ├── ask_human.py         # 사용자 입력
    │   ├── terminate.py         # 종료
    │   ├── 📁 search/           # 검색 엔진 구현
    │   ├── 📁 sandbox/          # 샌드박스 도구
    │   └── 📁 chart_visualization/ # 차트 시각화
    │
    ├── 📁 flow/            # 실행 흐름
    │   ├── base.py              # BaseFlow
    │   ├── planning.py          # PlanningFlow
    │   └── flow_factory.py      # FlowFactory
    │
    ├── 📁 prompt/          # 프롬프트 템플릿
    │   ├── bloom_prompt.py      # 설계 에이전트 프롬프트
    │   ├── manus.py             # Manus 프롬프트
    │   ├── browser.py           # Browser 프롬프트
    │   └── ...
    │
    ├── 📁 mcp/             # MCP 서버
    │   └── server.py
    │
    ├── 📁 sandbox/         # 샌드박스 환경
    │   ├── client.py
    │   └── 📁 core/
    │
    ├── 📁 daytona/         # Daytona 통합
    │   ├── sandbox.py
    │   └── tool_base.py
    │
    └── 📁 utils/           # 유틸리티
        └── files_utils.py       # 파일 처리 유틸리티
```

## 🏗️ 계층 구조

### Agent 계층
```
BaseAgent (추상)
    └── ReActAgent (추상, think/act 패턴)
            └── ToolCallAgent (도구 호출 기능)
                    ├── Manus (범용 에이전트)
                    ├── JeongongBloom (인터랙티브 에이전트)
                    ├── BrowserAgent (브라우저)
                    └── MCPAgent (MCP)
```

### Mixin 구조
```
MCPMixin ─────┬──→ Manus
              └──→ JeongongBloom

BrowserContextHelper ─┬──→ Manus
                      ├──→ JeongongBloom
                      └──→ BrowserAgent
```

## 🔧 모듈별 책임

| 모듈 | 책임 |
|------|------|
| `agent/` | AI 에이전트 정의 및 실행 로직 |
| `tool/` | 에이전트가 사용하는 도구들 |
| `flow/` | 다중 에이전트 실행 흐름 관리 |
| `prompt/` | 시스템/사용자 프롬프트 템플릿 |
| `mcp/` | MCP 프로토콜 서버 |
| `sandbox/` | 안전한 코드 실행 환경 |
| `utils/` | 공통 유틸리티 함수 |

## ⚙️ 실행 방법

```bash
# Manus 에이전트 (범용)
python main.py --prompt "작업 내용"

# 인터랙티브 모드 (Vibe Coding)
python run_bloom.py
```
