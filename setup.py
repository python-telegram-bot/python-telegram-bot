#!/usr/bin/env python
"""The setup and build script for the python-telegram-bot library."""
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from setuptools import find_packages, setup


def get_requirements() -> List[str]:
    """Build the requirements list for this project"""
    requirements_list = []

    with Path("requirements.txt").open(encoding="utf-8") as reqs:
        for install in reqs:
            if install.startswith("#"):
                continue
            requirements_list.append(install.strip())

    return requirements_list


def get_packages_requirements(raw: bool = False) -> Tuple[List[str], List[str]]:
    """Build the package & requirements list for this project"""
    reqs = get_requirements()

    exclude = ["tests*", "docs*"]
    if raw:
        exclude.append("telegram.ext*")

    packs = find_packages(exclude=exclude)

    return packs, reqs


def get_optional_requirements(raw: bool = False) -> Dict[str, List[str]]:
    """Build the optional dependencies"""
    requirements = defaultdict(list)

    with Path("requirements-opts.txt").open(encoding="utf-8") as reqs:
        for line in reqs:
            effective_line = line.strip()
            if not effective_line or effective_line.startswith("#"):
                continue
            dependency, names = effective_line.split("#")
            dependency = dependency.strip()
            for name in names.split(","):
                effective_name = name.strip()
                if effective_name.endswith("!ext"):
                    if raw:
                        continue
                    effective_name = effective_name[:-4]
                    requirements["ext"].append(dependency)
                requirements[effective_name].append(dependency)
                requirements["all"].append(dependency)

    return requirements


def get_setup_kwargs(raw: bool = False) -> Dict[str, Any]:
    """Builds a dictionary of kwargs for the setup function"""
    packages, requirements = get_packages_requirements(raw=raw)

    raw_ext = "-raw" if raw else ""
    readme = Path(f'README{"_RAW" if raw else ""}.rst')

    version_file = Path("telegram/_version.py").read_text(encoding="utf-8")
    first_part = version_file.split("# SETUP.PY MARKER")[0]
    exec(first_part)  # pylint: disable=exec-used

    return {
        "script_name": f"setup{raw_ext}.py",
        "name": f"python-telegram-bot{raw_ext}",
        "version": locals()["__version__"],
        "author": "Leandro Toledo",
        "author_email": "devs@python-telegram-bot.org",
        "license": "LGPLv3",
        "url": "https://python-telegram-bot.org/",
        # Keywords supported by PyPI can be found at
        # https://github.com/pypa/warehouse/blob/aafc5185e57e67d43487ce4faa95913dd4573e14/
        # warehouse/templates/packaging/detail.html#L20-L58
        "project_urls": {
            "Documentation": "https://docs.python-telegram-bot.org",
            "Bug Tracker": "https://github.com/python-telegram-bot/python-telegram-bot/issues",
            "Source Code": "https://github.com/python-telegram-bot/python-telegram-bot",
            "News": "https://t.me/pythontelegrambotchannel",
            "Changelog": "https://docs.python-telegram-bot.org/en/stable/changelog.html",
        },
        "download_url": f"https://pypi.org/project/python-telegram-bot{raw_ext}/",
        "keywords": "python telegram bot api wrapper",
        "description": "We have made you a wrapper you can't refuse",
        "long_description": readme.read_text(encoding="utf-8"),
        "long_description_content_type": "text/x-rst",
        "packages": packages,
        "install_requires": requirements,
        "extras_require": get_optional_requirements(raw=raw),
        "include_package_data": True,
        "classifiers": [
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
            "Operating System :: OS Independent",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Communications :: Chat",
            "Topic :: Internet",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
        ],
        "python_requires": ">=3.8",
    }


def main() -> None:
    # If we're building, build ptb-raw as well
    if set(sys.argv[1:]) in [{"bdist_wheel"}, {"sdist"}, {"sdist", "bdist_wheel"}]:
        args = ["python", "setup_raw.py"]
        args.extend(sys.argv[1:])
        subprocess.run(args, check=True, capture_output=True)

    setup(**get_setup_kwargs(raw=False))


if __name__ == "__main__":
    main()
