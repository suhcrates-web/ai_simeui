import json
from functools import wraps
from pathlib import Path
from utils.config import get_config


def get_project_path():
    return Path(__file__).parents[1]


def ensure_absolute_path(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if args:
            path = Path(args[0])
            if not path.is_absolute():
                new_path = get_project_path() / path
                args = (new_path,) + args[1:]
        return func(*args, **kwargs)

    return wrapper


@ensure_absolute_path
def find_file_extension_files(directory, extension):
    directory_path = Path(directory)
    files = list(directory_path.rglob(f'*.{extension}'))
    return [str(file) for file in files]


@ensure_absolute_path
def get_output_path(file_path, extension) -> Path:
    input_path = Path(file_path)
    file_path = input_path.with_suffix(f'.{extension}')
    return file_path


@ensure_absolute_path
def read_text_file(file_path):
    if isinstance(file_path, str):
        file_path = Path(file_path)

    if file_path.exists() and file_path.is_file():
        with file_path.open(mode='r', encoding='utf-8') as f:
            content = f.read()
        return content
    else:
        print(f"File '{file_path}' does not exist or is not a regular file.")
        return None


def load_prompt(template_name: str):
    prompt_path = get_project_path() / 'resource' / 'templates' / template_name
    return read_text_file(prompt_path)


def get_course_name():
    config = get_config()
    course_name = config['variables']['course_name']
    return course_name


def get_course_path():
    course_name = get_course_name()
    return get_project_path() / 'resource' / 'course' / course_name


def load_course_info():
    course_path = get_course_path()
    course_info_path = course_path / 'course-info.txt'
    return read_text_file(course_info_path)


def load_edu_memory(student_id):
    course_path = get_course_path()
    path = course_path / 'memory' / f'edu_memory_{student_id}.json'
    with path.open('r') as f:
        return json.load(f)


def save_edu_memory(student_id, edu_memory):
    course_path = get_course_path()
    path = course_path / 'memory' / f'edu_memory_{student_id}.json'
    with path.open('w') as f:
        json.dump(edu_memory, f, indent=4, ensure_ascii=False)


def load_student_info(student_id):
    student_path = get_project_path() / 'resource' / 'students'
    prompt_path = student_path / f'{student_id}.txt'
    return read_text_file(prompt_path)


@ensure_absolute_path
def collect_items_from_jsonl(dir_path):
    file_paths = find_file_extension_files(dir_path, 'json')
    collected_items = []

    for path in file_paths:
        with open(path, 'r', encoding='utf-8') as file:
            for line in file:
                item = json.loads(line)
                collected_items.append(item)

    return collected_items


@ensure_absolute_path
def find_file(root_path, file_name):
    root = Path(root_path)
    for file in root.glob('**/*'):
        if file.name == file_name:
            return file.resolve()
