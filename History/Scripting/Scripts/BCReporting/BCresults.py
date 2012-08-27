import sys, os

if len(sys.argv) == 3:
	infilename = sys.argv[1]
	outfilename = sys.argv[2]
else:
	infilename = os.path.normpath( "BCReports/BCReport.txt" )
	outfilename = "Report.txt"

print infilename
print outfilename

def isDate(string):
    x = string.split(" ")
    x = string.split(" ")
    days = ["Monday,", "Tuesday,", "Wednesday,", "Thursday,", "Friday,", "Saturday,", "Sunday",
                "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    months = ["January", "February", "March", "April", "May", "June", "July","August", "September", "October", "November", "December", 
                "janvier", "fvrier", "mars", "avril", "mai", "juin", "juillet", "aot", "septembre", "octobre", "novembre", "dcembre" ]
    if ( ( x[0] in days and x[1] in months ) or ( x[0] in days and x[2] in months ) ):
        return 1
    return 0
    
def get_meta( infile ):
    meta = []
    meta.append( infile.pop(0) )
    meta.append( infile.pop(0) )
    temp = infile.pop(0)
    temp = infile.pop(0)
    temp = infile.pop(0).split()
    if len(temp) == 6:
        meta.append( "O: " + temp[2].split("\\")[-1].rstrip() )
        meta.append( "M: " + temp[5].split("\\")[-1].rstrip() )
    else:
        meta.append( "O: " + temp[2].split("\\")[-1].rstrip() )
        temp = infile.pop(0).split()
        meta.append( "M: " + temp[2].split("\\")[-1].rstrip() )
    return meta, infile

def get_side( line ):
    x = list(line)
    if x[0] == ' ':
        return 1
    return -1
	
def main():
    infile = open(infilename).readlines()
    meta, infile = get_meta( infile )
    output = []
    for line in infile:
        output.append( [ line.split()[0], " ".join(line.split()[1:] ), get_side(line) ] )
    routput = []
    bar = "------------------------------------------------------------------------"
    for i in range( len(output) ):
        if output[i][0] != bar:
            routput.append( output[i] )
    doubles = []
    j = 0
    for i in range( len( routput ) ):
        j = i
        while j < len( routput ):
            if j != i and routput[i][1] == routput[j][1]:
                routput[i][1] = "24164/2&REMOVEDflag=1"
                routput[j][1] = "24164/2&REMOVEDflag=1"
                #doubles.append(routput[i])
                #doubles.append(routput[j])
            j+=1
    for line in routput:
        if line[1] != "24164/2&REMOVEDflag=1":
            doubles.append(line)
        #try:
        #    routput.remove(line)
        #except:
        #    pass
	side = ""
	written = 0
	date = 0
	outfile = open( outfilename , "w")
	outfile.write( meta[0] )
	outfile.write( meta[1] )
	outfile.write( meta[2] + " - " + meta[3] + "\n\n" )
	for line in doubles:
        #if isDate( line[1] ) == 0:
		written = 1
		if line[2] == -1:
			side = meta[2]
		elif line[2] == 1:
			side = meta[3]
		outfile.write( side + ": Line " + line[0] + " - " + line[1] + "\n")
        #else:
        #    date += 1
	if written == 0:
		outfile.write("No differences to report")
    #outfile.write(date + " number of dates excluded.")
    print "Done!\n"

def open_file():
	os.system('notepad.exe ' + outfilename)
	
if __name__=='__main__':
	main()
	#x = raw_input("Open in Notepad? [y/n] >> ")
	#if x.upper() == "Y":
	#	open_file()
