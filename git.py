# -*- coding: utf-8 -*-
# git.py

import os
import sys
import subprocess

def isRepo(path):
    return os.path.exists(os.path.join(path, ".git"))
	
def isNBstripoutInstalled():
    out = subprocess.run([sys.executable, "-m", "nbstripout", "--status"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8")
    return len(out) and "not recognized" not in out

def isNBstripoutActivated():
    out = subprocess.run([sys.executable, "-m", "nbstripout", "--status"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8")
    return len(out) and "is installed" in out
	
def checkRepo():
    if not isRepo("."):
        print("Not a GIT repository.")
        return
    # is git installed?
    try:
        import git
    except ImportError:
        print("Could not load git module, is GIT installed and in PATH?")
        return
    # check for nbstripout
#    if not isNBstripoutInstalled():
#        print("nbstripout not found!")
#        print("Please run the 'Anaconda Update Script'.")
#    if not isNBstripoutActivated():
#        print("nbstripout not active in this repo!")
#        print("Jupyter output will be added to GIT (which is bad).")
    # check the repository in detail
    from IPython.display import display, HTML
    repo = git.Repo('.')
#    currentNB = os.path.basename(currentNBpath())
    try:
        editedOn = repo.git.show(no_patch=True, format="%cd, version %h by %cn", date="iso")
    except git.GitCommandError:
        print("Not a GIT repository.")
        return
    editedOn = editedOn.split(', ')
    opacity = 0.3 # 1.0 if repo.is_dirty() else 0.5
    display(HTML('<div style="opacity: {opacity};">'
                 '<h3>Document updated on {}</h3>'
                 '<h4>({})</h4></div>'.format(*editedOn, opacity=opacity)))
    if repo.is_dirty():
        edits = repo.git.diff(stat=True)
        import re
        edits = re.sub(r" (\++)", r' <span style="color: green;">\1</span>', edits)
        edits = re.sub(r"(\+)?(-+)(\s)", r'\1<span style="color: red;">\2</span>\3', edits)
        display(HTML(
            '<div style="border-style: solid; border-color: darkred; border-width: 1px; padding: 0em 1em 1em 1em; margin: 1em 0em;">'
            '<h4 style="color: darkred;">There are changes in this repository:</h4>'
            "<pre>"+edits+"</pre>"
            '</div>'
        ))
    return
    try:
        return [int(num) for num in edits.split()[:2]]
    except:
        pass
    edits = nbModified()
    if edits is not None and len(edits):
        print("{} lines added, {} removed".format(*edits))
    else:
        print("no changes")
