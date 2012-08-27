@echo off
set exe=C:\Program Files (x86)\Beyond Compare 3\BCompare.exe
set script=BCscript.txt
set file1=ASANQA1\31.pdf
set file2=ASANTEST\31.pdf
set output=BCReports\BCReport.txt
echo running...
"%exe%" @"%script%" "%file1%" "%file2%" "%output%"  
