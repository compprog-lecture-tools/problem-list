#!/usr/bin/env python3
import argparse
import datetime
import itertools
import json
import pathlib
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional, List

import jinja2

SCRIPT_DIR = pathlib.Path(__file__).absolute().parent
sys.path.append(str(SCRIPT_DIR))
from lib import find_problems

DIFFICULTIES = ['trivial', 'easy', 'medium', 'hard', 'very hard']
FEATURES = ['validator', 'answer-generator', 'interactor', 'python']
FEATURE_TITLES = [
    'Problems with a validator',
    'Problems with an answer generator',
    'Problems with an interactor',
    'Problems solvable in python',
]
TAGS = ['2-sat', 'binary search', 'bitmasks', 'brute force',
        'chinese remainder theorem', 'combinatorics', 'constructive algorithms',
        'data structures', 'dfs and similar', 'divide and conquer', 'dp', 'dsu',
        'expression parsing', 'fft', 'flows', 'games', 'geometry',
        'graph matchings', 'graphs', 'greedy', 'hashing', 'implementation',
        'math', 'matrices', 'meet-in-the-middle',
        'number theory', 'probabilities', 'schedules', 'shortest paths',
        'sortings', 'string suffix structures', 'strings', 'ternary search',
        'trees', 'two pointers']


@dataclass
class BasedOnInfo:
    # One of: 'codeforces', 'old-problem' or 'other'.
    type: str

    # Value depends on the type:
    #  * 'codeforces': Contest followed by problem id, i.e. ['988', 'C2'].
    #  * 'old-problem': List containing course, content and problem name, in
    #                   that order.
    #  * 'other': Only element is an arbitrary message, which should be
    #             displayed as-is.
    data: List[str]


@dataclass
class Problem:
    dir: pathlib.Path
    name: str
    course: str
    contest: str
    has_validator: bool
    has_interactor: bool
    has_answer_generator: bool
    has_python: bool
    difficulty: Optional[int]
    tags: Optional[List[str]]
    description: Optional[str]
    based_on: Optional[BasedOnInfo]
    statement_ok: bool = False
    notes_ok: bool = False

    def __str__(self):
        return f'{self.course}/{self.contest}/{self.name}'

    @property
    def ok(self):
        return (self.tags is not None and self.statement_ok and
                self.notes_ok and self.description)

    @classmethod
    def load(cls, problem_dir):
        try:
            with (problem_dir / 'problem.json').open() as f:
                data = json.load(f)
                difficulty = data['difficulty']
                tags = data['tags']
                description = data.get('description')
                based_on = data.get('based_on')
                if based_on is not None:
                    based_on = BasedOnInfo(type=based_on['type'],
                                           data=based_on['data'])
        except FileNotFoundError:
            difficulty, tags, description, based_on = None, None, None, None
        executables_dir = (problem_dir / 'executables')
        has_validator = any(executables_dir.glob('validator.*'))
        has_interactor = any(executables_dir.glob('interactor.*'))
        has_answer_generator = any(executables_dir.glob('answer-generator.*'))
        has_python = any(e for e in executables_dir.glob('solution*.py') if
                         not e.name.endswith('.wa.py') and
                         not e.name.endswith('.tle.py'))
        name = problem_dir.name
        contest = problem_dir.parent.name
        course = problem_dir.parents[1].name
        return cls(dir=problem_dir, name=name, contest=contest, course=course,
                   has_validator=has_validator, has_interactor=has_interactor,
                   has_answer_generator=has_answer_generator,
                   has_python=has_python, difficulty=difficulty, tags=tags,
                   description=description, based_on=based_on)


def build_pdfs(problems, out_dir):
    pdf_dir = out_dir / 'pdfs'
    pdf_dir.mkdir(exist_ok=True)
    for problem in problems:
        print(f'Building {problem}', flush=True)
        problem_pdf_dir = pdf_dir / str(problem)
        problem_pdf_dir.mkdir(exist_ok=True, parents=True)
        pdf_proc = subprocess.run(['make', 'pdf'], cwd=problem.dir)
        if pdf_proc.returncode == 0:
            shutil.copy2(problem.dir / 'build/problem/problem.pdf',
                         problem_pdf_dir / 'statement.pdf')
            problem.statement_ok = True
        else:
            problem.statement_ok = False

        problem.notes_ok = False
        check_notes_proc = subprocess.run(['make', 'check-notes'],
                                          cwd=problem.dir,
                                          stdout=subprocess.PIPE)
        if check_notes_proc.returncode == 0 and not check_notes_proc.stdout:
            notes_proc = subprocess.run(['make', 'notes'], cwd=problem.dir)
            if notes_proc.returncode == 0:
                problem.notes_ok = True
                shutil.copy2(
                    problem.dir / 'build' / f'{problem.name}-notes.pdf',
                    problem_pdf_dir / 'notes.pdf')


