import re
from enum import Enum, auto
from typing import List, Union

# 1. Token types
class TokenType(Enum):
    INTEGER    = auto()
    FLOAT      = auto()
    PLUS       = auto()
    MINUS      = auto()
    MULTIPLY   = auto()
    DIVIDE     = auto()
    LPAREN     = auto()
    RPAREN     = auto()
    SIN        = auto()
    COS        = auto()
    IDENTIFIER = auto()
    EOF        = auto()

# 2. Token and Lexer
class Token:
    def __init__(self, type: TokenType, value: Union[str, int, float, None]):
        self.type  = type
        self.value = value

    def __repr__(self):
        return f'Token({self.type.name}, {self.value!r})'

# regex specs for each token
_TOKEN_SPEC = [
    (r'\d+\.\d+',    TokenType.FLOAT),
    (r'\d+',         TokenType.INTEGER),
    (r'sin\b',       TokenType.SIN),
    (r'cos\b',       TokenType.COS),
    (r'\+',          TokenType.PLUS),
    (r'-',           TokenType.MINUS),
    (r'\*',          TokenType.MULTIPLY),
    (r'/',           TokenType.DIVIDE),
    (r'\(',          TokenType.LPAREN),
    (r'\)',          TokenType.RPAREN),
    (r'[A-Za-z_]\w*',TokenType.IDENTIFIER),
    (r'\s+',         None),           # skip whitespace
]

_master_pattern = re.compile(
    '|'.join(f'(?P<T{i}>{pat})' for i, (pat, _) in enumerate(_TOKEN_SPEC))
)

def lex(text: str) -> List[Token]:
    tokens: List[Token] = []
    for m in _master_pattern.finditer(text):
        tok_type = None
        for i, (_, ttype) in enumerate(_TOKEN_SPEC):
            if m.lastgroup == f'T{i}':
                tok_type = ttype
                break
        lexeme = m.group(0)
        if tok_type is None:
            continue  # skip (whitespace)
        if tok_type == TokenType.INTEGER:
            value = int(lexeme)
        elif tok_type == TokenType.FLOAT:
            value = float(lexeme)
        else:
            value = lexeme
        tokens.append(Token(tok_type, value))
    tokens.append(Token(TokenType.EOF, None))
    return tokens

# 3. AST node definitions
class AST:
    pass

class Num(AST):
    def __init__(self, token: Token):
        self.value = token.value
    def __repr__(self):
        return f'Num({self.value})'

class Var(AST):
    def __init__(self, token: Token):
        self.name = token.value
    def __repr__(self):
        return f'Var({self.name})'

class BinOp(AST):
    def __init__(self, left: AST, op: Token, right: AST):
        self.left  = left
        self.token = op
        self.op    = op.type
        self.right = right
    def __repr__(self):
        return f'BinOp({self.left}, {self.op.name}, {self.right})'

class UnaryOp(AST):
    def __init__(self, op: Token, expr: AST):
        self.token = op
        self.op    = op.type
        self.expr  = expr
    def __repr__(self):
        return f'UnaryOp({self.op.name}, {self.expr})'

class FuncCall(AST):
    def __init__(self, name: str, arg: AST):
        self.name = name
        self.arg  = arg
    def __repr__(self):
        return f'FuncCall({self.name}, {self.arg})'

# 4. Recursive-descent Parser
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos    = 0
        self.current_token = self.tokens[self.pos]

    def error(self):
        raise Exception(f'Unexpected token: {self.current_token}')

    def eat(self, ttype: TokenType):
        if self.current_token.type == ttype:
            self.pos += 1
            self.current_token = self.tokens[self.pos]
        else:
            self.error()

    def factor(self) -> AST:
        """factor : (PLUS|MINUS) factor
                   | INTEGER | FLOAT
                   | IDENTIFIER
                   | (SIN|COS) LPAREN expr RPAREN
                   | LPAREN expr RPAREN
        """
        tok = self.current_token
        if tok.type in (TokenType.PLUS, TokenType.MINUS):
            self.eat(tok.type)
            node = UnaryOp(tok, self.factor())
            return node

        if tok.type in (TokenType.INTEGER, TokenType.FLOAT):
            self.eat(tok.type)
            return Num(tok)

        if tok.type == TokenType.IDENTIFIER:
            self.eat(TokenType.IDENTIFIER)
            return Var(tok)

        if tok.type in (TokenType.SIN, TokenType.COS):
            func_name = tok.value
            self.eat(tok.type)
            self.eat(TokenType.LPAREN)
            arg = self.expr()
            self.eat(TokenType.RPAREN)
            return FuncCall(func_name, arg)

        if tok.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node

        self.error()

    def term(self) -> AST:
        """term : factor ((MULTIPLY|DIVIDE) factor)*"""
        node = self.factor()
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            op = self.current_token
            self.eat(op.type)
            node = BinOp(node, op, self.factor())
        return node

    def expr(self) -> AST:
        """expr : term ((PLUS|MINUS) term)*"""
        node = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token
            self.eat(op.type)
            node = BinOp(node, op, self.term())
        return node

    def parse(self) -> AST:
        ast = self.expr()
        if self.current_token.type != TokenType.EOF:
            self.error()
        return ast

# 5. Example usage
if __name__ == '__main__':
    text = "3 + 5 * (10 - 2) + sin(0.5) + cos(x) - y"
    tokens = lex(text)
    print("Tokens:", tokens)

    parser = Parser(tokens)
    tree = parser.parse()
    print("AST:", tree)
