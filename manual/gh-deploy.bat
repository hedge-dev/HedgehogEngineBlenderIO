@echo off

setlocal
:PROMPT
SET /P AREYOUSURE=Do you want to deploy the manual to github pages (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO END

call make.bat html
python .\build_files\utils\sphinx_gh_deploy.py

:END
endlocal