#!/usr/bin/env python-sirius
"""This script is used to find a window position."""
import subprocess, sys, re, shlex
from os import system

# Make sure xdotools is installed
try:
	subprocess.Popen('xdotool', stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
except OSError as e:
	if 'No such file' in e.args[1]:
		print("ERROR: The program 'xdotool' is not installed. Use "\
		      "'sudo apt-get install xdotool' to install it.")
		sys.exit(1)

PRODUCE_SCRIPT = False
LAUNCHED = []

def run_cmd(cmd):
	''' Run a command '''
	proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE,
	                                        stderr=subprocess.PIPE)
	return proc

def get_proc_output(proc):
	out, err = proc.communicate()
	return out.decode("UTF-8"), err.decode("UTF-8")

def get_cmd_output(cmd):
	''' Run a command and get its output'''
	return get_proc_output(run_cmd(cmd))

def xdo(do):
	out, err = get_cmd_output('xdotool ' + do)
	if err:
		print('ERROR: %s' % err)
	return out

def win_pid(wid):
	''' Gives the PID of the process that window belongs to '''
	return xdo('getwindowpid %s' % wid).strip()

def current_windows():
	''' Gives a list with all open windows '''
	out, err = get_cmd_output('xprop -root')
	match = re.search(r'_NET_CLIENT_LIST_STACKING\(WINDOW\): window id # (.*)', out)
	if not match:
		return None
	return match.group(1).split(', ')

def win_name(wid):
    ''' Gives the name of a window '''
    return xdo('getwindowname %s' % wid).strip()

def win_size(wid, x=None, y=None):
	if x is None or y is None:
		out = xdo('getwindowgeometry %s' % wid)
		match = re.search(r'Geometry: (.*)', out)
		if not match:
			return (None, None)
		return map(int, match.group(1).split('x'))
	else:
		xdo('windowsize %s %s %s' % (wid, x, y))

def win_pos(wid, x=None, y=None):
	if x is None or y is None:
		out = xdo('getwindowgeometry %s' % wid)
		match = re.search(r'Position: (\d*,\d*)', out)
		if not match:
			return (None, None)
		return map(int, match.group(1).split(','))
	else:
		xdo('windowmove %s %s %s' % (wid, x, y))

'''get a process command/arguments using process id'''
def process_comm_args(pid):
    sub_proc = subprocess.Popen(['ps', '-p', str(pid), '-o', 'args'], shell=False, stdout=subprocess.PIPE)
    sub_proc.stdout.readline()
    proc_info = ''
    for line in sub_proc.stdout:
        proc_info = line.decode('utf-8')
    return proc_info

def win_screen(wid):
	out = xdo('getwindowgeometry %s' % wid)
	match = re.search(r'Position: \d*,\d* \(screen: (\d*)\)', out)
	if not match:
		return None
	return int(match.group(1))

'''test function'''
def get_all_pca():
    cw = current_windows()
    r = []
    for id in cw:
        pid = win_pid(id)
        p = process_comm_args(pid)
        if 'python-sirius' and '/sirius-' in p:
            app = p.split('/')
            app[-1] = app[-1][:len(app[-1])-1]
            obj = (app[-1], list(win_pos(id)), list(win_size(id)))
            r.append(obj)
    return r

def open_window():
    #==================change path before commiting================
    system('/home/sirius/Documents/Rone/hla/pyqt-apps/scripts/sirius-hla-as-ap-launcher.py -x 100 -y 20 -wi 858 -he 171')

open_window()
