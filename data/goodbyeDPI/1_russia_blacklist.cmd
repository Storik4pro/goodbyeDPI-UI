@ECHO OFF
PUSHD "%~dp0"
set _arch=x86
IF "%PROCESSOR_ARCHITECTURE%"=="AMD64" (set _arch=x86_64)
IF DEFINED PROCESSOR_ARCHITEW6432 (set _arch=x86_64)
PUSHD "%_arch%"

powershell -windowstyle hidden -command "start-process goodbyedpi.exe -ArgumentList '-9 --blacklist ..\russia-blacklist.txt --blacklist ..\russia-youtube.txt' -NoNewWindow"

POPD
POPD
