from pathlib import Path


class MockSubprocessContext:
    def __init__(self, returncode=0, text=""):
        self.returncode = returncode
        self.stdout = text

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


def full_plugin_path(path: str) -> str:
    basePath = Path(__file__).parent.parent
    return str(basePath.parent) + f"/chaosgrafana/{path}"
