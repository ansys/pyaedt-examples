@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXOPTS%" == "" (
	set SPHINXOPTS=-j auto --color -W
)
if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=source
set BUILDDIR=_build
set LINKCHECKDIR=\%BUILDDIR%\linkcheck
set LINKCHECKOPTS=-d %BUILDDIR%\.doctrees -W --keep-going --color

REM This LOCs are used to uninstall and install specific package(s) during CI/CD
for /f %%i in ('pip freeze ^| findstr /c:"vtk-osmesa"') do set is_vtk_osmesa_installed=%%i
if NOT "%is_vtk_osmesa_installed%" == "vtk-osmesa" if "%ON_CI%" == "true" (
	@ECHO ON
	echo "Removing vtk to avoid conflicts with vtk-osmesa"
	@ECHO OFF
	pip uninstall --yes vtk
	@ECHO ON
	echo "Installing vtk-osmesa"
	@ECHO OFF
	pip install --extra-index-url https://wheels.vtk.org vtk-osmesa)
for /f %%i in ('pip freeze ^| findstr /c:"pypandoc_binary"') do set is_pypandoc_binary_installed=%%i
if NOT "%is_pypandoc_binary_installed%" == "pypandoc_binary" if "%ON_CI%" == "true" (
	@ECHO ON
	echo "Removing pypandoc to avoid conflicts with pypandoc-binary"
	@ECHO OFF
	pip uninstall --yes pypandoc
	@ECHO ON
	echo "Installing pypandoc-binary"
	@ECHO OFF
	pip install pypandoc-binary==1.13)
REM End of CICD dedicated setup

if "%1" == "" goto help
if "%1" == "clean" goto clean
if "%1" == "html" goto html
if "%1" == "pdf" goto pdf

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.https://sphinx-doc.org/
	exit /b 1
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:clean
echo Cleaning everything
rmdir /s /q %SOURCEDIR%\examples > /NUL 2>&1 
rmdir /s /q %BUILDDIR% > /NUL 2>&1
goto end

:html
echo Building HTML pages with running examples
REM %SPHINXBUILD% -M linkcheck %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %LINKCHECKOPTS% %O%
%SPHINXBUILD% -M html %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
echo "HTML build finished."
goto end

:pdf
%SPHINXBUILD% -M latex %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
cd "%BUILDDIR%\latex"
for %%f in (*.tex) do (
xelatex "%%f" --interaction=nonstopmode)
if NOT EXIST pyaedt-examples.pdf (
	Echo "PDF file not generated!"
	exit /b 1)
Echo "PDF file generated!"
goto end 	

:end
popd
