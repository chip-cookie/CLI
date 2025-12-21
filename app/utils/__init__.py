"""
Utils 모듈
==========
유틸리티 함수들과 상수들을 포함합니다.

포함 내용:
- files_utils: 파일 경로 처리 및 필터링 유틸리티
- git_utils: Git 저장소 복제 및 확인 유틸리티
"""

from app.utils.files_utils import (
    EXCLUDED_DIRS,
    EXCLUDED_EXT,
    EXCLUDED_FILES,
    clean_path,
    should_exclude_file,
)
from app.utils.git_utils import (
    clone_repo,
    get_repo_name,
    is_git_installed,
)


__all__ = [
    # Files
    "EXCLUDED_DIRS",
    "EXCLUDED_EXT",
    "EXCLUDED_FILES",
    "clean_path",
    "should_exclude_file",
    # Git
    "clone_repo",
    "get_repo_name",
    "is_git_installed",
]
