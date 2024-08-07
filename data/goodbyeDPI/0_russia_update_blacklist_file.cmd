@ECHO OFF
PUSHD "%~dp0"
powershell -windowstyle hidden -command "bitsadmin /transfer blacklist https://p.thenewone.lol/domains-export.txt '%CD%\russia-blacklist.txt'"
POPD
