@echo off
set exe=C:\\Program Files (x86)\\Beyond Compare 3\\BCompare.exe
set script=%2


set folder1=%3
set folder2=%4

set filename=%5
::set file1=ASANTEST\60.pdf
::set file2=ASANQA1\60.pdf

set output=%6\%5.txt

set file1=%folder1%\%filename%.pdf
set file2=%folder2%\%filename%.pdf

echo %filename%

echo running...

"%exe%" @"%script%" "%file1%" "%file2%" "%output%"


