import argparse
import shutil
import tempfile
import re

def makeSDKmod(modName, dir):
    with tempfile.TemporaryDirectory() as tmpDir:
        shutil.copytree(dir, tmpDir, ignore=shutil.ignore_patterns('*.sdkmod'), dirs_exist_ok=True)
        shutil.make_archive(modName, 'zip', tmpDir)
    shutil.move(f"{modName}.zip", f"{dir}{modName}.sdkmod")


def main():
    parser = argparse.ArgumentParser(
        prog='top'
    )
    parser.add_argument('directory')
    args = parser.parse_args()
    modName = re.sub(r'\W+', '', args.directory)
    makeSDKmod(modName, args.directory)
if __name__ == "__main__":
    main()