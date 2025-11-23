"""
Output sanitization and truncation to prevent overflow attacks.

This module provides guardrails against malicious or accidental output
that could corrupt files, overflow context, or break agent operation.
"""

from __future__ import annotations


MAX_OUTPUT_LENGTH = 500  # Characters for terminal output
MAX_DIAGNOSTIC_LENGTH = 2000  # Characters for diagnostic messages
MAX_FILE_CONTENT_LENGTH = 10000  # Characters for file content


class OutputSanitizer:
    """Sanitizes and truncates potentially dangerous output."""

    @staticmethod
    def sanitize_terminal_output(output: str, max_length: int = MAX_OUTPUT_LENGTH) -> str:
        """
        Truncate and sanitize terminal command output.

        Args:
            output: Raw terminal output
            max_length: Maximum allowed length

        Returns:
            Sanitized and possibly truncated output
        """
        if not output:
            return ""

        # Check for massive ASCII art or repetitive patterns
        if OutputSanitizer._is_ascii_art_spam(output):
            return "[OUTPUT BLOCKED: Detected ASCII art or repetitive pattern spam]"

        # Truncate if too long
        if len(output) > max_length:
            truncated = output[:max_length]
            remaining = len(output) - max_length
            return f"{truncated}\n... [TRUNCATED: {remaining} more characters]"

        return output

    @staticmethod
    def sanitize_diagnostic(message: str, max_length: int = MAX_DIAGNOSTIC_LENGTH) -> str:
        """
        Sanitize diagnostic messages.

        Args:
            message: Diagnostic message
            max_length: Maximum allowed length

        Returns:
            Sanitized message
        """
        if not message:
            return ""

        if len(message) > max_length:
            return message[:max_length] + f"... [TRUNCATED: {len(message) - max_length} more chars]"

        return message

    @staticmethod
    def sanitize_file_content(content: str, max_length: int = MAX_FILE_CONTENT_LENGTH) -> str:
        """
        Sanitize file content before processing.

        Args:
            content: File content
            max_length: Maximum allowed length

        Returns:
            Sanitized content or error message
        """
        if not content:
            return ""

        if len(content) > max_length:
            return (
                f"[FILE TOO LARGE: {len(content)} characters, "
                f"exceeds {max_length} limit. First {max_length} chars shown]\n"
                + content[:max_length]
            )

        return content

    @staticmethod
    def _is_ascii_art_spam(text: str) -> bool:
        """
        Detect if text contains ASCII art spam or repetitive patterns.

        Args:
            text: Text to check

        Returns:
            True if likely spam
        """
        if len(text) < 500:
            return False

        # Check for excessive repeating patterns
        lines = text.split("\n")
        if len(lines) > 100:
            # Sample every 10th line
            sample_lines = lines[::10]
            if len(set(sample_lines)) < len(sample_lines) * 0.1:
                # Less than 10% unique lines in sample = likely spam
                return True

        # Check for ASCII art characters
        ascii_art_chars = set("*.-|/\\#")
        ascii_art_ratio = sum(1 for c in text if c in ascii_art_chars) / len(text)
        if ascii_art_ratio > 0.3:  # More than 30% ASCII art chars
            return True

        # Check for very long lines (banner spam)
        max_line_length = max(len(line) for line in lines) if lines else 0
        if max_line_length > 200:
            return True

        return False

    @staticmethod
    def create_digest(text: str) -> str:
        """
        Create a digest of large text for confirmation prompts.

        Args:
            text: Full text

        Returns:
            Digest with length and sample
        """
        length = len(text)
        line_count = text.count("\n") + 1

        if length <= 200:
            return text

        # Get first and last 100 chars
        first_part = text[:100]
        last_part = text[-100:]

        return (
            f"[OUTPUT DIGEST: {length} characters, {line_count} lines]\n"
            f"First 100 chars: {first_part}\n"
            f"...\n"
            f"Last 100 chars: {last_part}"
        )


def wrap_terminal_output(raw_output: str) -> dict[str, str]:
    """
    Wrap terminal output in structured format.

    Args:
        raw_output: Raw terminal output

    Returns:
        Dict with 'raw', 'sanitized', and 'digest' keys
    """
    sanitizer = OutputSanitizer()

    return {
        "raw": raw_output,
        "sanitized": sanitizer.sanitize_terminal_output(raw_output),
        "digest": sanitizer.create_digest(raw_output),
        "length": str(len(raw_output)),
    }


def should_reject_output(text: str, max_length: int = 50000) -> tuple[bool, str]:
    """
    Check if output should be rejected entirely.

    Args:
        text: Output to check
        max_length: Absolute maximum length

    Returns:
        (should_reject, reason)
    """
    if len(text) > max_length:
        return True, f"Output too large: {len(text)} characters exceeds {max_length} limit"

    if OutputSanitizer._is_ascii_art_spam(text):
        return True, "Detected ASCII art or repetitive pattern spam"

    return False, ""
