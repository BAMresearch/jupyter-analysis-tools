# -*- coding: utf-8 -*-
# utils.py

import os
import urllib
import json
import ipykernel
from notebook import notebookapp
import locale

def currentNBpath():
    """Returns the absolute path of the Notebook or None if it cannot be determined
    NOTE: works only when the security is token-based or there is also no password
    """
    connection_file = os.path.basename(ipykernel.get_connection_file())
    kernel_id = connection_file.split('-', 1)[1].split('.')[0]

    for srv in notebookapp.list_running_servers():
        try:
            if srv['token']=='' and not srv['password']:  # No token and no password, ahem...
                req = urllib.request.urlopen(srv['url']+'api/sessions')
            else:
                req = urllib.request.urlopen(srv['url']+'api/sessions?token='+srv['token'])
            sessions = json.load(req)
            for sess in sessions:
                if sess['kernel']['id'] == kernel_id:
                    return os.path.join(srv['notebook_dir'],sess['notebook']['path'])
        except:
            pass  # There may be stale entries in the runtime directory 
    return None

def setLocaleUTF8():
    """Fix the Jupyter locale which is not UTF-8 by default on some systems (older Windows?)."""
    locOld = locale.getpreferredencoding(False).lower()
    def getpreferredencoding(do_setlocale = True):
        return "utf-8"
    locale.getpreferredencoding = getpreferredencoding
    locNew = locale.getpreferredencoding(False)
    if locOld != locNew:
        print(f"Updated locale from {locOld} -> {locNew}.")
