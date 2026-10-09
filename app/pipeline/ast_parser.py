import ast

class AntiPatternVisitor(ast.NodeVisitor):
    def __init__(self):
        self.flags = []

    def visit_FunctionDef(self, node):
        # 1. Detect mutable default arguments
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.flags.append("mutable_default_argument")
                break

        # 2. Detect missing return statement
        # We only flag if the function does not seem to be a stub (e.g. only contains pass or docstring)
        is_stub = False
        if len(node.body) == 1:
            stmt = node.body[0]
            if isinstance(stmt, ast.Pass):
                is_stub = True
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                is_stub = True

        if not is_stub and not self._has_direct_return(node):
            self.flags.append("missing_return_statement")

        self.generic_visit(node)

    def visit_Try(self, node):
        # 3. Detect bare except clauses
        for handler in node.handlers:
            if handler.type is None:
                self.flags.append("bare_except_clause")
                break
        self.generic_visit(node)

    def visit_While(self, node):
        # 4. Detect infinite loops without break/return/raise
        if self._is_condition_always_true(node.test):
            if not self._has_loop_terminator(node):
                self.flags.append("infinite_loop")
        self.generic_visit(node)

    def _has_direct_return(self, node):
        """Walks children to find if there is a Return statement directly belonging to this function."""
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(child, ast.Return):
                return True
            if self._has_direct_return(child):
                return True
        return False

    def _is_condition_always_true(self, test_node):
        """Checks if the loop condition is statically always truthy (e.g., True, 1, 'yes')."""
        if isinstance(test_node, ast.Constant):
            return bool(test_node.value)
        # Compat with older python ast forms
        if isinstance(test_node, ast.Name):
            if test_node.id == 'True':
                return True
        return False

    def _has_loop_terminator(self, node, allow_break=True):
        """Recursively checks if there is a return, raise, or break that can terminate the loop."""
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(child, (ast.Return, ast.Raise)):
                return True
            if isinstance(child, ast.Break) and allow_break:
                return True
            if isinstance(child, (ast.While, ast.For)):
                # Inside a nested loop, break won't terminate the outer loop, but return/raise will
                if self._has_loop_terminator(child, allow_break=False):
                    return True
            else:
                if self._has_loop_terminator(child, allow_break):
                    return True
        return False

def analyze_ast(code: str) -> list[str]:
    """Parses code and returns list of identified anti-pattern flags."""
    try:
        tree = ast.parse(code)
        visitor = AntiPatternVisitor()
        visitor.visit(tree)
        # Remove duplicates while preserving order
        seen = set()
        return [x for x in visitor.flags if not (x in seen or seen.add(x))]
    except SyntaxError:
        # If there's a syntax error, static analysis can't proceed, return empty
        return []
