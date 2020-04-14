#!/usr/bin/env python3
import pathlib
import shutil
import sys

SCRIPT_DIR = pathlib.Path(__file__).absolute().parent
sys.path.append(str(SCRIPT_DIR))
from lib import find_problems


def main():
    """Symlink problem build directories to a central cache dir.

    This directory can then be cached by gitlab ci. Also delete build
    directories for unknown problems, to avoid the cache growing when problems
    get renamed or removed.
    """
    root_dir = pathlib.Path.cwd()
    cache_dir = root_dir / '.cache/build'
    cache_dir.mkdir(exist_ok=True, parents=True)

    problem_dirs = find_problems(root_dir)
    known_build_dirs = set()
    for problem_dir in problem_dirs:
        problem = problem_dir.name
        contest = problem_dir.parent.name
        course = problem_dir.parents[1].name
        problem_cache_dir = cache_dir / f'{course}__{contest}__{problem}'
        problem_cache_dir.mkdir(exist_ok=True)
        (problem_dir / 'build').symlink_to(problem_cache_dir,
                                           target_is_directory=True)
        known_build_dirs.add(problem_cache_dir.name)
        print(f'Set up build caching for {course}/{contest}/{problem}')

    for entry in cache_dir.iterdir():
        if not entry.is_dir():
            continue
        if entry.name not in known_build_dirs:
            print(f'Deleting unknown build dir {entry.name}')
            shutil.rmtree(entry)


if __name__ == '__main__':
    main()
