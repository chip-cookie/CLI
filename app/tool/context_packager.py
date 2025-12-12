"""
ContextPackager Tool
====================
A tool for packing generated project files into AI-optimized context blocks.
This enables seamless transfer of code/architecture to web-based AI builders.
"""

from typing import Literal, Optional, List
from pathlib import Path
from app.tool.base import BaseTool, ToolResult


_CONTEXT_PACKAGER_DESCRIPTION = """
A tool that packages project files and code into a structured, AI-optimized format.
This output can be directly copied into web-based AI builders (v0, Bolt.new, ChatGPT, etc.)
for seamless project handoff. The tool supports multiple target AI formats.
"""


class ContextPackager(BaseTool):
    """
    Packages project files into AI-ready context blocks optimized for specific LLM targets.
    """

    name: str = "context_packager"
    description: str = _CONTEXT_PACKAGER_DESCRIPTION
    parameters: dict = {
        "type": "object",
        "properties": {
            "command": {
                "description": "The command to execute. Available: pack, list_files, preview",
                "enum": ["pack", "list_files", "preview"],
                "type": "string",
            },
            "target_ai": {
                "description": "Target AI platform for optimization. Default: generic",
                "enum": ["generic", "v0", "bolt", "chatgpt", "claude", "gemini"],
                "type": "string",
            },
            "project_path": {
                "description": "Path to the project directory to package",
                "type": "string",
            },
            "file_paths": {
                "description": "Specific file paths to include in the package",
                "type": "array",
                "items": {"type": "string"},
            },
            "include_tree": {
                "description": "Whether to include file tree structure in the output",
                "type": "boolean",
            },
            "output_format": {
                "description": "Output format: markdown, xml, or json",
                "enum": ["markdown", "xml", "json"],
                "type": "string",
            },
        },
        "required": ["command"],
        "additionalProperties": False,
    }

    async def execute(
        self,
        *,
        command: Literal["pack", "list_files", "preview"],
        target_ai: str = "generic",
        project_path: Optional[str] = None,
        file_paths: Optional[List[str]] = None,
        include_tree: bool = True,
        output_format: str = "markdown",
        **kwargs,
    ) -> ToolResult:
        """Execute the context packager with given parameters."""
        
        if command == "pack":
            return await self._pack_context(
                target_ai, project_path, file_paths, include_tree, output_format
            )
        elif command == "list_files":
            return await self._list_files(project_path)
        elif command == "preview":
            return await self._preview(target_ai, project_path, file_paths)
        else:
            return ToolResult(error=f"Unknown command: {command}")

    async def _pack_context(
        self,
        target_ai: str,
        project_path: Optional[str],
        file_paths: Optional[List[str]],
        include_tree: bool,
        output_format: str,
    ) -> ToolResult:
        """Pack files into an AI-optimized context block."""
        
        files_to_pack = []
        
        if file_paths:
            files_to_pack = [Path(p) for p in file_paths if Path(p).exists()]
        elif project_path:
            project = Path(project_path)
            if project.is_dir():
                # Collect relevant files (skip hidden, node_modules, etc.)
                for ext in ["*.py", "*.js", "*.ts", "*.tsx", "*.jsx", "*.html", "*.css", "*.json", "*.md"]:
                    files_to_pack.extend(project.rglob(ext))
                files_to_pack = [f for f in files_to_pack if not any(
                    part.startswith('.') or part in ['node_modules', '__pycache__', 'venv', '.git']
                    for part in f.parts
                )]
        
        if not files_to_pack:
            return ToolResult(error="No files found to pack. Provide valid project_path or file_paths.")
        
        # Build the context package
        output = self._build_header(target_ai)
        
        if include_tree:
            output += self._build_file_tree(files_to_pack)
        
        output += self._build_file_contents(files_to_pack, output_format)
        output += self._build_footer(target_ai)
        
        return ToolResult(output=output)

    async def _list_files(self, project_path: Optional[str]) -> ToolResult:
        """List all packagable files in a project."""
        if not project_path:
            return ToolResult(error="project_path is required for list_files command")
        
        project = Path(project_path)
        if not project.is_dir():
            return ToolResult(error=f"Path is not a directory: {project_path}")
        
        files = []
        for ext in ["*.py", "*.js", "*.ts", "*.tsx", "*.jsx", "*.html", "*.css", "*.json"]:
            files.extend(project.rglob(ext))
        
        files = [f for f in files if not any(
            part.startswith('.') or part in ['node_modules', '__pycache__', 'venv']
            for part in f.parts
        )]
        
        output = f"Found {len(files)} packagable files:\n\n"
        for f in sorted(files)[:50]:  # Limit to 50 files
            output += f"- {f.relative_to(project)}\n"
        
        if len(files) > 50:
            output += f"\n... and {len(files) - 50} more files"
        
        return ToolResult(output=output)

    async def _preview(
        self,
        target_ai: str,
        project_path: Optional[str],
        file_paths: Optional[List[str]],
    ) -> ToolResult:
        """Preview the package structure without full content."""
        return ToolResult(output=f"Preview for {target_ai}:\n{self._build_header(target_ai)}\n[File contents would appear here]\n{self._build_footer(target_ai)}")

    def _build_header(self, target_ai: str) -> str:
        """Build target-specific header."""
        headers = {
            "generic": "# Project Context\n\nBelow is the complete context of the project:\n\n",
            "v0": "# v0 Project Handoff\n\nThis is a complete project structure for v0.dev. Implement this exactly:\n\n",
            "bolt": "# Bolt.new Project Import\n\nStackBlitz-optimized project structure:\n\n",
            "chatgpt": "# Complete Project Context\n\nPlease analyze and understand this project structure completely:\n\n",
            "claude": "<project_context>\n\n",
            "gemini": "## Project Overview\n\nFull project context for implementation:\n\n",
        }
        return headers.get(target_ai, headers["generic"])

    def _build_file_tree(self, files: List[Path]) -> str:
        """Build a visual file tree."""
        if not files:
            return ""
        
        output = "## File Structure\n\n```\n"
        
        # Get unique directories and files
        root = files[0].parent if files else Path(".")
        try:
            root = Path(*[p for p in files[0].parts[:1]])  # Get common root
        except:
            pass
        
        for f in sorted(set(files))[:30]:
            try:
                rel_path = str(f.name)
                output += f"📄 {rel_path}\n"
            except:
                output += f"📄 {f.name}\n"
        
        output += "```\n\n"
        return output

    def _build_file_contents(self, files: List[Path], output_format: str) -> str:
        """Build formatted file contents section."""
        output = "## File Contents\n\n"
        
        for f in sorted(files)[:20]:  # Limit to 20 files to avoid context overflow
            if not f.exists():
                continue
            
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                if len(content) > 5000:  # Truncate very long files
                    content = content[:5000] + "\n... [truncated]"
                
                ext = f.suffix.lstrip('.')
                lang = self._get_language(ext)
                
                if output_format == "xml":
                    output += f"<file path=\"{f.name}\">\n{content}\n</file>\n\n"
                elif output_format == "json":
                    import json
                    output += f"/* {f.name} */\n{content}\n\n"
                else:  # markdown
                    output += f"### `{f.name}`\n\n```{lang}\n{content}\n```\n\n"
            except Exception as e:
                output += f"### `{f.name}`\n\nError reading file: {e}\n\n"
        
        return output

    def _build_footer(self, target_ai: str) -> str:
        """Build target-specific footer with instructions."""
        footers = {
            "generic": "\n---\n\nPlease implement this project structure.\n",
            "v0": "\n---\n\nGenerate a modern, responsive UI based on this context.\n",
            "bolt": "\n---\n\nCreate a working StackBlitz project from this context.\n",
            "chatgpt": "\n---\n\nNow, based on this complete context, please proceed with the next steps.\n",
            "claude": "\n</project_context>\n\nPlease analyze and work with this project.\n",
            "gemini": "\n---\n\n위 프로젝트를 기반으로 작업을 진행해주세요.\n",
        }
        return footers.get(target_ai, footers["generic"])

    def _get_language(self, ext: str) -> str:
        """Map file extension to language for syntax highlighting."""
        mapping = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "tsx": "tsx",
            "jsx": "jsx",
            "html": "html",
            "css": "css",
            "json": "json",
            "md": "markdown",
            "yaml": "yaml",
            "yml": "yaml",
            "sql": "sql",
            "sh": "bash",
            "bash": "bash",
        }
        return mapping.get(ext, ext)
