#!/usr/bin/env python-sirius
"""This script is used to find a window position."""
import subprocess as _subprocess
import sys
import re
import shlex
import socket

# Make sure xdotools is installed
try:
	_subprocess.Popen('xdotool', stdout=_subprocess.PIPE,
                                    stderr=_subprocess.PIPE)
except OSError as e:
	if 'No such file' in e.args[1]:
		print("ERROR: The program 'xdotool' is not installed. Use "\
		      "'sudo apt-get install xdotool' to install it.")
		sys.exit(1)

PRODUCE_SCRIPT = False
LAUNCHED = []
win_info = dict(x=0,
				y=0,
				wi=0,
				he=0)


class WinInfoPos():

    def __init__(self, x, y, wi, he):
        self.x = x
        self.y = y
        self.wi = wi
        self.he = he

    def info(self):
        _dict = {'-x': self.x,
                 '-y': self.y,
                 '-wi': self.wi,
                 '-he': self.he}
        return _dict

def run_cmd(cmd):
	''' Run a command '''
	proc = _subprocess.Popen(shlex.split(cmd), stdout=_subprocess.PIPE,
	                                        stderr=_subprocess.PIPE)
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
    sub_proc = _subprocess.Popen(['ps', '-p', str(pid), '-o', 'args'], shell=False, stdout=_subprocess.PIPE)
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

'''get all system control window position/size info'''
def get_win_info(window=None):
	if window == None:
		cw = current_windows()
		r = []
		cfg = dict(window=None,size=(0,0), position=(0,0))
		for id in cw:
			pid = win_pid(id)
			p = process_comm_args(pid)
			if 'python-sirius' and '/sirius-' in p:
				# print(p)
				app = p.split('/')
				app[-1] = app[-1][:len(app[-1])-1]
				_cfg = cfg.copy()
				_cfg.update(window=app[-1], size=list(win_size(id)), position=list(win_pos(id)))
				r.append(_cfg)
		return r
	else:
		cw = current_windows()
		r = []
		cfg = dict(id=None,window='',size=(0,0), position=(0,0))
		for id in cw:
			pid = win_pid(id)
			p = process_comm_args(pid)
			if window in p:
				app = p.split('/')
				app[-1] = app[-1][:len(app[-1])-1]
				_cfg = cfg.copy()
				_cfg.update(id=id,window=app[-1], size=list(win_size(id)), position=list(win_pos(id)))
				r.append(_cfg)
		return r

def get_computer_name():
	return socket.gethostname()

def build_config():
	cfg = dict(computer='computername', config=[])
	cfg.update(computer=get_computer_name(), config=get_win_info())
	return cfg

#open window using arguments for positioning and sizing
# def open_window_args(window, pos):
# 	w = get_win_info(window)
# 	if w:
# 		wid = w[0]['id']
# 		x=pos['-x']
# 		y=pos['-y']
# 		wi=pos['-wi']
# 		he=pos['-he']
# 		cmd = "wmctrl -i -r " + wid +  " -e 0," + str(x) + "," + str(y) + "," + str(wi) + "," + str(he)
# 		_subprocess.run(cmd, stdin=_subprocess.PIPE, shell=True)
# 	else:
# 		args_txt = ''
# 		for key in pos:
# 			args_txt = args_txt + key + ' ' + str(pos[key]) + ' '
# 		cmd = window + ' ' + args_txt
# 		cmd = cmd.rstrip(cmd[-1])
# 		_subprocess.Popen(cmd, shell=True)

def open_window_args(windows, pos=None, noargs=False):
	if noargs == True:
		for window in windows:
			name = window['window']
			_subprocess.Popen(name, shell=True)
		return 0
	if pos == None:
		for window in windows:
			name = window['window']
			args = window['args']
			size = window['size']
			position = window['position']
			x=size[0]
			y=size[1]
			wi=position[0]
			he=position[1]
			w = get_win_info(name)
			if w:
				wid = w[0]['id']
				cmd = "wmctrl -i -r " + wid +  " -e 0," + str(wi) + "," + str(he) + "," + str(x) + "," + str(y)
				_subprocess.Popen(cmd, stdin=_subprocess.PIPE, shell=True)
			else:
				args_txt1 = ' ' + \
					'-x ' + str(x) + ' ' + \
					'-y ' + str(y) + ' '  + \
					'-wi ' + str(wi) + ' ' + \
					'-he ' + str(he)
				cmd = name + ' ' + args_txt1
				if args != None:
					for args_txt2 in args:
						cmd += ' ' + args_txt2
				# print('cmd', cmd)
				_subprocess.Popen(cmd, stdin=_subprocess.PIPE, shell=True)
	else:
		w = get_win_info(windows)
		if w:
			wid = w[0]['id']
			x=pos['-x']
			y=pos['-y']
			wi=pos['-wi']
			he=pos['-he']
			cmd = "wmctrl -i -r " + wid +  " -e 0," + str(x) + "," + str(y) + "," + str(wi) + "," + str(he)
			_subprocess.run(cmd, stdin=_subprocess.PIPE, shell=True)
		else:
			args_txt = ''
			for key in pos:
				args_txt = args_txt + key + ' ' + str(pos[key]) + ' '
			cmd = windows + ' ' + args_txt
			cmd = cmd.rstrip(cmd[-1])
			_subprocess.Popen(cmd, shell=True)


# _wininfo = WinInfoPos(100, 20, 858, 171)
# win_info = _wininfo.info()
# open_window_args('sirius-hla-as-ap-launcher.py', win_info)
# print(get_win_info())
# print(get_computer_name())
# print(build_config())
