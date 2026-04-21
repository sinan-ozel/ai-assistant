#!/usr/bin/env python3
"""Check that agent_stem/src contains no print() calls.

Use logger instead: logger.debug / logger.info / logger.warning / logger.error
Annotate with  # noqa: T201  for the rare intentional use (e.g. DSL stdout injection).
"""

import ast
import pathlib
import sys


def check(src: pathlib.Path) -> list[str]:
    violations = []
    for path in sorted(src.rglob("*.py")):
        source = path.read_text()
        lines = source.splitlines()
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as e:
            violations.append(f"  {path}: SyntaxError: {e}")
            continue
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "print"
            ):
                continue
            if "# noqa: T201" in lines[node.lineno - 1]:
                continue
            violations.append(
                f"  {path}:{node.lineno}: {lines[node.lineno - 1].strip()}"
            )
    return violations


if __name__ == "__main__":
    root = pathlib.Path(__file__).parent.parent
    src = root / "agent_stem" / "src"

    violations = check(src)
    if violations:
        print("ERROR: print() calls found in agent_stem/src. Use logger instead.")
        print("       Annotate with  # noqa: T201  only for intentional DSL use.")
        for v in violations:
            print(v)
        sys.exit(1)

    print("OK: no print() calls in agent_stem/src.")
