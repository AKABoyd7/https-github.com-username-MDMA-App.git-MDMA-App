"""
Tests for safety guards and validation.
"""

import pytest
from pathlib import Path, PureWindowsPath
from mcp_server.safety import (
    validate_powershell_command,
    validate_python_code,
    validate_file_path,
    validate_file_size,
    is_safe_filename
)


class TestPowerShellValidation:
    """Test PowerShell command validation."""

    def test_allow_safe_command(self):
        """Test that safe commands are allowed."""
        valid, msg = validate_powershell_command("Get-ChildItem *.txt")
        assert valid is True

    def test_block_dangerous_command(self):
        """Test that dangerous commands are blocked."""
        valid, msg = validate_powershell_command("Remove-Item test.txt")
        assert valid is False
        assert "Blocked command" in msg

    def test_block_invoke_webrequest(self):
        """Test blocking of Invoke-WebRequest."""
        valid, msg = validate_powershell_command("Invoke-WebRequest http://example.com")
        assert valid is False

    def test_block_command_chaining(self):
        """Test blocking of command chaining attempts."""
        valid, msg = validate_powershell_command("Get-Process; $x = Get-Content")
        assert valid is False
        assert "dangerous pattern" in msg.lower()

    def test_require_whitelisted_cmdlet(self):
        """Test that at least one whitelisted cmdlet is required."""
        valid, msg = validate_powershell_command("Write-Something Custom")
        assert valid is False
        assert "whitelisted" in msg.lower()


class TestPythonValidation:
    """Test Python code validation."""

    def test_allow_safe_code(self):
        """Test that safe Python code is allowed."""
        code = """
x = 5
y = 10
print(x + y)
        """
        valid, msg = validate_python_code(code)
        assert valid is True

    def test_block_subprocess_import(self):
        """Test blocking of subprocess import."""
        code = "import subprocess"
        valid, msg = validate_python_code(code)
        assert valid is False
        assert "subprocess" in msg

    def test_block_os_system(self):
        """Test blocking of os.system import."""
        code = "from os.system import *"
        valid, msg = validate_python_code(code)
        assert valid is False

    def test_block_exec(self):
        """Test blocking of exec() calls."""
        code = "exec('print(1)')"
        valid, msg = validate_python_code(code)
        assert valid is False
        assert "exec" in msg

    def test_block_eval(self):
        """Test blocking of eval() calls."""
        code = "result = eval('2 + 2')"
        valid, msg = validate_python_code(code)
        assert valid is False

    def test_block_open(self):
        """Test blocking of open() calls."""
        code = "with open('file.txt') as f: pass"
        valid, msg = validate_python_code(code)
        assert valid is False
        assert "open" in msg.lower()


class TestFilePathValidation:
    """Test file path validation."""

    def test_allow_path_within_project(self):
        """Test allowing paths within project root."""
        valid, msg, path = validate_file_path("G:\\AlphaEdge_AINV\\test.txt")
        assert valid is True

    def test_block_path_outside_project(self):
        """Test blocking paths outside project root."""
        valid, msg, path = validate_file_path("C:\\Windows\\system32\\test.txt")
        assert valid is False
        assert "within" in msg

    def test_block_path_traversal(self):
        """Test blocking path traversal attempts."""
        valid, msg, path = validate_file_path("G:\\AlphaEdge_AINV\\..\\..\\test.txt")
        assert valid is False
        assert "traversal" in msg

    def test_block_invalid_extension(self):
        """Test blocking files with invalid extensions."""
        valid, msg, path = validate_file_path("G:\\AlphaEdge_AINV\\test.exe")
        assert valid is False
        assert "extension" in msg


class TestFileSizeValidation:
    """Test file size validation."""

    def test_allow_small_file(self):
        """Test allowing files under size limit."""
        valid, msg = validate_file_size(1024 * 1024)  # 1MB
        assert valid is True

    def test_block_large_file(self):
        """Test blocking files over size limit."""
        valid, msg = validate_file_size(20 * 1024 * 1024)  # 20MB
        assert valid is False
        assert "exceeds limit" in msg


class TestFilenameValidation:
    """Test filename validation."""

    def test_allow_safe_filename(self):
        """Test allowing safe filenames."""
        valid, msg = is_safe_filename("test_file.txt")
        assert valid is True

    def test_block_path_separator_in_filename(self):
        """Test blocking path separators in filename."""
        valid, msg = is_safe_filename("path/to/file.txt")
        assert valid is False

    def test_block_dangerous_characters(self):
        """Test blocking dangerous characters."""
        dangerous = ['<', '>', ':', '"', '|', '?', '*']
        for char in dangerous:
            valid, msg = is_safe_filename(f"test{char}file.txt")
            assert valid is False, f"Should block character: {char}"

    def test_block_reserved_windows_names(self):
        """Test blocking reserved Windows names."""
        reserved = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'LPT1']
        for name in reserved:
            valid, msg = is_safe_filename(f"{name}.txt")
            assert valid is False, f"Should block reserved name: {name}"

    def test_allow_normal_reserved_substring(self):
        """Test allowing filenames that contain but aren't reserved names."""
        valid, msg = is_safe_filename("console.txt")
        assert valid is True


class TestSecurityScenarios:
    """Test complete security scenarios."""

    def test_powershell_injection_attempt(self):
        """Test blocking PowerShell injection."""
        attacks = [
            "Get-Process; Remove-Item *.*",
            "Get-ChildItem | ForEach-Object {Remove-Item $_}",
            "Get-Content file.txt | Out-File -Append attack.txt"
        ]

        for attack in attacks:
            valid, msg = validate_powershell_command(attack)
            assert valid is False, f"Should block: {attack}"

    def test_python_escape_attempts(self):
        """Test blocking Python sandbox escape attempts."""
        escapes = [
            "__import__('os').system('calc')",
            "exec(__import__('base64').b64decode('...'))",
            "[x for x in ().__class__.__bases__[0].__subclasses__()]"
        ]

        for escape in escapes:
            valid, msg = validate_python_code(escape)
            assert valid is False, f"Should block: {escape}"

    def test_path_traversal_variations(self):
        """Test various path traversal attempts."""
        attempts = [
            "G:\\AlphaEdge_AINV\\..\\..\\Windows\\system32\\calc.exe",
            "G:\\AlphaEdge_AINV\\workspace\\..\\..\\..\\secret.txt",
            "..\\..\\..\\etc\\passwd"
        ]

        for attempt in attempts:
            valid, msg, path = validate_file_path(attempt)
            assert valid is False, f"Should block: {attempt}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
