from tdd_agents.sanitize import strip_code_fences, sanitize_snippet


def test_strip_code_fences_python_lang():
    src = """```python\nprint('hi')\n```"""
    assert strip_code_fences(src) == "print('hi')\n"


def test_strip_code_fences_no_fence():
    src = "print('hi')\n"
    assert strip_code_fences(src) == src


def test_sanitize_snippet_adds_trailing_newline():
    src = "```\nprint('hi')\n```"
    assert sanitize_snippet(src).endswith("\n")
    assert "```" not in sanitize_snippet(src)


def test_sanitize_multiple_fenced_blocks():
    src = "```python\nprint('a')\n```\nnoise\n```python\nprint('b')\n```"
    result = sanitize_snippet(src)
    assert "print('a')" in result and "print('b')" in result
    assert result.count("print") == 2
    assert "```" not in result
