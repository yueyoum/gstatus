# -*- coding: utf-8 -*-

import re
import sys
import os
import json
import subprocess
from xml.sax.saxutils import unescape

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from bottle import Bottle, run, static_file
from jinja2 import Environment, FileSystemLoader

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
TEMPLATES_PATH = os.path.join(CURRENT_PATH, 'templates')
STATIC_PATH = os.path.join(CURRENT_PATH, 'static')
env = Environment(loader=FileSystemLoader(TEMPLATES_PATH))

lexer = get_lexer_by_name('diff')

def highlight_diff(text):
    return highlight(unescape(text.decode('utf-8')), lexer, HtmlFormatter())

COMMIT_PATTERN = re.compile('commit\s*(\w+)\nAuthor:\s*(.+)\nDate:\s*(.+)\n\n\s*(.+)')

step = 10
class Config(object):
    pass

config = Config()

class GitError(Exception):
    pass


def run_subprocess(command):
    os.chdir(config.git_repo_dir)
    p = subprocess.PIPE
    x = subprocess.Popen(command, stdout=p, stderr=p)
    o, e = x.communicate()
    if x.wait() != 0:
        raise GitError(e)
    return o, e


def get_git_commits(start):
    """return format:
    [ (a, b, c, d), (a, b, c, d)... ]
    a - commit hash
    b - author
    c - date
    d - commit log
    """
    command = ['git', 'log', '--date=iso']
    head_range = 'HEAD~{0}...HEAD~{1}'.format(start, start+step+1)
    command.append(head_range)
    out, err = run_subprocess(command)
    return COMMIT_PATTERN.findall(out)




def diff_commit(commitid_old, commitid_new):
    command = ['git', 'diff', '--name-only', commitid_old, commitid_new]
    out, err = run_subprocess(command)

    def diff_one_file(filename):
        command = ['git', 'diff', commitid_old, commitid_new, filename]
        out, err = run_subprocess(command)
        c = StringIO.StringIO(out)
        for i in range(4):
            c.readline()
        return {
            'filename': filename,
            'content': highlight_diff(''.join(c.readlines()))
        }

    return [diff_one_file(_f) for _f in out.split('\n') if _f]




def git_error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GitError as e:
            return {'error_msg': e}
    return wrapper
            

def jinja_view(tpl, **kwargs):
    _kwargs = kwargs
    def deco(func):
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            res.update(_kwargs)
            
            template = env.get_template(tpl)
            return template.render(**res)
        return wrapper
    return deco


app = Bottle()

@app.get('/static/<filename:path>')
def static_files(filename):
    return static_file(filename, root=STATIC_PATH)


@app.get('/')
@app.get('/page/<page:int>')
@jinja_view('index.html')
@git_error_handler
def index(page=0):
    def _uniform(commit):
        return {
            'id': commit[0],
            'author': commit[1].decode('utf-8'),
            'date': commit[2].split('+')[0],
            'log': commit[3].decode('utf-8'),
        }

    commits = map(_uniform, get_git_commits(page*step))
    for index in range(len(commits)):
        try:
            commits[index]['old_id'] = commits[index+1]['id']
        except IndexError:
            pass

    # drop the step+1 commit, get this commit just for get it's commit id
    commits.pop(-1)
    return {'commits': commits, 'page': page}


@app.get('/commit/<commitid_old>/<commitid_new>')
@jinja_view('diffs.html')
@git_error_handler
def index(commitid_old, commitid_new):
    diffs = diff_commit(commitid_old, commitid_new)
    return {'diffs': diffs}



if __name__ == '__main__':
    def usage():
        print "Invalid arguments! gstatus.py [GIT REPO DIR] [PORT]"
        sys.exit(1)

    if len(sys.argv) != 3:
        usage()

    _, git_repo_dir, port = sys.argv
    if not os.path.isdir(git_repo_dir):
        usage()

    port = int(port)

    config.git_repo_dir = git_repo_dir
    run(app, host='0.0.0.0', port=port)



