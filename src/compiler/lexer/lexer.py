from enum import Enum
from typing import Optional


# Stub Token classes (implement or import as needed)
class Token:
    pass


class ErrorToken(Token):
    def __init__(self, message: str, span: "Span"):
        self.message = message
        self.span = span

    def __repr__(self):
        return f"ErrorToken({self.message!r})"


class Operator(Token):
    def __init__(self, op_type: "OperatorType", span: "Span"):
        self.op_type = op_type
        self.span = span

    def __repr__(self):
        return f"Operator({self.op_type})"


class Separator(Token):
    def __init__(self, sep_type: "SeparatorType", span: "Span"):
        self.sep_type = sep_type
        self.span = span

    def __repr__(self):
        return f"Separator({self.sep_type})"


class Identifier(Token):
    def __init__(self, name: str, span: "Span"):
        self.name = name
        self.span = span

    def __repr__(self):
        return f"Identifier({self.name})"


class Keyword(Token):
    def __init__(self, keyword_type: "KeywordType", span: "Span"):
        self.keyword_type = keyword_type
        self.span = span

    def __repr__(self):
        return f"Keyword({self.keyword_type})"


class NumberLiteral(Token):
    def __init__(self, value: str, base: int, span: "Span"):
        self.value = value
        self.base = base
        self.span = span

    def __repr__(self):
        return f"NumberLiteral({self.value}, base={self.base})"


# Simplified Span class
class Span:
    def __init__(self, start_line: int, start_col: int, end_line: int, end_col: int):
        self.start_line = start_line
        self.start_col = start_col
        self.end_line = end_line
        self.end_col = end_col

    def __repr__(self):
        return (
            f"Span({self.start_line}:{self.start_col} - {self.end_line}:{self.end_col})"
        )


# Enumeration types
class OperatorType(Enum):
    MINUS = "-"
    ASSIGN_MINUS = "-="
    PLUS = "+"
    ASSIGN_PLUS = "+="
    MUL = "*"
    ASSIGN_MUL = "*="
    DIV = "/"
    ASSIGN_DIV = "/="
    MOD = "%"
    ASSIGN_MOD = "%="
    ASSIGN = "="


class SeparatorType(Enum):
    PAREN_OPEN = "("
    PAREN_CLOSE = ")"
    BRACE_OPEN = "{"
    BRACE_CLOSE = "}"
    SEMICOLON = ";"


