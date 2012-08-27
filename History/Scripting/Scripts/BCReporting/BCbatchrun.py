import subprocess, os

output = "BCReports"

folder1 = "ASANTEST"
folder2 = "ASANQA1"

process = "BCresults.py"

f1 = []
f2 = []
f3 = []
for file in os.listdir(folder1):
	f1.append(file[:-4])
for file in os.listdir(folder2):
	f2.append(file[:-4])
for file in os.listdir(output):
	f3.append(file[:-4])

if f1 != f3 and f2 != f3:
	for i in range(len(f1)):
		if f1[i] != f3[i]: 
			print f1[i], f2[i], f3[i]
	print "Differences in folders"
	raw_input()
else:
	for file in f3:
		inputfile = os.path.normpath( output + "/" + file + ".txt" )
		outputfile = os.path.normpath( "Reports" + "/" + file + ".txt" )
		command = []
		command.append( "python" )
		command.append( process.strip() )
		command.append( inputfile )
		command.append( outputfile )
		subprocess.call( command )