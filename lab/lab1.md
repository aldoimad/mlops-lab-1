#Answer to question 1 : 
pyproject.toml: the project settings file (name, version, Python version, list of dependencies).
.python-version: the Python version the project uses.
README.md: the project description (empty at first).
src/: the folder for source code.
uv.lock (appears after uv add): exact versions of all installed libraries.
.venv/: the virtual environment holding the installed libraries.

#Answer to question 2 : 
.dvc/: dvc's internal folder. It holds config (dvc settings, such as the remote), a .gitignore, and later the cache.
.dvc/config: dvc settings such as the remote location.
.dvcignore: like .gitignore, but it lists files dvc should ignore.
All of these should be pushed to git, except the cache and config.local (dvc already tells git to ignore those).

#Answer to question 3 : 
With --global, credentials are stored in a config file in the user's home/profile folder (on Windows, under AppData), outside the repo and shared by all projects.
Other options: --local (stored in .dvc/config.local, which git ignores, only for this repo) and --system (for all users on the machine). Without any flag, the setting goes to .dvc/config, which is committed.
Credentials should never be pushed to GitHub, because anyone who can read the repo could use them.

#Answer to question 4 : 
dvc added the line /data to .gitignore. This tells git to ignore the whole data folder, so the large image files are not stored in git. dvc manages the data instead.

#Answer to question 5 : 
Yes, data.dvc was created. It is a small text file containing the hash (md5) of the data folder, its total size, the number of files, and the path (data). It is the pointer that lets dvc find the exact version of the data.

#Answer to question 6 : 
On GitHub: the code is there, the data is not, and data.dvc is there and points to the data.
DagsHub: I used a local remote, so there is no DagsHub page. The data is in my local dvc-storage folder, stored as hashed files.

#Answer to question 7 :
No, the data folder is not there after cloning. Only data.dvc is present.
The command needed is dvc pull, which downloads the data from the remote.

#Answer to question 8 : 
No. After checking out the old commit and running dvc checkout, food11_processed and food11_processed_mini were gone and only food11_raw remained, because the old data.dvc did not know about them.