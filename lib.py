NOT_COURSES = {'tools'}
NOT_CONTESTS = {'templates'}


def find_problems(repo_root):
    """Finds all problems in a problem repo."""

    def filtered_subdirs(dir, ignored):
        return (entry for entry in dir.iterdir() if entry.is_dir() and
                entry.name not in ignored and not entry.name.startswith('.'))

    for course_dir in filtered_subdirs(repo_root, NOT_COURSES):
        for contest_dir in filtered_subdirs(course_dir, NOT_CONTESTS):
            yield from (dir for dir in filtered_subdirs(contest_dir, []) if
                        (dir / 'problem.tex').is_file())
