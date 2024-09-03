import os
import sys
import re






def write_version(version):
    with open("upsonic_on_prem/__init__.py", "r+") as file:
        content = file.read()
        content = re.sub(r"__version__ = '.*'", f"__version__ = '{version}'", content)  # fmt: skip
        file.seek(0)
        file.write(content)


def update_version(version):
    files = ["setup.py"]
    for file in files:
        with open(file, "r+") as f:
            content = f.read()
            content = re.sub(r'    version=".*"', f'    version="{version}"', content)
            f.seek(0)
            f.write(content)






def main():
    part = sys.argv[1]
    new_version = str(part) + "-dev"
    write_version(new_version)
    update_version(new_version)



if __name__ == "__main__":
    main()
