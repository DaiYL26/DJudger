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


def check_py3_syatax(target:str, log:str) -> str:
    '''
        check python3 systax and kill the process and its subprocesses
    '''
    commds = [f'ag os {target} > {log}',
              f'ag multiprocessing {target} >> {log}',
              f'ag socket {target} >> {log}',
              f'ag requests {target} >> {log}',
              f'ag http {target} >> {log}']
    
    for commd in commds:
        os.system(commd)
        
    systax_info = ''
    with open(log, 'r') as err:
        for line in err.readlines():
            systax_info += line

    
    if systax_info != '':
        return systax_info + '\n Not Allow'
    
    try:
        subprocess.run(f'python3 {target} 2> {log}', shell=True, check=True, timeout=0.5)
    except subprocess.CalledProcessError:
        # check a systax error beacuse not zero return
        with open(log, 'r') as err:        
            for line in err.readlines():
                systax_info += line
    except subprocess.TimeoutExpired:
        # kill the process
        pass

    return systax_info


def compile_src(target: Tuple, language: str) -> str:
    '''
        convert source file to executable file.
        
        return a string that is the path of the exectable file.
    '''
    target_file = target[0] + target[1]

    info_file = f'{target[0]}/{target[1]}compile_info.log'
    if language == 'Python3':
        compile_info = check_py3_syatax(target_file, info_file)
        if compile_info != '':
            return compile_info

        return target_file
    
    if language == 'C':
        if os.system(f'gcc {target_file} -o {target[0]}/main 2> {info_file}') != 0:
            error_info = ''
            with open(info_file) as info:
                for line in info.readlines():
                    error_info += line
            return error_info
                
    elif language == 'C++':
        if os.system(f'g++ {target_file} -o {target[0]}/main 2> {info_file}') != 0:
            error_info = ''
            with open(info_file) as info:
                for line in info.readlines():
                    error_info += line
            return error_info
    
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
            runcnf['args'] = ['python3', exec_file, '2>', './error.log']
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
        res = run_one(exec_file, in_path, out_path, tmp_path, 1000, 20 * 1024, language)
        res['result'] = RESULT_STR[res['result']]
        results.append(res)

    return results


def remove_tmp_file(user: str) -> None:
    '''
        remove the temporary files creating in the test by the user
    '''
    dpath = os.path.join('user_code/user', user)
    for item in [ os.path.join(dpath, sub) for sub in os.listdir(dpath) ]:
        os.remove(item)
        

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



if __name__ == '__main__':
    
    print (judge('1001', '1', 'C++', '''
#include <iostream>
#include <cstring>
#include <set>
#include <unordered_map>
#include <unistd.h>
using namespace std;

const int N = 1e5;

// head 邻接表头，vertex存的顶点，next_p 存邻接表下一条边， idx 指针
int head[N], vertex[N], next_p[N], idx;
int n, m, ans = 1e9;
// colors[c] = {} 染成颜色 c 的点的集合
unordered_map<int, set<int>> colors;
unordered_map<int, set<int>> result;

//邻接表加边
void add(int a, int b)
{
    vertex[idx] = b, next_p[idx] = head[a], head[a] = idx ++;
}

// 检查当前点 cur 能否染成 color 色
bool check(int cur, int color)
{
    for (int i = head[cur]; i != -1; i = next_p[i])
    {
        int target = vertex[i]; // cur 的邻点

        if (colors[color].find(target) != colors[color].end())
            return false;
    }

    return true;
}

// cur 当前点， color_num 颜色数
void draw(int cur, int color_num)
{
    if (color_num >= ans) return; //剪枝

    if (cur > n)
    {
        ans = min(ans, color_num); // 取最小的颜色方案数
        for (int i = 1; i <= color_num; i ++)
        {
            result[i] = colors[i];
        }
        return;
    }

    // 依次枚举颜色
    for (int c = 1; c <= color_num; c++)
    {
        if (check(cur, c)) // 当前点 是否 能染成颜色 c
        {
            colors[c].insert(cur);
            draw(cur + 1, color_num); //不扩充颜色，染下一个点
            colors[c].erase(cur);
        }
    }

    colors[color_num + 1].insert(cur);
    draw(cur + 1, color_num + 1); // 扩充颜色，染下一个点
    colors[color_num + 1].erase(cur);
}

int main()
{
    cin >> n >> m;
    memset(head, -1, sizeof head);
    for (int i = 0; i < m; i ++)
    {
        int a, b;
        cin >> a >> b;
        add(a, b);
        add(b, a);
    }

    draw(1, 0);

    // for (auto kv = result.begin(); kv != result.end(); kv ++)
    // {
    //     cout << "color " << kv->first << " : ";
    //     for (auto item = kv->second.begin(); item != kv->second.end(); item ++)
    //         cout << *item << ' ';
    //     cout << endl;
    // }
    
    cout << ans << endl;

    return 0;
}
'''))