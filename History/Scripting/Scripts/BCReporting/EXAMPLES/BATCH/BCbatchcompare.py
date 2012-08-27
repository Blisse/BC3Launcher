import subprocess, os

batch = "BCcompare.bat"

exe = "'C:\\Program Files (x86)\\Beyond Compare 3\\BCompare.exe'"
script = "BCscript.txt"

output = "BCReports"

folder1 = "ASANSTAGE"
folder2 = "ASANQA1"

f1 = []
f2 = []
for file in os.listdir(folder1):
	f1.append(file[:-4])
for file in os.listdir(folder2):
	f2.append(file[:-4])
if f1 != f2:
	print "Differences in folders"
	raw_input()
else:
	for file in f1:
		command = []
		command.append(batch)
		command.append(exe)		
		command.append(script)
		command.append(folder1)
		command.append(folder2)
		command.append(file)
		command.append(output)

		subprocess.call(command)
		#raw_input("NEXT >>")