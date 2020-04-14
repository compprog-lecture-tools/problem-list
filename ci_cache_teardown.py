#!/usr/bin/env python3
import pathlib
import shutil
import sys

SCRIPT_DIR = pathlib.Path(__file__).absolute().parent
sys.path.append(str(SCRIPT_DIR))
from lib import find_problems


def main():
    """Move build directories back to cache dir."""
    root_dir = pathlib.Path.cwd()
    cache_dir = root_dir / '.cache/build'
    cache_dir.mkdir(exist_ok=True, parents=True)

    problem_dirs = find_problems(root_dir)
    for problem_dir in problem_dirs:
        problem = problem_dir.name
        contest = problem_dir.parent.name
        course = problem_dir.parents[1].name
        build_dir = problem_dir / 'build'
        if build_dir.is_dir():
            print(f'Caching build dir for {course}/{contest}/{problem}')
            cache_dir_name = f'{course}__{contest}__{problem}'
            build_dir.rename(cache_dir / cache_dir_name)


if __name__ == '__main__':
    main()
