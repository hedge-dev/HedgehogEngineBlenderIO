@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=source
set BUILDDIR=build

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 goto sphinx_python
goto sphinx_ok

:sphinx_python

set SPHINXBUILD=python -m sphinx.__init__
%SPHINXBUILD% 2> nul
if errorlevel 9009 (
	echo.
	echo The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo installed, then set the SPHINXBUILD environment variable to point
	echo to the full path of the 'sphinx-build' executable. Alternatively you
	echo may add the Sphinx directory to PATH.
	echo.
	echo If you don't have Sphinx installed, grab it from
	echo http://sphinx-doc.org/
	rem Exit with errorlevel 1
	popd
	exit /b 1
)

:sphinx_ok

REM Default to livehtml
if "%1" == "" (
	goto livehtml
)

if "%1" == "help" (
	%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
	goto EOF
)

if "%1" == "livehtml" (
	:livehtml
	sphinx-autobuild --open-browser --delay 0 "%SOURCEDIR%" "%BUILDDIR%\html" %SPHINXOPTS% %O%
	if errorlevel 1 (
		popd
		exit /b 1
	)
	goto EOF
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:EOF
popd
