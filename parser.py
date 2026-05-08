# LoopBeat Parser — Full Version

class ParseError(Exception):
    pass

def _indent(text, level):
    prefix = "  " * level
    return "\n".join(prefix + line for line in text.splitlines())

# ── AST Nodes ──────────────────────────────────────────────────────────────

class Program:
    def __init__(self, stmts): self.stmts = stmts
    def pretty(self, l=0):
        return "Program\n" + "\n".join(_indent(s.pretty(), 1) for s in self.stmts)

class AssignmentStatement:
    def __init__(self, name, expr): self.name=name; self.expr=expr
    def pretty(self, l=0):
        return f"Assign({self.name})\n" + _indent(self.expr.pretty(), 1)

class PrintStatement:
    def __init__(self, expr): self.expr=expr
    def pretty(self, l=0): return "Print\n" + _indent(self.expr.pretty(), 1)

class ReturnStatement:
    def __init__(self, expr): self.expr=expr
    def pretty(self, l=0): return "Return\n" + (_indent(self.expr.pretty(), 1) if self.expr else "  none")

class BreakStatement:
    def pretty(self, l=0): return "Break"

class IfStatement:
    def __init__(self, cond, then_body, else_body): self.cond=cond; self.then_body=then_body; self.else_body=else_body
    def pretty(self, l=0):
        s = "If\n" + _indent(self.cond.pretty(), 1) + "\n" + _indent("Then:", 1)
        for st in self.then_body: s += "\n" + _indent(st.pretty(), 2)
        if self.else_body:
            s += "\n" + _indent("Else:", 1)
            for st in self.else_body: s += "\n" + _indent(st.pretty(), 2)
        return s

class WhileStatement:
    def __init__(self, cond, body): self.cond=cond; self.body=body
    def pretty(self, l=0):
        s = "While\n" + _indent(self.cond.pretty(), 1)
        for st in self.body: s += "\n" + _indent(st.pretty(), 2)
        return s

class ForStatement:
    def __init__(self, var, iterable, body): self.var=var; self.iterable=iterable; self.body=body
    def pretty(self, l=0):
        s = f"For({self.var}) in\n" + _indent(self.iterable.pretty(), 1)
        for st in self.body: s += "\n" + _indent(st.pretty(), 2)
        return s

class FuncDef:
    def __init__(self, name, params, body): self.name=name; self.params=params; self.body=body
    def pretty(self, l=0):
        s = f"FuncDef({self.name}, params={self.params})"
        for st in self.body: s += "\n" + _indent(st.pretty(), 1)
        return s

class ExprStatement:
    def __init__(self, expr): self.expr=expr
    def pretty(self, l=0): return "Expr\n" + _indent(self.expr.pretty(), 1)

# expressions
class IntLiteral:
    def __init__(self, v): self.value=v
    def pretty(self, l=0): return f"Int({self.value})"

class FloatLiteral:
    def __init__(self, v): self.value=v
    def pretty(self, l=0): return f"Float({self.value})"

class StringLiteral:
    def __init__(self, v): self.value=v
    def pretty(self, l=0): return f"String({self.value!r})"

class BoolLiteral:
    def __init__(self, v): self.value=v
    def pretty(self, l=0): return f"Bool({self.value})"

class NoneLiteral:
    def pretty(self, l=0): return "None"

class ListLiteral:
    def __init__(self, elements): self.elements=elements
    def pretty(self, l=0):
        s = "List"
        for e in self.elements: s += "\n" + _indent(e.pretty(), 1)
        return s

class Identifier:
    def __init__(self, name): self.name=name
    def pretty(self, l=0): return f"Ident({self.name})"

class BinaryOp:
    def __init__(self, op, left, right): self.op=op; self.left=left; self.right=right
    def pretty(self, l=0):
        return f"BinOp({self.op})\n" + _indent(self.left.pretty(),1) + "\n" + _indent(self.right.pretty(),1)

class UnaryOp:
    def __init__(self, op, operand): self.op=op; self.operand=operand
    def pretty(self, l=0): return f"UnaryOp({self.op})\n" + _indent(self.operand.pretty(),1)

class CallExpr:
    def __init__(self, name, args): self.name=name; self.args=args
    def pretty(self, l=0):
        s = f"Call({self.name})"
        for a in self.args: s += "\n" + _indent(a.pretty(), 1)
        return s

class IndexExpr:
    def __init__(self, obj, index): self.obj=obj; self.index=index
    def pretty(self, l=0): return f"Index\n" + _indent(self.obj.pretty(),1) + "\n" + _indent(self.index.pretty(),1)

class IndexAssign:
    def __init__(self, obj, index, value): self.obj=obj; self.index=index; self.value=value
    def pretty(self, l=0): return f"IndexAssign"


