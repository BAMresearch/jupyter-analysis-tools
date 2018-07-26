@echo off
set AP=%LOCALAPPDATA%\Continuum\Anaconda3
if not exist %AP% set AP=%USERPROFILE%\Anaconda3
set WD=%CD%
if exist "%*" call :getParentPath WD %*
%AP%\python.exe %AP%\cwp.py %AP% %AP%\python.exe %AP%\Scripts\jupyter-notebook-script.py --notebook-dir="%WD:\=/%" %*
:getParentPath <resultVar> <pathVar>
(
    set "%~1=%~dp2"
    exit /b
)
