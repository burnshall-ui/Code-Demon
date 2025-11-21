"""
Command Execution Tool

Execute shell commands safely
"""

import asyncio
import shlex
from pathlib import Path
from ..registry import Tool, ToolMetadata, ToolCategory, ToolParameter


class ExecuteCommandTool(Tool):
    """Tool to execute shell commands"""

    def _define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="execute_command",
            description="Execute a shell command and return its output. Use with caution!",
            category=ToolCategory.EXECUTION,
            parameters=[
                ToolParameter(
                    name="command",
                    type="string",
                    description="Shell command to execute",
                    required=True,
                ),
                ToolParameter(
                    name="cwd",
                    type="string",
                    description="Working directory for the command (defaults to current directory)",
                    required=False,
                    default=None,
                ),
                ToolParameter(
                    name="timeout",
                    type="number",
                    description="Timeout in seconds (default: 30)",
                    required=False,
                    default=30,
                ),
            ],
            requires_approval=True,  # Command execution is dangerous
            dangerous=True,
            timeout=60,
        )

    async def execute(
        self, command: str, cwd: str | None = None, timeout: int = 30
    ) -> str:
        """Execute shell command"""
        try:
            # Validate command
            if not command.strip():
                return "Error: Empty command"

            # Parse working directory
            work_dir = None
            if cwd:
                work_dir = Path(cwd).expanduser().resolve()
                if not work_dir.exists():
                    return f"Error: Directory '{cwd}' does not exist"
                if not work_dir.is_dir():
                    return f"Error: '{cwd}' is not a directory"

            # Execute command
            try:
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(work_dir) if work_dir else None,
                )

                # Wait for completion with timeout
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )

                # Decode output
                stdout_text = stdout.decode("utf-8", errors="ignore")
                stderr_text = stderr.decode("utf-8", errors="ignore")

                # Build result
                output = []
                output.append(f"🔧 Command: {command}")
                output.append(f"📍 Exit code: {process.returncode}")
                output.append("")

                if stdout_text:
                    output.append("📤 Output:")
                    output.append(stdout_text)

                if stderr_text:
                    output.append("")
                    output.append("⚠ Errors:")
                    output.append(stderr_text)

                if not stdout_text and not stderr_text:
                    output.append("(No output)")

                return "\n".join(output)

            except asyncio.TimeoutError:
                return f"Error: Command timed out after {timeout} seconds"

        except Exception as e:
            return f"Error executing command: {str(e)}"


class RunPythonTool(Tool):
    """Tool to run Python code"""

    def _define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="run_python",
            description="Execute Python code and return the output.",
            category=ToolCategory.EXECUTION,
            parameters=[
                ToolParameter(
                    name="code",
                    type="string",
                    description="Python code to execute",
                    required=True,
                ),
                ToolParameter(
                    name="timeout",
                    type="number",
                    description="Timeout in seconds (default: 30)",
                    required=False,
                    default=30,
                ),
            ],
            requires_approval=True,  # Code execution is dangerous
            dangerous=True,
            timeout=60,
        )

    async def execute(self, code: str, timeout: int = 30) -> str:
        """Run Python code"""
        try:
            # Validate code
            if not code.strip():
                return "Error: Empty code"

            # Create temp file
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as f:
                f.write(code)
                temp_file = f.name

            try:
                # Execute Python script
                process = await asyncio.create_subprocess_exec(
                    "python3",
                    temp_file,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )

                stdout_text = stdout.decode("utf-8", errors="ignore")
                stderr_text = stderr.decode("utf-8", errors="ignore")

                # Build result
                output = []
                output.append("🐍 Python Execution")
                output.append(f"📍 Exit code: {process.returncode}")
                output.append("")

                if stdout_text:
                    output.append("📤 Output:")
                    output.append(stdout_text)

                if stderr_text:
                    output.append("")
                    output.append("⚠ Errors:")
                    output.append(stderr_text)

                if not stdout_text and not stderr_text:
                    output.append("(No output)")

                return "\n".join(output)

            finally:
                # Clean up temp file
                os.unlink(temp_file)

        except asyncio.TimeoutError:
            return f"Error: Code execution timed out after {timeout} seconds"
        except Exception as e:
            return f"Error running Python code: {str(e)}"


class RunTestsTool(Tool):
    """Tool to run tests"""

    def _define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="run_tests",
            description="Run tests in a project (supports pytest, unittest, npm test, etc.)",
            category=ToolCategory.EXECUTION,
            parameters=[
                ToolParameter(
                    name="path",
                    type="string",
                    description="Path to project directory",
                    required=False,
                    default=".",
                ),
                ToolParameter(
                    name="test_type",
                    type="string",
                    description="Test framework: pytest, unittest, npm, cargo, go",
                    required=False,
                    default="pytest",
                    enum=["pytest", "unittest", "npm", "cargo", "go"],
                ),
                ToolParameter(
                    name="pattern",
                    type="string",
                    description="Test file pattern or specific test",
                    required=False,
                    default=None,
                ),
            ],
            requires_approval=False,
            dangerous=False,
            timeout=120,
        )

    async def execute(
        self, path: str = ".", test_type: str = "pytest", pattern: str | None = None
    ) -> str:
        """Run tests"""
        try:
            work_dir = Path(path).expanduser().resolve()
            if not work_dir.exists():
                return f"Error: Directory '{path}' does not exist"

            # Build test command based on type
            commands = {
                "pytest": ["pytest", "-v"] + ([pattern] if pattern else []),
                "unittest": ["python", "-m", "unittest", "discover"]
                + (["-p", pattern] if pattern else []),
                "npm": ["npm", "test"] + ([pattern] if pattern else []),
                "cargo": ["cargo", "test"] + ([pattern] if pattern else []),
                "go": ["go", "test", "./..."] + (["-run", pattern] if pattern else []),
            }

            if test_type not in commands:
                return f"Error: Unknown test type '{test_type}'"

            cmd_args = commands[test_type]

            # Run tests
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(work_dir),
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)

            stdout_text = stdout.decode("utf-8", errors="ignore")
            stderr_text = stderr.decode("utf-8", errors="ignore")

            # Build output
            output = []
            output.append(f"🧪 Test Results ({test_type})")
            output.append(f"📁 Directory: {path}")
            output.append(f"📍 Exit code: {process.returncode}")
            output.append("")

            if stdout_text:
                output.append(stdout_text)

            if stderr_text:
                output.append("")
                output.append("⚠ Errors:")
                output.append(stderr_text)

            # Truncate if too long
            full_output = "\n".join(output)
            if len(full_output) > 5000:
                full_output = (
                    full_output[:5000]
                    + "\n\n... (output truncated, run tests manually for full output)"
                )

            return full_output

        except asyncio.TimeoutError:
            return "Error: Tests timed out after 120 seconds"
        except Exception as e:
            return f"Error running tests: {str(e)}"

