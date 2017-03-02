#!/usr/bin/env python3

import os
import sys

if __name__ == '__main__':

    if len(sys.argv) != 2:
        raise Exception('invalid number of arguments!')
        sys.exit(1);

    project = sys.argv[1]
    if os.path.exists(project):
        raise Exception('directory already exists!')

    os.system('cp -rf --preserve=mode template_files ' + project)
    os.rename(os.path.join(project, 'pcaspy-template'), os.path.join(project, project))
    os.rename(os.path.join(project, project, 'run.py'), os.path.join(project, project, project+'.py'))
    os.system('cd ' + project + '; ln -s ' + os.path.join(project,'VERSION'))
