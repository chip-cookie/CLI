# 🛠️ Manus Interactive Agent - Update Log & Patch Notes

이 문서는 최근 업데이트를 통해 추가된 기능, 리팩토링 사항, 그리고 Python 3.9 호환성 패치 내역을 상세히 기술합니다.

## 🚀 주요 신규 기능 (New Features)

### 1. **Clone & Evolve (GitHub Import)**
   - **기능**: 기존 GitHub 레포지토리를 가져와서 분석하고, 새로운 기능을 추가하거나 수정할 수 있는 모드입니다.
   - **작동 방식**: 
     - CLI 시작 시 `2. GitHub 레포지토리 가져오기`를 선택하면 URL을 입력받아 자동으로 Clone 합니다.
     - Clone된 코드를 분석하여 에이전트에게 "기존 코드 분석 모드" 컨텍스트를 주입합니다.
   - **관련 파일**: `run_interactive.py`, `app/utils/git_utils.py`

### 2. **Project Type Wizard (프로젝트 타입 선택)**
   - **기능**: 프로젝트의 성격(Web, App, GUI 등)을 정의하여 에이전트가 더 정확한 설계를 하도록 돕습니다.
   - **카테고리**:
     - `Web Application`: React, FastAPI 등
     - `Mobile App`: React Native, Flutter 등
     - `GUI / Desktop`: PyQt, Tkinter 등
     - `Other`: 기타
   - **효과**: 선택한 타입에 따라 프로젝트가 `workspace/projects/{type}/{name}` 폴더에 체계적으로 저장됩니다.

### 3. **Interactive CLI (대화형 실행 환경)**
   - **기능**: 복잡한 인자 없이 `python run_interactive.py` 실행만으로 프로젝트 설정부터 에이전트 실행까지 위자드(Wizard) 형태로 진행됩니다.
   - **호환성**: Windows 콘솔(cmd, powershell)에서의 깨짐 방지를 위해 이모지 대신 ASCII 문자를 사용하도록 개선되었습니다.

### 4. **Python 3.11 Complete Migration** (Latest)
   - **업그레이드**: Python 3.9의 호환성 한계를 극복하기 위해 **Python 3.11 기반 가상환경(.venv)**으로 완전히 전환했습니다.
   - **기능 복구**: 제외되었던 `browser-use` 및 `mcp` 라이브러리가 정상 설치되어 모든 기능을 100% 활용할 수 있습니다.
   - **편의성**: `run.bat` 스크립트를 통해 가상환경 활성화 + 실행을 원클릭으로 처리합니다.


---

## 🔧 호환성 및 안정성 패치 (Compatibility Fixes)

### 1. **Python 3.9 지원 (Legacy Support)**
   - **문제**: Python 3.9에서 최신 Python 문법(`type | None` 등) 사용 시 `TypeError` 발생.
   - **해결**: 모든 주요 파일에 `from __future__ import annotations`를 추가하여 하위 버전 호환성 확보.
   - **수정된 파일**:
     - `app/llm.py`
     - `app/tool/bash.py`
     - `app/tool/create_chat_completion.py`
     - `app/tool/str_replace_editor.py`
     - `app/tool/browser_use_tool.py`

### 2. **선택적 의존성 처리 (Optional Dependencies)**
   - **문제**: `mcp`, `browser-use` 등 일부 최신 라이브러리가 Python 3.9 환경에서 설치되지 않는 문제.
   - **해결**: 해당 라이브러리가 없어도 에이전트가 실행되도록 `try-import` 블록과 Mocking 클래스를 구현.
   - **패치 내용**:
     - `app/tool/mcp.py`: `mcp` 라이브러리 부재 시 기능 비활성화 (에러 없이 실행).
     - `app/tool/browser_use_tool.py`: 브라우저 기능 부재 시 에이전트 실행은 가능하도록 수정.

### 3. **Windows 텍스트 인코딩 문제 해결**
   - **문제**: Windows 기본 콘솔(cp949)에서 유니코드 이모지(🤖, 📦 등) 출력 시 `UnicodeEncodeError` 발생.
   - **해결**: CLI 출력 메시지를 이모지 없는 ASCII 스타일(`(*)`, `[Warning]` 등)로 전면 교체.

---

## 📂 파일 구조 변경 (Refactoring)

- **`workspace/projects/` 계층 구조 도입**:
  기존의 평면적인 프로젝트 저장 방식을 개선하여 타입별로 정리됩니다.
  ```text
  workspace/projects/
  ├── web/
  │   └── my-react-app/
  ├── app/
  │   └── my-flutter-app/
  └── gui/
      └── my-pyqt-tool/
  ```
- **`app/utils/git_utils.py`**: Git 작업을 전담하는 유틸리티 모듈 분리.

---

## 📝 실행 방법

이제 의존성 문제 없이 바로 실행 가능합니다:

```powershell
# Interactive 모드 실행 (추천)
python run_interactive.py
```

만약 모듈 부족 에러가 발생하면 다음 명령어로 필요한 패키지를 설치하세요:
```powershell
pip install pydantic loguru openai tomli tenacity six boto3 numpy html2text beautifulsoup4 requests docker baidusearch googlesearch-python duckduckgo_search
```
