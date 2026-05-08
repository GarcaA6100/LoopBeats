# LoopBeat Interpreter — Full Version

from lexer  import Lexer,  LexerError
from parser import Parser, ParseError, \
    Program, AssignmentStatement, PrintStatement, ReturnStatement, \
    BreakStatement, IfStatement, WhileStatement, ForStatement, \
    FuncDef, ExprStatement, IndexAssign, \
    IntLiteral, FloatLiteral, StringLiteral, BoolLiteral, NoneLiteral, \
    ListLiteral, Identifier, BinaryOp, UnaryOp, CallExpr, IndexExpr

class InterpreterError(Exception): pass
class ReturnSignal(Exception):
    def __init__(self, value): self.value = value
class BreakSignal(Exception): pass

class Environment:
    def __init__(self, parent=None):
        self.vars = {}; self.parent = parent
    def get(self, name):
        if name in self.vars: return self.vars[name]
        if self.parent:       return self.parent.get(name)
        raise InterpreterError(f"Runtime error: '{name}' is not defined")
    def set(self, name, value): self.vars[name] = value
    def assign(self, name, value):
        if name in self.vars: self.vars[name] = value; return
        if self.parent:       self.parent.assign(name, value); return
        self.vars[name] = value  # create at current scope

class LBFunction:
    def __init__(self, name, params, body, closure):
        self.name=name; self.params=params; self.body=body; self.closure=closure
    def __repr__(self): return f"<func {self.name}>"