class KeywordType(Enum):
    IF = "if"
    ELSE = "else"
    WHILE = "while"

    def keyword(self):
        return self.value


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line_start = 0
        self.line = 0

    @classmethod
    def for_string(cls, source: str) -> "Lexer":
        return cls(source)

    def next_token(self) -> Optional[Token]:
        error = self.skip_whitespace()
        if error is not None:
            return error
        if self.pos >= len(self.source):
            return None
        current_char = self.peek()

        if current_char == "(":
            return self.separator(SeparatorType.PAREN_OPEN)
        elif current_char == ")":
            return self.separator(SeparatorType.PAREN_CLOSE)
        elif current_char == "{":
            return self.separator(SeparatorType.BRACE_OPEN)
        elif current_char == "}":
            return self.separator(SeparatorType.BRACE_CLOSE)
        elif current_char == ";":
            return self.separator(SeparatorType.SEMICOLON)
        elif current_char == "-":
            return self.single_or_assign(OperatorType.MINUS, OperatorType.ASSIGN_MINUS)
        elif current_char == "+":
            return self.single_or_assign(OperatorType.PLUS, OperatorType.ASSIGN_PLUS)
        elif current_char == "*":
            return self.single_or_assign(OperatorType.MUL, OperatorType.ASSIGN_MUL)
        elif current_char == "/":
            return self.single_or_assign(OperatorType.DIV, OperatorType.ASSIGN_DIV)
        elif current_char == "%":
            return self.single_or_assign(OperatorType.MOD, OperatorType.ASSIGN_MOD)
        elif current_char == "=":
            return Operator(OperatorType.ASSIGN, self.build_span(1))
        else:
            if self.is_identifier_char(current_char):
                if self.is_numeric(current_char):
                    return self.lex_number()
                return self.lex_identifier_or_keyword()
            return ErrorToken(current_char, self.build_span(1))

    def skip_whitespace(self) -> Optional[ErrorToken]:
        current_comment_type = None  # "SINGLE_LINE" or "MULTI_LINE"
        multi_line_comment_depth = 0
        comment_start = -1
        while self.has_more(0):
            ch = self.peek()
            if ch in (" ", "\t"):
                self.pos += 1
            elif ch in ("\n", "\r"):
                self.pos += 1
                self.line_start = self.pos
                self.line += 1
                if current_comment_type == "SINGLE_LINE":
                    current_comment_type = None
            elif ch == "/":
                if current_comment_type == "SINGLE_LINE":
                    self.pos += 1
                    continue
                if self.has_more(1):
                    next_ch = self.peek(1)
                    if next_ch == "/" and current_comment_type is None:
                        current_comment_type = "SINGLE_LINE"
                        comment_start = self.pos
                        self.pos += 2
                        continue
                    elif next_ch == "*":
                        current_comment_type = "MULTI_LINE"
                        multi_line_comment_depth += 1
                        comment_start = self.pos
                        self.pos += 2
                        continue
                    elif current_comment_type == "MULTI_LINE":
                        self.pos += 1
                        continue
                    else:
                        return None
                if multi_line_comment_depth > 0:
                    self.pos += 1
                    continue
                return None
            else:
                if current_comment_type == "MULTI_LINE":
                    if ch == "*" and self.has_more(1) and self.peek(1) == "/":
                        self.pos += 2
                        multi_line_comment_depth -= 1
                        current_comment_type = (
                            None if multi_line_comment_depth == 0 else "MULTI_LINE"
                        )
                    else:
                        self.pos += 1
                    continue
                elif current_comment_type == "SINGLE_LINE":
                    self.pos += 1
                    continue
                return None
        if not self.has_more(0) and current_comment_type == "MULTI_LINE":
            return ErrorToken(self.source[comment_start:], self.build_span(0))
        return None

    def separator(self, sep_type: SeparatorType) -> Separator:
        return Separator(sep_type, self.build_span(1))

    def lex_identifier_or_keyword(self) -> Token:
        start_pos = self.pos
        while self.has_more(0) and self.is_identifier_char(self.peek()):
            self.pos += 1
        id_str = self.source[start_pos : self.pos]
        for value in KeywordType:
            if value.keyword() == id_str:
                return Keyword(value, self.build_span(self.pos - start_pos))
        return Identifier(id_str, self.build_span(self.pos - start_pos))

    def lex_number(self) -> Token:
        start_pos = self.pos
        if self.is_hex_prefix():
            self.pos += 2
            while self.has_more(0) and self.is_hex(self.peek()):
                self.pos += 1
            if self.pos - start_pos == 2:
                return ErrorToken(self.source[start_pos : self.pos], self.build_span(2))
            return NumberLiteral(
                self.source[start_pos : self.pos],
                16,
                self.build_span(self.pos - start_pos),
            )
        while self.has_more(0) and self.is_numeric(self.peek()):
            self.pos += 1
        if self.source[start_pos] == "0" and self.pos - start_pos > 1:
            return ErrorToken(
                self.source[start_pos : self.pos], self.build_span(self.pos - start_pos)
            )
        return NumberLiteral(
            self.source[start_pos : self.pos], 10, self.build_span(self.pos - start_pos)
        )

    def is_hex_prefix(self) -> bool:
        return self.peek() == "0" and self.has_more(1) and self.peek(1) in ("x", "X")

    def is_identifier_char(self, c: str) -> bool:
        return c == "_" or c.isalpha() or c.isdigit()

    def is_numeric(self, c: str) -> bool:
        return c.isdigit()

    def is_hex(self, c: str) -> bool:
        return c.isdigit() or c.lower() in "abcdef"

    def single_or_assign(self, single: OperatorType, assign: OperatorType) -> Operator:
        if self.has_more(1) and self.peek(1) == "=":
            # build_span here consumes two characters
            return Operator(assign, self.build_span(2))
        return Operator(single, self.build_span(1))

    def build_span(self, proceed: int) -> Span:
        start = self.pos
        # Create a span from the current position to the new position.
        span = Span(
            self.line,
            start - self.line_start,
            self.line,
            (start - self.line_start) + proceed,
        )
        self.pos += proceed
        return span

    def peek(self, offset: int = 0) -> str:
        return self.source[self.pos + offset]

    def has_more(self, offset: int) -> bool:
        return self.pos + offset < len(self.source)
