# upgrade_venv
Discover, freeze and rebuild venvs to preserve them when installing a new Python release (e.g. Python 3.7 --> Python 3.8)

## Important!

**This script has not been thoroughly tested! Use it at your own risk!!!**

## Description

The purpose of this script is to automatically:

 - discover venvs/virtualenvs that exist in your system
 - backup their configuration, i.e. freeze their requirements in
   a `requirements.txt` file located outside the venv itself
 - rebuild venvs from the backed up `requirements.txt` files
 
The main use case is dealing with a minor Python upgrade, e.g. from
Python 3.7 to Python 3.8 with a rolling release Linux distribution
such as Manjaro Linux or Arch.

__WARNING__: this script will always build venvs, not virtualenvs, even
if the backed up thing was a virtualenv.
In some cases this is not what you want. For example, pipenv manages
virtualenv but is not able to manage venvs. Be sure to remove virtualenvs
thay you do not want to rebuild as venvs, as explained below.

Here is the intended usage recipe:

## Before upgrading to Python 3.8

 1. __Important:__ edit script configuration. Specify the list of directories
    where venvs will be looked for, and the directory where your requirements
    will be backed up. Search is recursive
    
 2. Run:
    ```python upgrade_venv.py freeze```
 
 3. Review your destination directory. You will find a copy of your filesystem
    structure, populated only with venv folders and requirements.txt files.
    You can delete folders corresponding to venvs/virtualenvs that
    you do not want to rebuild later
    
## After upgrading to Python 3.8

 4. Run:
    ```python upgrade_venv.py rebuild```
    The script will archive the old content of your venvs (such as directories
    `bin`, `lib`, `include`) in a subdirectory `venv_archive` of each venv.
    Then it will create a new venv and reinstall requirements using `pip`
    
 5. Inspect and test your venvs to make sure that they work as intended
 
 6. If you really wish to remove your old archived venv stuff, run:
    ```python upgrade_venv.py cleanup```
