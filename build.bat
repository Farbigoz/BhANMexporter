
set PYTHON_FILE=run
set OUT_EXE_FILE=ANM Exporter
set PYTHON_DIR=C:\Python38

call "%ProgramFiles(x86)%\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" x64

"%PYTHON_DIR%\python.exe" -m pip install cython
"%PYTHON_DIR%\python.exe" -m cython --embed -3 "%PYTHON_FILE%.py" --cplus
cl.exe /nologo /Ox /MD /W3 /GS- /DNDEBUG -I"%PYTHON_DIR%\include" /Tp"%PYTHON_FILE%.cpp" /link /DYNAMICBASE "kernel32.lib" /OUT:"%OUT_EXE_FILE%.exe" /SUBSYSTEM:CONSOLE /LIBPATH:"%PYTHON_DIR%\libs"