class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self._register_builtins()

    def _register_builtins(self):
        # Built-in functions
        self.global_env.set("len",    ("builtin", self._bi_len))
        self.global_env.set("str",    ("builtin", self._bi_str))
        self.global_env.set("int",    ("builtin", self._bi_int))
        self.global_env.set("float",  ("builtin", self._bi_float))
        self.global_env.set("type",   ("builtin", self._bi_type))
        self.global_env.set("append", ("builtin", self._bi_append))

    def _bi_len(self, args):
        if len(args)!=1: raise InterpreterError("len() takes 1 argument")
        v = args[0]
        if isinstance(v,(str,list)): return len(v)
        raise InterpreterError(f"len() does not support {self._tn(v)}")
    def _bi_str(self, args):
        if len(args)!=1: raise InterpreterError("str() takes 1 argument")
        return self._display(args[0])
    def _bi_int(self, args):
        if len(args)!=1: raise InterpreterError("int() takes 1 argument")
        try: return int(args[0])
        except: raise InterpreterError(f"Cannot convert {args[0]!r} to int")
    def _bi_float(self, args):
        if len(args)!=1: raise InterpreterError("float() takes 1 argument")
        try: return float(args[0])
        except: raise InterpreterError(f"Cannot convert {args[0]!r} to float")
    def _bi_type(self, args):
        if len(args)!=1: raise InterpreterError("type() takes 1 argument")
        return self._tn(args[0])
    def _bi_append(self, args):
        if len(args)!=2: raise InterpreterError("append() takes 2 arguments")
        if not isinstance(args[0],list): raise InterpreterError("append() requires a list")
        args[0].append(args[1]); return None

    def reset(self):
        self.global_env = Environment()
        self._current_output = []
        self._register_builtins()

    def run(self, source):
        output = []
        try: tokens = Lexer(source).get_tokens()
        except LexerError as e: return [], str(e)
        try: ast = Parser(tokens).parse()
        except (ParseError, Exception) as e: return [], str(e)
        try:
            self.reset()
            self._current_output = output
            self._exec_stmts(ast.stmts, self.global_env, output)
        except InterpreterError as e: return output, str(e)
        except Exception as e: return output, f"Runtime error: {e}"
        return output, None

    def _exec_stmts(self, stmts, env, output):
        for s in stmts: self._exec(s, env, output)

    def _exec(self, node, env, output):
        if isinstance(node, FuncDef):
            env.set(node.name, LBFunction(node.name, node.params, node.body, env))

        elif isinstance(node, AssignmentStatement):
            env.assign(node.name, self._eval(node.expr, env))

        elif isinstance(node, IndexAssign):
            obj = self._eval(node.obj, env)
            idx = self._eval(node.index, env)
            val = self._eval(node.value, env)
            if isinstance(obj, list):
                if not isinstance(idx,int): raise InterpreterError("List index must be integer")
                if idx < 0 or idx >= len(obj): raise InterpreterError(f"Index {idx} out of range")
                obj[idx] = val
            else: raise InterpreterError("Cannot index into non-list")

        elif isinstance(node, PrintStatement):
            output.append(self._display(self._eval(node.expr, env)))

        elif isinstance(node, IfStatement):
            cond = self._eval(node.cond, env)
            if not isinstance(cond, bool):
                raise InterpreterError(f"if condition must be bool, got {self._tn(cond)}")
            child = Environment(env)
            if cond: self._exec_stmts(node.then_body, child, output)
            elif node.else_body: self._exec_stmts(node.else_body, child, output)

        elif isinstance(node, WhileStatement):
            while True:
                cond = self._eval(node.cond, env)
                if not isinstance(cond, bool):
                    raise InterpreterError(f"while condition must be bool, got {self._tn(cond)}")
                if not cond: break
                try: self._exec_stmts(node.body, Environment(env), output)
                except BreakSignal: break

        elif isinstance(node, ForStatement):
            iterable = self._eval(node.iterable, env)
            if not isinstance(iterable, list):
                raise InterpreterError(f"for-in requires a list, got {self._tn(iterable)}")
            for item in iterable:
                child = Environment(env); child.set(node.var, item)
                try: self._exec_stmts(node.body, child, output)
                except BreakSignal: break

        elif isinstance(node, ReturnStatement):
            val = self._eval(node.expr, env) if node.expr else None
            raise ReturnSignal(val)

        elif isinstance(node, BreakStatement):
            raise BreakSignal()

        elif isinstance(node, ExprStatement):
            self._eval(node.expr, env)

        else:
            raise InterpreterError(f"Unknown statement: {type(node).__name__}")

    def _eval(self, node, env):
        if isinstance(node, IntLiteral):    return int(node.value)
        if isinstance(node, FloatLiteral):  return float(node.value)
        if isinstance(node, StringLiteral): return node.value
        if isinstance(node, BoolLiteral):   return node.value == "true"
        if isinstance(node, NoneLiteral):   return None
        if isinstance(node, ListLiteral):   return [self._eval(e,env) for e in node.elements]
        if isinstance(node, Identifier):    return env.get(node.name)

        if isinstance(node, IndexExpr):
            obj = self._eval(node.obj, env)
            idx = self._eval(node.index, env)
            if isinstance(obj, list):
                if not isinstance(idx,int): raise InterpreterError("List index must be integer")
                if idx < 0 or idx >= len(obj): raise InterpreterError(f"Index {idx} out of range")
                return obj[idx]
            if isinstance(obj, str):
                if not isinstance(idx,int): raise InterpreterError("String index must be integer")
                if idx < 0 or idx >= len(obj): raise InterpreterError(f"Index {idx} out of range")
                return obj[idx]
            raise InterpreterError(f"Cannot index into {self._tn(obj)}")

        if isinstance(node, UnaryOp):
            v = self._eval(node.operand, env)
            if node.op == "-":
                if isinstance(v,(int,float)) and not isinstance(v,bool): return -v
                raise InterpreterError(f"Unary '-' requires number, got {self._tn(v)}")
            if node.op == "not":
                if isinstance(v,bool): return not v
                raise InterpreterError(f"'not' requires bool, got {self._tn(v)}")

        if isinstance(node, BinaryOp):
            return self._binop(node.op, node.left, node.right, env)

        if isinstance(node, CallExpr):
            return self._call(node, env)

        raise InterpreterError(f"Unknown expression: {type(node).__name__}")

    def _binop(self, op, left_node, right_node, env):
        # short-circuit
        if op == "and":
            l = self._eval(left_node, env)
            if not isinstance(l,bool): raise InterpreterError("'and' requires bool")
            return l and self._eval(right_node, env)
        if op == "or":
            l = self._eval(left_node, env)
            if not isinstance(l,bool): raise InterpreterError("'or' requires bool")
            return l or self._eval(right_node, env)

        l = self._eval(left_node, env)
        r = self._eval(right_node, env)

        if op == "+":
            if isinstance(l,str) and isinstance(r,str): return l+r
            if isinstance(l,(int,float)) and isinstance(r,(int,float)) and not isinstance(l,bool) and not isinstance(r,bool):
                return l+r
            raise InterpreterError(f"'+' cannot combine {self._tn(l)} and {self._tn(r)}")
        if op == "-":
            self._req_num(l,r,op); return l-r
        if op == "*":
            self._req_num(l,r,op); return l*r
        if op == "/":
            self._req_num(l,r,op)
            if r==0: raise InterpreterError("Division by zero")
            return l/r
        if op == "%":
            self._req_num(l,r,op)
            if r==0: raise InterpreterError("Modulo by zero")
            return int(l)%int(r)
        if op == "==": return l==r
        if op == "!=": return l!=r
        if op in ("<",">","<=",">="):
            self._req_num(l,r,op)
            if op=="<":  return l<r
            if op==">":  return l>r
            if op=="<=": return l<=r
            if op==">=": return l>=r
        raise InterpreterError(f"Unknown operator: '{op}'")

    def _call(self, node, env):
        # check if it's a builtin first
        try: fn = env.get(node.name)
        except InterpreterError: raise InterpreterError(f"'{node.name}' is not defined")

        args = [self._eval(a, env) for a in node.args]

        if isinstance(fn, tuple) and fn[0]=="builtin":
            return fn[1](args)

        if isinstance(fn, LBFunction):
            if len(args) != len(fn.params):
                raise InterpreterError(f"'{fn.name}' expects {len(fn.params)} args, got {len(args)}")
            call_env = Environment(fn.closure)
            for p,a in zip(fn.params, args): call_env.set(p,a)
            try:
                self._exec_stmts(fn.body, call_env, self._current_output)
            except ReturnSignal as r:
                return r.value
            return None

        raise InterpreterError(f"'{node.name}' is not a function")

    def _req_num(self, l, r, op):
        if isinstance(l,bool) or isinstance(r,bool):
            raise InterpreterError(f"'{op}' cannot be used with bool")
        if not isinstance(l,(int,float)) or not isinstance(r,(int,float)):
            raise InterpreterError(f"'{op}' requires numbers, got {self._tn(l)} and {self._tn(r)}")

    def _tn(self, v):
        if isinstance(v,bool):  return "bool"
        if isinstance(v,int):   return "int"
        if isinstance(v,float): return "float"
        if isinstance(v,str):   return "string"
        if isinstance(v,list):  return "list"
        if isinstance(v,LBFunction): return "func"
        if v is None:           return "none"
        return type(v).__name__

    def _display(self, v):
        if v is None:            return "none"
        if isinstance(v,bool):   return "true" if v else "false"
        if isinstance(v,list):   return "[" + ", ".join(self._display(x) for x in v) + "]"
        if isinstance(v,LBFunction): return f"<func {v.name}>"
        if isinstance(v,float):
            return str(int(v)) if v==int(v) else str(v)
        return str(v)
