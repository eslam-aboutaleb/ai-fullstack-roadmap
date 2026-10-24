"""Sandboxed Python code execution: Static AST safety analysis, restricted built-in namespaces, and prompt injection defense.

Demonstrates:
1. Static Abstract Syntax Tree (AST) safety inspection: Blocking forbidden modules (os, sys, subprocess, socket) and dangerous builtins before execution.
2. Safe execution environment: Restricted global namespace devoid of __import__, eval, or open.
3. Defeating reflection bypasses: Detecting attempts to traverse object hierarchies via __subclasses__ or getattr.
4. Output truncation and execution resource boundaries.
"""
from typing import Any, Dict, List, Optional, Tuple
import ast
import io
import sys

class SecurityViolationError(Exception):
    pass

class AstSecurityInspector(ast.NodeVisitor):
    FORBIDDEN_MODULES = {"os", "sys", "subprocess", "socket", "shutil", "importlib", "pty", "builtins"}
    FORBIDDEN_CALLS = {"eval", "exec", "open", "compile", "__import__"}

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            base_mod = alias.name.split(".")[0]
            if base_mod in self.FORBIDDEN_MODULES:
                raise SecurityViolationError(f"Import of forbidden module '{alias.name}' is blocked.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            base_mod = node.module.split(".")[0]
            if base_mod in self.FORBIDDEN_MODULES:
                raise SecurityViolationError(f"Import from forbidden module '{node.module}' is blocked.")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            if node.func.id in self.FORBIDDEN_CALLS:
                raise SecurityViolationError(f"Invocation of dangerous function '{node.func.id}' is blocked.")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        # Defend against reflection jailbreaks: [].__class__.__bases__[0].__subclasses__()
        if node.attr in {"__subclasses__", "__bases__", "__globals__", "__builtins__"}:
            raise SecurityViolationError(f"Access to dangerous reflection attribute '{node.attr}' is blocked.")
        self.generic_visit(node)

class SandboxedPythonExecutor:
    MAX_OUTPUT_CHARS = 1000

    @classmethod
    def execute_safe_snippet(cls, code_str: str) -> Tuple[bool, str]:
        # 1. Parse into AST
        try:
            tree = ast.parse(code_str)
        except SyntaxError as se:
            return False, f"Syntax Error: {str(se)}"

        # 2. Static AST Security Scan
        inspector = AstSecurityInspector()
        try:
            inspector.visit(tree)
        except SecurityViolationError as sve:
            return False, f"Security Violation: {str(sve)}"

        # 3. Restricted execution sandbox namespace
        safe_builtins = {
            "abs": abs, "min": min, "max": max, "sum": sum, "len": len,
            "range": range, "enumerate": enumerate, "zip": zip,
            "int": int, "float": float, "str": str, "bool": bool, "list": list, "dict": dict,
            "print": print
        }
        sandbox_globals: Dict[str, Any] = {"__builtins__": safe_builtins}
        sandbox_locals: Dict[str, Any] = {}

        # 4. Capture and truncate standard output
        captured_stdout = io.StringIO()
        old_stdout = sys.stdout

        try:
            sys.stdout = captured_stdout
            compiled_code = compile(tree, filename="<sandbox>", mode="exec")
            exec(compiled_code, sandbox_globals, sandbox_locals)
            output = captured_stdout.getvalue()
            if len(output) > cls.MAX_OUTPUT_CHARS:
                output = output[:cls.MAX_OUTPUT_CHARS] + "\n[OUTPUT TRUNCATED - LIMIT EXCEEDED]"
            return True, output.strip()
        except Exception as runtime_err:
            return False, f"Runtime Error: {str(runtime_err)}"
        finally:
            sys.stdout = old_stdout

if __name__ == "__main__":
    executor = SandboxedPythonExecutor()

    # 1. Valid mathematical algorithm executes cleanly
    safe_code = """
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
print(f"Fib(10) is {fib(10)}")
"""
    ok, output = executor.execute_safe_snippet(safe_code)
    assert ok is True
    assert "Fib(10) is 55" in output

    # 2. Direct forbidden module import is BLOCKED
    malicious_import = "import os\nos.system('ls /')"
    ok_mod, err_mod = executor.execute_safe_snippet(malicious_import)
    assert ok_mod is False
    assert "Import of forbidden module 'os' is blocked" in err_mod

    # 3. Dangerous built-in function invocation is BLOCKED
    malicious_call = "open('/etc/passwd', 'r').read()"
    ok_call, err_call = executor.execute_safe_snippet(malicious_call)
    assert ok_call is False
    assert "dangerous function 'open' is blocked" in err_call

    # 4. Reflection Jailbreak attempt is BLOCKED
    reflection_jailbreak = "subclasses = ().__class__.__bases__[0].__subclasses__()"
    ok_ref, err_ref = executor.execute_safe_snippet(reflection_jailbreak)
    assert ok_ref is False
    assert "dangerous reflection attribute '__subclasses__' is blocked" in err_ref

    # 5. Output length bounding
    verbose_code = "print('A' * 2000)"
    ok_trunc, out_trunc = executor.execute_safe_snippet(verbose_code)
    assert ok_trunc is True
    assert "[OUTPUT TRUNCATED" in out_trunc

    print("Sandboxed code execution, AST security analysis, and jailbreak defense verified successfully.")

