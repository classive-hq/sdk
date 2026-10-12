"""Inspect the distributable files that registries receive, not only source manifests."""
import argparse
from email.parser import BytesParser
import json
from pathlib import Path
import tarfile
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument("javascript_tarball", type=Path)
parser.add_argument("python_wheel", type=Path)
parser.add_argument("python_sdist", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]

with tarfile.open(args.javascript_tarball) as archive:
    names = set(archive.getnames())
    manifest = json.load(archive.extractfile("package/package.json"))
    readme = archive.extractfile("package/README.md").read()
    assert readme == (root / "javascript/README.md").read_bytes(), "npm received the wrong README"
    assert b"```python" not in readme and b"pip install" not in readme
    assert manifest["name"] == "@classive/sdk"
    assert manifest["author"]["name"] == "Classive Ltd"
    assert manifest["keywords"] and manifest["license"] == "MIT"
    assert manifest["repository"]["directory"] == "javascript"
    assert manifest["publishConfig"]["access"] == "public"
    assert "package/LICENSE" in names
    assert not any(name.startswith("package/python/") for name in names)
    for entrypoint in manifest["exports"]["."].values():
        assert "package/" + entrypoint.removeprefix("./") in names, entrypoint

with zipfile.ZipFile(args.python_wheel) as archive:
    names = archive.namelist()
    metadata = BytesParser().parsebytes(archive.read(next(name for name in names if name.endswith("/METADATA"))))
    assert metadata["Name"] == "classive-sdk"
    assert metadata["Author"] == "Classive Ltd"
    assert metadata["Keywords"] and metadata["License-Expression"] == "MIT"
    assert metadata["Requires-Python"] == ">=3.11"
    assert "Typing :: Typed" in metadata.get_all("Classifier")
    assert "classive/py.typed" in names
    assert any(name.endswith("/licenses/LICENSE") for name in names)
    assert any("python/README.md" in url for url in metadata.get_all("Project-URL"))
    assert metadata.get_payload().strip() == (root / "python/README.md").read_text().strip()

with tarfile.open(args.python_sdist) as archive:
    readme_path = next(name for name in archive.getnames() if name.endswith("/README.md"))
    assert archive.extractfile(readme_path).read() == (root / "python/README.md").read_bytes()

print("Distributable READMEs, metadata, licenses, types and JavaScript entrypoints verified.")
