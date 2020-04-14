#!/usr/bin/env python3
import pathlib
import shutil
import sys

SCRIPT_DIR = pathlib.Path(__file__).absolute().parent
sys.path.append(str(SCRIPT_DIR))
from lib import find_problems


def main():
    """Install cached build directories into the problems.

    Also delete build directories for unknown problems from the cache, to avoid
    the cache growing indefinitely when problems get renamed or removed.
    """
    root_dir = pathlib.Path.cwd()
    cache_dir = root_dir / '.cache/build'
    cache_dir.mkdir(exist_ok=True, parents=True)

    problem_dirs = find_problems(root_dir)
    known_build_dirs = {}
    for problem_dir in problem_dirs:
        problem = problem_dir.name
        contest = problem_dir.parent.name
        course = problem_dir.parents[1].name
        cache_dir_name = f'{course}__{contest}__{problem}'
        known_build_dirs[cache_dir_name] = problem_dir

    for entry in cache_dir.iterdir():
        if not entry.is_dir():
            continue
        problem_dir = known_build_dirs.get(entry.name)
        if problem_dir is None:
            print(f'Deleting unknown build dir {entry.name}')
            shutil.rmtree(entry)
        else:
            print(f'Importing cache dir {entry.name}')
            entry.rename(problem_dir / 'build')


if __name__ == '__main__':
    main()
