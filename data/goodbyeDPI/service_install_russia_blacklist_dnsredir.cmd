:: Licensed under the Apache License, Version 2.0 (the "License");
:: you may not use this file except in compliance with the License.
:: You may obtain a copy of the License at
::
::     http://www.apache.org/licenses/LICENSE-2.0
::
:: Unless required by applicable law or agreed to in writing, software
:: distributed under the License is distributed on an "AS IS" BASIS,
:: WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
:: See the License for the specific language governing permissions and
:: limitations under the License.
@ECHO OFF
PUSHD "%~dp0"
set _arch=x86
IF "%PROCESSOR_ARCHITECTURE%"=="AMD64" (set _arch=x86_64)
IF DEFINED PROCESSOR_ARCHITEW6432 (set _arch=x86_64)

echo This script should be run with administrator privileges.
echo Right click - run as administrator.
echo Press any key if you're running it as administrator.
pause
sc stop "GoodbyeDPI"
sc delete "GoodbyeDPI"
sc create "GoodbyeDPI" binPath= "\"%CD%\%_arch%\goodbyedpi.exe\" -9 --dns-addr 77.88.8.8 --dns-port 1253 --dnsv6-addr 2a02:6b8::feed:0ff --dnsv6-port 1253 --blacklist \"%CD%\russia-blacklist.txt\" --blacklist \"%CD%\russia-youtube.txt\"" start= "auto"
sc description "GoodbyeDPI" "Passive Deep Packet Inspection blocker and Active DPI circumvention utility"
sc start "GoodbyeDPI"

POPD
