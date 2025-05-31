import pytest
from compiler.lexer.lexer import (
    Lexer,
    ErrorToken,
    Operator,
    Separator,
    Identifier,
    Keyword,
    NumberLiteral,
)
from compiler.lexer.lexer import OperatorType, SeparatorType, KeywordType


def test_single_character_tokens():
    tests = {
        "(": SeparatorType.PAREN_OPEN,
        ")": SeparatorType.PAREN_CLOSE,
        "{": SeparatorType.BRACE_OPEN,
        "}": SeparatorType.BRACE_CLOSE,
        ";": SeparatorType.SEMICOLON,
        "=": OperatorType.ASSIGN,
    }
    for input_char, expected in tests.items():
        lexer = Lexer.for_string(input_char)
        token = lexer.next_token()
        assert token is not None, f"Token for input '{input_char}' should not be None"
        if isinstance(token, Separator):
            result = token.sep_type
        elif isinstance(token, Operator):
            result = token.op_type
        else:
            result = None
        assert (
            result == expected
        ), f"Expected {expected} for input '{input_char}', got {result}"


def test_operator_single_or_assign():
    lexer = Lexer.for_string("-=")
    token = lexer.next_token()
    assert token is not None
    assert isinstance(token, Operator)
    assert token.op_type == OperatorType.ASSIGN_MINUS

    lexer = Lexer.for_string("+")
    token = lexer.next_token()
    assert token is not None
    assert isinstance(token, Operator)
    assert token.op_type == OperatorType.PLUS


def test_identifier_and_keyword():
    # Test Keyword
    lexer = Lexer.for_string("if")
    token = lexer.next_token()
    assert token is not None
    assert isinstance(token, Keyword), "Expected Keyword token for 'if'"
    assert token.keyword_type == KeywordType.IF

    # Test Identifier
    lexer = Lexer.for_string("var")
    token = lexer.next_token()
    assert token is not None
    assert isinstance(token, Identifier)
    assert token.name == "var"


def test_numeric_literal():
    # Decimal literal
    lexer = Lexer.for_string("123")
    token = lexer.next_token()
    assert token is not None
    assert isinstance(token, NumberLiteral)
    assert token.value == "123"
    assert token.base == 10

    # Hex literal
    lexer = Lexer.for_string("0x1A3")
    token = lexer.next_token()
    assert token is not None
    assert isinstance(token, NumberLiteral)
    # Lowercase comparison to handle case differences.
    assert token.value.lower() == "0x1a3"
    assert token.base == 16


if __name__ == "__main__":
    pytest.main()
