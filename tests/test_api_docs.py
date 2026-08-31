import ast
import unittest
from pathlib import Path


class PublicApiDocumentationTests(unittest.TestCase):
    def test_public_domain_classes_and_functions_have_docstrings(self) -> None:
        root = Path(__file__).parents[1] / "src" / "xyz_klipper_tool"
        missing: list[str] = []
        for path in root.rglob("*.py"):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if (
                    isinstance(
                        node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
                    )
                    and not node.name.startswith("_")
                    and ast.get_docstring(node) is None
                ):
                    missing.append(f"{path.name}:{node.name}")
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
