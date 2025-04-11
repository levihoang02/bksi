import ast

banned_modules = [
    "os",
    "subprocess",
    "sys",
    "shutil",
    "socket",
    "threading",
    "multiprocessing",
    "signal",
    "ctypes",
    "pickle",
    "marshal",
    "resource",
    "fcntl",
    "pty",
    "select",
    "termios"
]

banned_functions = [
    "eval",
    "exec",
    "compile",
    "open",
    "input",
    "__import__",
    "getattr",
    "setattr",
    "globals",
    "locals"
]

banned_patterns = [
    "__dict__",
    "__class__"
]

banned_names = banned_modules + banned_functions + banned_patterns

def analyze_process_file(file_stream):
    """
    Analyze process.py and return warnings
    """
    warnings = []
    try:
        source = file_stream.read().decode('utf-8')
        tree = ast.parse(source)

        class WarningCollector(ast.NodeVisitor):
            def visit_Import(self, node):
                for alias in node.names:
                    mod = alias.name
                    if any(banned in mod for banned in banned_names):
                        line = getattr(node, 'lineno', '?')
                        warnings.append(f"Import '{mod}' is potentially unsafe. - at line {line}")

            def visit_ImportFrom(self, node):
                mod = node.module
                if mod and any(banned in mod for banned in banned_names):
                    line = getattr(node, 'lineno', '?')
                    warnings.append(f"Import from '{mod}' is potentially unsafe. - at line {line}")

            def visit_Call(self, node):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        func_name = f"{node.func.value.id}.{node.func.attr}"
                if func_name in banned_names:
                    lineno = getattr(node, "lineno", "?")
                    warnings.append(f"Usage of '{func_name}' is potentially unsafe. - at line {lineno}")
                self.generic_visit(node)

        collector = WarningCollector()
        collector.visit(tree)
        file_stream.seek(0)

    except Exception as e:
        warnings.append(f"Error parsing file: {str(e)}")

    return warnings

def has_process_function(file_stream):
    """
    check if file has process function
    """
    try:
        source = file_stream.read().decode('utf-8')
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "process":
                if len(node.args.args) >= 1:
                    file_stream.seek(0)
                    return True
        file_stream.seek(0)
        return False

    except Exception as e:
        file_stream.seek(0)
        print("Error parsing file:", e)
        return False
