# LoopBeat Lexer — Full Version
# Data types: int, float, bool, string, none, list
# Functions: func, return
# Control flow: if, else, while, for, in, break
# Operators: + - * / % == != < > <= >= and or not

class LexerError(Exception):
    pass

class Token:
    def __init__(self, type_, value, line=1):
        self.type  = type_
        self.value = value
        self.line  = line
    def __repr__(self):
        return f"{self.type}({self.value!r})"

KEYWORDS = {
    "print": "PRINT", "true": "BOOLEAN", "false": "BOOLEAN",
    "none": "NONE", "func": "FUNC", "return": "RETURN",
    "if": "IF", "else": "ELSE", "while": "WHILE",
    "for": "FOR", "in": "IN", "break": "BREAK",
    "and": "AND", "or": "OR", "not": "NOT",
}

class Lexer:
    def __init__(self, text):
        self.text         = text
        self.pos          = 0
        self.line         = 1
        self.current_char = text[self.pos] if text else None

    def advance(self):
        if self.current_char == '\n': self.line += 1
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def peek(self):
        p = self.pos + 1
        return self.text[p] if p < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char in (' ', '\t'): self.advance()

    def skip_newlines(self):
        while self.current_char == '\n': self.advance()

    def skip_comment(self):
        while self.current_char is not None and self.current_char != '\n': self.advance()

    def read_string(self):
        line = self.line
        self.advance()  # skip opening "
        result = ""
        while self.current_char is not None and self.current_char != '"':
            if self.current_char == '\\':
                self.advance()
                esc = {'n':'\n','t':'\t','\\':'\\','"':'"'}.get(self.current_char, self.current_char)
                result += esc
            else:
                result += self.current_char
            self.advance()
        if self.current_char != '"':
            raise LexerError(f"[Line {line}] Unterminated string")
        self.advance()  # skip closing "
        return Token("STRING", result, line)

    def number(self):
        line, result = self.line, ""
        is_float = False
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if is_float: break
                is_float = True
            result += self.current_char
            self.advance()
        return Token("FLOAT" if is_float else "INTEGER", result, line)

    def identifier(self):
        line, result = self.line, ""
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == "_"):
            result += self.current_char; self.advance()
        return Token(KEYWORDS.get(result, "IDENTIFIER"), result, line)

    def get_tokens(self):
        tokens = []
        while self.current_char is not None:
            if self.current_char in (' ', '\t'):   self.skip_whitespace(); continue
            if self.current_char == '#':            self.skip_comment();    continue
            if self.current_char == '\n':           self.skip_newlines();   continue
            if self.current_char == '"':            tokens.append(self.read_string()); continue
            if self.current_char.isdigit():         tokens.append(self.number());      continue
            if self.current_char.isalpha() or self.current_char == '_':
                tokens.append(self.identifier()); continue

            line = self.line
            c = self.current_char

            if c == '=':
                if self.peek() == '=': self.advance(); self.advance(); tokens.append(Token("EQEQ","==",line))
                else: tokens.append(Token("EQUAL","=",line)); self.advance()
            elif c == '!':
                if self.peek() == '=': self.advance(); self.advance(); tokens.append(Token("NEQ","!=",line))
                else: raise LexerError(f"[Line {line}] Invalid character: '!'")
            elif c == '<':
                if self.peek() == '=': self.advance(); self.advance(); tokens.append(Token("LTE","<=",line))
                else: tokens.append(Token("LT","<",line)); self.advance()
            elif c == '>':
                if self.peek() == '=': self.advance(); self.advance(); tokens.append(Token("GTE",">=",line))
                else: tokens.append(Token("GT",">",line)); self.advance()
            elif c == '+': tokens.append(Token("PLUS",    "+", line)); self.advance()
            elif c == '-': tokens.append(Token("MINUS",   "-", line)); self.advance()
            elif c == '*': tokens.append(Token("STAR",    "*", line)); self.advance()
            elif c == '/': tokens.append(Token("SLASH",   "/", line)); self.advance()
            elif c == '%': tokens.append(Token("PERCENT", "%", line)); self.advance()
            elif c == '(': tokens.append(Token("LPAREN",  "(", line)); self.advance()
            elif c == ')': tokens.append(Token("RPAREN",  ")", line)); self.advance()
            elif c == '{': tokens.append(Token("LBRACE",  "{", line)); self.advance()
            elif c == '}': tokens.append(Token("RBRACE",  "}", line)); self.advance()
            elif c == '[': tokens.append(Token("LBRACKET","[", line)); self.advance()
            elif c == ']': tokens.append(Token("RBRACKET","]", line)); self.advance()
            elif c == ',': tokens.append(Token("COMMA",   ",", line)); self.advance()
            elif c == ':': tokens.append(Token("COLON",   ":", line)); self.advance()
            else: raise LexerError(f"[Line {self.line}] Invalid character: {c!r}")

        tokens.append(Token("EOF", None, self.line))
        return tokens
