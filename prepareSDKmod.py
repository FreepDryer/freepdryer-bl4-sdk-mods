import argparse
import shutil
import tempfile
import re
from pathlib import Path

def makeSDKmod(modName, directory):
    source_dir = Path(directory).resolve()
    if not source_dir.is_dir():
        raise NotADirectoryError(source_dir)

    output_path = source_dir / f"{modName}.sdkmod"

    with tempfile.TemporaryDirectory() as tmpDir:
        tmp_path = Path(tmpDir)
        dest = tmp_path / modName
        shutil.copytree(
            source_dir,
            dest,
            ignore=shutil.ignore_patterns("*.sdkmod"),
            dirs_exist_ok=True,
        )

        archive_base = tmp_path / modName
        archive_path = Path(
            shutil.make_archive(
                str(archive_base),
                "zip",
                root_dir=tmp_path,
                base_dir=modName,
            )
        )

        if output_path.exists():
            output_path.unlink()
        shutil.move(str(archive_path), str(output_path))


def main():
    parser = argparse.ArgumentParser(
        prog='top'
    )
    parser.add_argument('directory')
    args = parser.parse_args()
    modName = re.sub(r'\W+', '', Path(args.directory).resolve().name)
    makeSDKmod(modName, args.directory)
if __name__ == "__main__":
    main()
