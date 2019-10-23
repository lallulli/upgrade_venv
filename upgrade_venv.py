import os
import subprocess
import traceback
import shutil
import sys

"""
Freeze venv requirements, in order to rebuild them later.

The purpose of this script is to automatically:

 - discover venvs/virtualenvs that exist in your system
 - backup their configuration, i.e. freeze their requirements in
   a requirements.txt file located outside the venv itself
 - rebuild venvs from the backed up requirements.txt
 
The main use case is dealing with a minor Python upgrade, e.g. from
Python 3.7 to Python 3.8.

WARNING: this script will always rebuild venvs, not virtualenvs.
In some cases this is not what you want. For example, pipenv manages
virtualenv but not venvs.
If you do not exclude virtualenvs, they will be rebuilt as venvs.

Here is the intended usage recipe:

Before upgrading to Python 3.8
------------------------------

 1. (Important!) Edit script configuration: specify the list of directories
    where venvs will be looked for, and the directory where your requirements
    will be backed up. Search is recursive.
    
 2. Run:
    python upgrade_venv.py freeze
 
 3. Review your destination directory. You will find a copy of your filesystem
    structure, populated only with venv folders and requirements.txt files.
    You can delete venv folders if you do not want to rebuild them later
    
After upgrading to Python 3.8
-----------------------------

 4. Run:
    python upgrade_venv.py rebuild
    The script will archive the old content of your venvs (such as directories
    'bin', 'lib', 'include') in a subdirectory 'venv_archive'.
    Then it will create a new venv and reinstall requirements using pip.
    
 5. Inspect and test your venvs to make sure that they work as intended
 
 6. If you really wish to remove your old archived venvs, run:
    python upgrade_venv.py cleanup
 """


# List of absolute paths where venv are looked for (without trailing slash)
BASE_PATHS = [
	'/home/luca/Documents',
]
# Path where requirements will be backed up
TARGET_PATH = '.'


TEST_FOR_BIN = {'python3', 'pip', 'pip3.7', 'easy_install', 'activate'}
VENV_STUFF = ['bin', 'include', 'lib', 'lib64', 'pyvenv.cfg']
ARCHIVE_DIR = 'venv_archive'


def filewalk(path, callback_file=None, callback_dir=None, process_file_links=True, process_dir_links=False):
	"""
	For every file and directory call callback

	:param path: base path
	:param callback_file: function with params: dir, sub
	:param callback_dir: function with params: dir, sub
	:return:
	"""
	try:
		content = os.listdir(path)
	except:
		return
	for f in content:
		f_path = os.path.join(path, f)
		if os.path.isdir(f_path) and (process_dir_links or not os.path.islink(f_path)):
			if callback_dir is not None:
				callback_dir(path, f)
			filewalk(f_path, callback_file, callback_dir)
		elif callback_file is not None and (process_file_links or not os.path.islink(f_path)):
				callback_file(path, f)


def create_dir_if_not_existing(path, recurse=False):
	path = os.path.abspath(path)
	if not os.path.exists(path):
		parent, sub = os.path.split(path)
		if recurse and not os.path.exists(parent):
			create_dir_if_not_existing(parent, recurse)
		os.mkdir(path)


def get_spare_filename(path, filename):
	"""
	If filename exists in path, attaches a suffix _<n> to its name (just before extension)

	:param path: path where filename is looked for
	:return: new filename
	"""
	filepath = os.path.join(path, filename)
	if not os.path.exists(filepath):
		return filename

	base, ext = os.path.splitext(filepath)
	i = 1
	while True:
		if not os.path.exists("{}_{}{}".format(base, i, ext)):
			name, ext = os.path.splitext(filename)
			return "{}_{}{}".format(name, i, ext)
		i += 1


def cleanup_archive(venv_path):
	archive_path = os.path.join(venv_path, ARCHIVE_DIR)
	print(archive_path)
	try:
		shutil.rmtree(archive_path)
	except:
		pass


def cleaner(venv, requirements):
	if requirements != 'requirements.txt':
		return
	venv_path = venv[len(TARGET_PATH):]
	cleanup_archive(venv_path)


def archive_venv(path):
	archive_path = os.path.join(path, get_spare_filename(path, ARCHIVE_DIR))
	create_dir_if_not_existing(archive_path)
	for v in VENV_STUFF:
		try:
			shutil.move(os.path.join(path, v), archive_path)
		except:
			pass


def rebuilder(venv, requirements):
	if requirements != 'requirements.txt':
		return
	venv_path = venv[len(TARGET_PATH):]
	print(venv_path)
	archive_venv(venv_path)
	print("  Creating venv")
	subprocess.run(['python', '-m', 'venv', venv_path])
	print("  Installing requirements")
	pip = os.path.join(venv_path, 'bin', 'pip')
	requirements_path = os.path.join(venv, requirements)
	subprocess.run([pip, 'install', '-r', requirements_path])
	print("\n")


def freezer(base, bin):
	if bin != 'bin':
		return
	content = set(os.listdir(os.path.join(base, bin)))
	if TEST_FOR_BIN.intersection(content) != TEST_FOR_BIN:
		return
	print(base)
	pip = os.path.join(base, bin, 'pip')
	try:
		res = subprocess.run([pip, 'freeze'], capture_output=True)
	except:
		traceback.print_exc()
		return
	if res.returncode != 0:
		print(res.stderr.decode('utf-8'))
		return
	target = os.path.join(TARGET_PATH, base[1:])
	create_dir_if_not_existing(target, True)
	with open(os.path.join(target, 'requirements.txt'), 'wb') as w:
		w.write(res.stdout)


def cleanup():
	filewalk(TARGET_PATH, cleaner)


def rebuild():
	filewalk(TARGET_PATH, rebuilder)


def freeze():
	for b in BASE_PATHS:
		filewalk(b, callback_dir=freezer)


def show_usage():
	print("USAGE: python upgrade_venv.py (freeze | rebuild | cleanup)")


if __name__ == '__main__':
	if len(sys.argv) != 2:
		show_usage()
	else:
		cmd = sys.argv[1]
		if cmd == 'freeze':
			freeze()
		elif cmd == 'rebuild':
			rebuild()
		elif cmd == 'cleanup':
			cleanup()
		else:
			show_usage()
