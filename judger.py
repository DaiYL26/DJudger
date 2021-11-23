#!/usr/bin/python
#! -*- coding: utf8 -*-

import os
from typing import Tuple, Dict, List
import lorun
import subprocess


RESULT_STR = [
    'Accepted',
    'Presentation Error',
    'Time Limit Exceeded',
    'Memory Limit Exceeded',
    'Wrong Answer',
    'Runtime Error',
    'Output Limit Exceeded',
    'Compile Error',
    'System Error'
]

suffix = {'C': '.c', 'C++': '.cpp', 'Python3': '.py'}


def create_file(user: str, problem_id: str, code: str, language: str) -> Tuple:
    '''        
        create the source code file with the corresponding type. (C: .c, C++: .cpp, Python3: .py)
        
        return a tuple which contains source file directory path and file name
    '''
    file_name = user + '_' + problem_id + suffix[language]
    file_path = 'user_code/user/' + user + '/'
    
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    
    with open(file_path + file_name, 'w') as f:
        f.write(code)
    
    return (file_path, file_name)


def compile_src(target: Tuple, language: str) -> str:
    '''
        convert source file to executable file.
        
        return a string that is the path of the exectable file.
    '''
    target_file = target[0] + target[1]

    # compile .py file to binary .pyc file and check some invalid modules and systax error
    if language == 'Python3':
        check_forbidden = subprocess.Popen(f'ag "os|threading|multiprocessing" {target_file}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = check_forbidden.communicate()
        if check_forbidden.returncode == 0:
            return "These modules are not allow in here! \n  " + str(out, encoding='utf-8')
        
        py_compile = subprocess.Popen(f'python3 -m py_compile {target_file}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = py_compile.communicate()
        if py_compile.returncode != 0:
            return str(err, encoding='utf-8')

        pyc_file = target[0] + '__pycache__/' + target[1].replace('py', 'cpython-38.pyc')
                
        return pyc_file
    
    if language == 'C':
        c_compile = subprocess.Popen(f'gcc {target_file} -o {target[0]}main', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = c_compile.communicate()
        if c_compile.returncode != 0:
            return str(err, encoding='utf-8')
                
    elif language == 'C++':
        cpp_compile = subprocess.Popen(f'g++ {target_file} -o {target[0]}main', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = cpp_compile.communicate()
        if cpp_compile.returncode != 0:
            return str(err, encoding='utf-8')
    
    return target[0] + 'main'  


def run_one(exec_file: str, data_path_in: str, data_path_out: str, tmp_path: str, limit_time: int, limit_memory:int, language: str) -> Dict:   
    '''
        parameter:
            exec_file is the path of executable file
            data_path_in is the path of input file
            data_path_out is the path of answer file
            tmp_path is the temporary output file for the testing program
        
        run a test case for the testing program.
        
        return a dict that contains test result of testing programs for current case
    '''
    with open(data_path_in) as fin, open(tmp_path, 'w') as ftmp:
        runcnf = {
            'fd_in': fin.fileno(),
            'fd_out': ftmp.fileno(),
            'timelimit': limit_time, #in MS
            'memorylimit': limit_memory, #in KB
        }
        
        if language == 'Python3':
            runcnf['args'] = ['python3', exec_file]
        elif language == 'C' or language == 'C++':
            runcnf['args'] = ['./' + exec_file]
            runcnf['trace'] = True
            runcnf['calls'] = [0, 1, 3, 5, 8, 9, 10, 11, 12, 17, 20, 21, 63, 89, 99, 158, 228, 231, 257]
            runcnf['files'] = {'/etc/ld.so.cache': 0}
        
        res = lorun.run(runcnf)
    
    if res['result'] == 0:
        with open(tmp_path) as ftmp, open(data_path_out) as fout:
            crst = lorun.check(fout.fileno(), ftmp.fileno())
        # os.remove(tmp_path)
        if crst != 0:
            return {'result':crst}

    return res   


def get_result(exec_file: str, language: str, problem_id: str, tmp_path: str) -> List:
    '''
        to get the results for the problem
        
        return a List that contains the result for every case.
    '''
    sample_cnt = len(os.listdir('problem/1')) // 2
    
    data_path = os.path.join('problem', problem_id)
    
    results = []
    
    for _ in range(sample_cnt):
        in_path = os.path.join(data_path, str(_) + '.in')
        out_path = os.path.join(data_path, str(_) + '.out')
        # tmp_path = 'user_code/user/1001/tmp.txt'
        res = run_one(exec_file, in_path, out_path, tmp_path, 1000, 64 * 1024, language)
        res['result'] = RESULT_STR[res['result']]
        results.append(res)

    return results


def remove_tmp_file(user: str) -> None:
    '''
        remove the temporary files creating in the test by the user
    '''
    dpath = os.path.join('user_code/user', user)
    subprocess.run(f'rm -r {dpath}', shell=True)
        

def judge(user: str, problem_id: str, language: str, code: str, info='') -> List:
    '''
        judge the code is true or not
    '''
    # problem sample ptah: problem/{id}/
    # user_code path: user_code/user/{user}/
    # tmp_code
    target = create_file(user, problem_id, code, language) 
       
    exectable_file = compile_src(target, language)
    
    if not os.path.isfile(exectable_file):
        remove_tmp_file(user)
        return {'result': 'Compile Error', 'info': exectable_file}
    
    tmp_path = os.path.join(target[0], 'tmp.out')
    
    res = get_result(exectable_file, language, problem_id, tmp_path)
    
    remove_tmp_file(user)
    
    return res 