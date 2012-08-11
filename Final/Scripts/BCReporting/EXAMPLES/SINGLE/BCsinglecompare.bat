@echo off
set exe=C:\Program Files (x86)\Beyond Compare 3\BCompare.exe
set script=BCscript.txt

set file1=001qa1.pdf
set file2=001stage.pdf
::alternatively, move the files to another folder and use
::set file1=ASANQA1\001qa1.pdf
::set file2=ASANSTAGE\001stage.pdf
set output=BCReports\BCReport.txt
echo running...
"%exe%" @"%script%" "%file1%" "%file2%" "%output%"