def group_problems(problems):
    def group_by_contest(problems):
        return sorted((contest_name, sorted(problems, key=lambda p: p.name)) for
                      contest_name, problems in
                      itertools.groupby(problems, lambda p: p.contest))

    def course_sort_key(course_name):
        # This sorts course names with the format `{course_name}{year_number}`
        # first by the year and then by the name. To make the code easier,
        # year_number is expected to be two digits long
        if len(course_name) >= 2 and course_name[-2:].isnumeric():
            return course_name[-2:] + course_name[:-2]
        return course_name

    grouped_by_course = ((course_name, group_by_contest(problems)) for
                         course_name, problems in
                         itertools.groupby(problems, lambda p: p.course))
    return sorted(grouped_by_course, key=lambda t: course_sort_key(t[0]))


def render_template(name, target_path, jinja_env, **kwargs):
    template = jinja_env.get_template(name)
    target_path.write_text(template.render(**kwargs))


def render_problem_list_template(name, target_path, jinja_env, problems,
                                 **kwargs):
    courses = group_problems(problems)
    render_template(name, target_path, jinja_env, courses=courses,
                    problems=problems, **kwargs)


def problem_html_id(course, contest, name):
    return f'{course}_{contest}_{name}'.replace(' ', '-')


def generate_pages(problems, args):
    print('Generating pages', flush=True)
    out_dir = args.out_dir
    git_hash = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'],
                              cwd=args.repo_root, stdout=subprocess.PIPE,
                              check=True, encoding='utf-8').stdout.strip()
    loader = jinja2.FileSystemLoader(str(SCRIPT_DIR / 'templates'))
    jinja_env = jinja2.Environment(loader=loader, lstrip_blocks=True)
    jinja_env.globals = {
        'DIFFICULTIES': DIFFICULTIES,
        'FEATURES': FEATURES,
        'TAGS': TAGS,
        'REPO_URL': args.repo_url,
        'REPO_BRANCH': args.repo_branch,
        'GIT_HASH': git_hash,
        'BUILD_TIME': datetime.datetime.now().isoformat(),
        'problem_html_id': problem_html_id,
    }

    not_ok_count = sum(1 for p in problems if not p.ok)
    render_problem_list_template('index.html', out_dir / 'index.html',
                                 jinja_env, problems, not_ok_count=not_ok_count)

    difficulties_dir = out_dir / 'difficulties'
    difficulties_dir.mkdir(exist_ok=True)
    render_template('difficulties/index.html', difficulties_dir / 'index.html',
                    jinja_env)
    for (index, name) in enumerate(DIFFICULTIES):
        target_file = difficulties_dir / (name.replace(' ', '-') + '.html')
        filtered_problems = [p for p in problems if p.difficulty == index + 1]
        render_problem_list_template('difficulties/by-difficulty.html',
                                     target_file, jinja_env, filtered_problems,
                                     difficulty_name=name)

    features_dir = out_dir / 'features'
    features_dir.mkdir(exist_ok=True)
    render_template('features/index.html', features_dir / 'index.html',
                    jinja_env)
    for name, title in zip(FEATURES, FEATURE_TITLES):
        target_file = features_dir / (name + '.html')
        filtered_problems = [p for p in problems if
                             getattr(p, 'has_' + name.replace('-', '_'))]
        render_problem_list_template('features/by-feature.html', target_file,
                                     jinja_env, filtered_problems,
                                     feature_name=name, title=title)

    tagged_dir = out_dir / 'tagged'
    tagged_dir.mkdir(exist_ok=True)
    render_template('tagged/index.html', tagged_dir / 'index.html', jinja_env)
    for tag in TAGS:
        target_file = tagged_dir / (tag + '.html')
        filtered_problems = [p for p in problems if p.tags and tag in p.tags]
        render_problem_list_template('tagged/by-tag.html', target_file,
                                     jinja_env, filtered_problems, tag_name=tag)

    incomplete_dir = out_dir / 'incomplete'
    incomplete_dir.mkdir(exist_ok=True)
    render_template('incomplete/index.html', incomplete_dir / 'index.html',
                    jinja_env)
    render_problem_list_template('incomplete/info.html',
                                 incomplete_dir / 'info.html', jinja_env,
                                 [p for p in problems if p.tags is None])
    render_problem_list_template('incomplete/description.html',
                                 incomplete_dir / 'description.html', jinja_env,
                                 [p for p in problems if
                                  p.tags is not None and not p.description])
    render_problem_list_template('incomplete/pdf.html',
                                 incomplete_dir / 'pdf.html', jinja_env,
                                 [p for p in problems if not p.statement_ok])
    render_problem_list_template('incomplete/notes.html',
                                 incomplete_dir / 'notes.html', jinja_env,
                                 [p for p in problems if not p.notes_ok])


def main():
    parser = argparse.ArgumentParser(description='Generate problem list pages')
    parser.add_argument('repo_root', type=pathlib.Path,
                        help='Problem repo to generate pages for')
    parser.add_argument('out_dir', type=pathlib.Path,
                        help='Directory to write pages to (can contain a '
                             '.build-info.json for an incremental build)')
    parser.add_argument('repo_url',
                        help='Repository url (works for github and gitlab)')
    parser.add_argument('--branch', default='master', dest='repo_branch',
                        help='Git branch (for repo urls)')
    args = parser.parse_args()

    args.out_dir.mkdir(exist_ok=True)
    problems = [Problem.load(dir) for dir in find_problems(args.repo_root)]
    build_pdfs(problems, args.out_dir)
    generate_pages(problems, args)


if __name__ == '__main__':
    main()
