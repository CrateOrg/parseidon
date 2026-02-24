from importlib import resources
from pathlib import Path
from contextlib import contextmanager
from typing import IO, Any, Generator, Literal


def file_exists(path: str) -> bool:
    p = Path(path)
    if p.exists():
        return True
    return resources.files("parseidon.data").joinpath(path).is_file()


@contextmanager
def open_file(
    path: str, mode: Literal["r"] | Literal["rb"]
) -> Generator[IO[Any], None, None]:
    p = Path(path)
    if p.exists():
        with p.open(mode) as f:
            yield f
    else:
        resource_path = resources.files("parseidon.data").joinpath(path)
        if not resource_path.is_file():
            raise FileNotFoundError(f"Not found as external file or resource: {path}")

        with resource_path.open(mode) as f:
            yield f
