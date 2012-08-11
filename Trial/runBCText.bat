set exe="C:/Program Files (x86)/Beyond Compare 3/BCompare.exe"
set script=%4
set file1=%1
set file2=%2
set output=%3
echo running...
%exe% @%script% "%file1%" "%file2%" "%output%"