from pylint.lint import Run
from io import StringIO
from pylint.reporters.text import TextReporter
import re
import os


class Code():
    def __init__(self, file_name):
        self.code = self.read_file(file_name)
        self.file_name : str = file_name


    def read_file(self, file_name):
        with open(file_name) as f:
            contents = f.readlines()

        return contents


    def replace_code(self, line_number, new_code):
        # also check if you are accessing data beyond the scope of code
        if line_number < len(self.code):
            self.code[line_number] = new_code
            return
        
        self.code.append(new_code)


    def get_loc(self, line_number):
        return self.code[line_number]
    
    def save_code(self, save_name=None):
        if save_name is None:
            save_name = os.path.splitext(self.file_name)[0] + '_new.py'
        
        contents = ''.join(self.code)
        with open(save_name, 'w') as f:
            f.write(contents)


def run_pylint(file_name):
    pylint_output = StringIO()
    reporter = TextReporter(pylint_output)
    Run([file_name], reporter=reporter, do_exit=False)

    output = pylint_output.getvalue()

    return output


def parse_pylint(file_name, pylint_output):
    split_messages = pylint_output.split('\n')

    error_msgs = []

    part_1_re = re.compile(re.escape(file_name) + r':([0-9]+):([0-9]+):.+\(([a-z\-]+)\)$')
    
    for message in split_messages:
        part_1 = part_1_re.search(message)

        if part_1 is None:
            continue
        
        error_dict = {'line_No' : int(part_1.group(1))-1, 'char' : int(part_1.group(2)), 'type' : part_1.group(3)}

        error_msgs.append(error_dict)

    return error_msgs


def process_pylint_msgs(error_msgs, code_object : Code, mode='save', file_name=None):
    for msg in error_msgs:
        line = code_object.get_loc(msg['line_No'])

        if msg['type'] == 'trailing-whitespace':
            code_object.replace_code(msg['line_No'], remove_trailing_whitespace(line))

        elif msg['type'] == 'missing-final-newline':
            # one line after the last line
            code_object.replace_code(msg['line_No']+1, '\n')

        # find a way of opening the file and figuring out what is referenced
        elif msg['type'] == 'wildcard-import':
            new_code = fix_wildcard_import(code_object.code, msg['line_No'])
            code_object.code = new_code

        # ignore this since the wildcard-immport error will solve the problem
        elif msg['type'] == 'unused-wildcard-import':
            continue

        else:
            print(msg['type'], msg['line_No'])

    if mode != 'save':
        return code_object.code

    code_object.save_code(file_name)


def remove_trailing_whitespace(line : str):
    new_line = line.rstrip()

    # check if line is empty
    if len(new_line) == 0:
        new_line = '\n'

    return new_line


def fix_wildcard_import(code, line_number):
    import_re = re.compile(r'from\s+([\w\.]+)')

    module = import_re.search(code[line_number]).group(1)

    path = os.path.join(*module.split('.')) + '.py'
    
    with open (path, 'r') as f:
        contents = f.read()

    list_of_references = []
    reference_re = re.compile(r'(class|def)\s+([a-zA-Z0-9_]+)')
    matches = reference_re.findall(contents)

    for m in matches:
        list_of_references.append(list(m))

    corrected_refs = []

    for x, line in enumerate(code):    
        for ref in list_of_references:
            ref_re = re.compile(r'[^a-zA-Z0-9]' + re.escape(ref[1]))
            ref_matches = ref_re.findall(line)

            for m in ref_matches:
                new_line = f'{module}.{m[1:]}'
                corrected_refs.append({'line' : x, 'old_line' : m[1:], 'new_line' : new_line})

    for corrected_ref in corrected_refs:
        code[corrected_ref['line']] = code[corrected_ref['line']].replace(corrected_ref['old_line'], corrected_ref['new_line'])

    # change the import statement now
    code[line_number] = f'import {module}'

    return code


if __name__ == '__main__':
    file_name = 'sample_code.py'

    code_object = Code(file_name)

    pylint_output = run_pylint(file_name=file_name)

    error_msgs = parse_pylint(file_name=file_name, pylint_output=pylint_output)

    process_pylint_msgs(error_msgs, code_object)
    