# ── Parser ─────────────────────────────────────────────────────────────────

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens; self.pos = 0
        self.current = tokens[0]

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens): self.current = self.tokens[self.pos]

    def eat(self, type_):
        if self.current.type == type_:
            t = self.current; self.advance(); return t
        line = getattr(self.current, 'line', '?')
        raise ParseError(f"[Line {line}] Expected {type_}, got {self.current.type} ({self.current.value!r})")

    def check(self, *types): return self.current.type in types

    def parse(self):
        stmts = []
        while not self.check("EOF"): stmts.append(self.statement())
        return Program(stmts)

    def statement(self):
        if self.check("FUNC"):   return self.func_def()
        if self.check("IF"):     return self.if_stmt()
        if self.check("WHILE"):  return self.while_stmt()
        if self.check("FOR"):    return self.for_stmt()
        if self.check("RETURN"): return self.return_stmt()
        if self.check("BREAK"):  self.advance(); return BreakStatement()
        if self.check("PRINT"):  return self.print_stmt()
        if self.check("IDENTIFIER"):
            # peek ahead for = (assignment) vs index assign vs expression
            return self.assign_or_expr()
        return ExprStatement(self.expression())

    def assign_or_expr(self):
        expr = self.expression()
        if self.check("EQUAL"):
            self.advance()
            val = self.expression()
            if isinstance(expr, Identifier):
                return AssignmentStatement(expr.name, val)
            elif isinstance(expr, IndexExpr):
                return IndexAssign(expr.obj, expr.index, val)
            else:
                raise ParseError("Invalid assignment target")
        return ExprStatement(expr)

    def print_stmt(self):
        self.eat("PRINT"); self.eat("LPAREN")
        expr = self.expression(); self.eat("RPAREN")
        return PrintStatement(expr)

    def return_stmt(self):
        self.eat("RETURN")
        expr = None
        if not self.check("RBRACE", "EOF"): expr = self.expression()
        return ReturnStatement(expr)

    def func_def(self):
        self.eat("FUNC")
        name = self.eat("IDENTIFIER").value
        self.eat("LPAREN")
        params = []
        if not self.check("RPAREN"):
            params.append(self.eat("IDENTIFIER").value)
            while self.check("COMMA"):
                self.advance()
                params.append(self.eat("IDENTIFIER").value)
        self.eat("RPAREN")
        body = self.block()
        return FuncDef(name, params, body)

    def if_stmt(self):
        self.eat("IF")
        cond = self.expression()
        then_body = self.block()
        else_body = None
        if self.check("ELSE"):
            self.advance()
            if self.check("IF"): else_body = [self.if_stmt()]
            else:                else_body = self.block()
        return IfStatement(cond, then_body, else_body)

    def while_stmt(self):
        self.eat("WHILE"); cond = self.expression(); body = self.block()
        return WhileStatement(cond, body)

    def for_stmt(self):
        self.eat("FOR"); var = self.eat("IDENTIFIER").value
        self.eat("IN"); iterable = self.expression(); body = self.block()
        return ForStatement(var, iterable, body)

    def block(self):
        self.eat("LBRACE")
        stmts = []
        while not self.check("RBRACE", "EOF"): stmts.append(self.statement())
        self.eat("RBRACE")
        return stmts

    # ── expressions ──

    def expression(self): return self.or_expr()

    def or_expr(self):
        node = self.and_expr()
        while self.check("OR"):
            self.advance(); node = BinaryOp("or", node, self.and_expr())
        return node

    def and_expr(self):
        node = self.not_expr()
        while self.check("AND"):
            self.advance(); node = BinaryOp("and", node, self.not_expr())
        return node

    def not_expr(self):
        if self.check("NOT"): self.advance(); return UnaryOp("not", self.not_expr())
        return self.comparison()

    def comparison(self):
        node = self.additive()
        while self.check("EQEQ","NEQ","LT","GT","LTE","GTE"):
            op = self.current.value; self.advance()
            node = BinaryOp(op, node, self.additive())
        return node

    def additive(self):
        node = self.multiplicative()
        while self.check("PLUS","MINUS"):
            op = self.current.value; self.advance()
            node = BinaryOp(op, node, self.multiplicative())
        return node

    def multiplicative(self):
        node = self.unary()
        while self.check("STAR","SLASH","PERCENT"):
            op = self.current.value; self.advance()
            node = BinaryOp(op, node, self.unary())
        return node

    def unary(self):
        if self.check("MINUS"): self.advance(); return UnaryOp("-", self.unary())
        return self.call_or_index()

    def call_or_index(self):
        node = self.primary()
        while True:
            if self.check("LPAREN"):
                self.advance()
                args = []
                if not self.check("RPAREN"):
                    args.append(self.expression())
                    while self.check("COMMA"): self.advance(); args.append(self.expression())
                self.eat("RPAREN")
                name = node.name if isinstance(node, Identifier) else str(node)
                node = CallExpr(name, args)
            elif self.check("LBRACKET"):
                self.advance(); idx = self.expression(); self.eat("RBRACKET")
                node = IndexExpr(node, idx)
            else: break
        return node

    def primary(self):
        t = self.current; line = getattr(t, 'line', '?')
        if t.type == "INTEGER":    self.advance(); return IntLiteral(t.value)
        if t.type == "FLOAT":      self.advance(); return FloatLiteral(t.value)
        if t.type == "STRING":     self.advance(); return StringLiteral(t.value)
        if t.type == "BOOLEAN":    self.advance(); return BoolLiteral(t.value)
        if t.type == "NONE":       self.advance(); return NoneLiteral()
        if t.type == "IDENTIFIER": self.advance(); return Identifier(t.value)
        if t.type == "LPAREN":
            self.advance(); node = self.expression(); self.eat("RPAREN"); return node
        if t.type == "LBRACKET":
            self.advance()
            elems = []
            if not self.check("RBRACKET"):
                elems.append(self.expression())
                while self.check("COMMA"): self.advance(); elems.append(self.expression())
            self.eat("RBRACKET"); return ListLiteral(elems)
        raise ParseError(f"[Line {line}] Unexpected token: {t.type} ({t.value!r})")
