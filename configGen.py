#!/usr/bin/python
#################################################################################################
#
# Damien Holloway 20140904
#
# For help file and usage instructions type
#   python scriptName.py -h
#

import time  # include time module, to allow tracking of script execution time
import re    # Regular expressions module
import csv   # Support for CSV files
import sys   # support for command line arguments
import getopt   # allows options on cli, like usage:myScript -i inputfile -o outputfile 

#################################################################################################
#
# Stuff you may want to change
#

# compile the regular expression that will be used. Do it outside the function, so it's done once. Saves some CPU.
var = re.compile('<#\s?([\w,\-]+)\s?#>') # look for up to one space either side of the word, matches forst instance on a line

#################################################################################################
#
# Probably don't need to change anything below here
#

# Global variables
matchLines = 0
countLines = 0
filesCreated = 0
singleFile = False      # default is to write output to a seperate file per row in the CSV


#################################################################################################
#
# getOptions
#
# DESCRIPTION
# -----------
#
# Process CLI arguments and shows help if not complete
# Returns: Nothing, but sets input variables globally
# 
def getOptions(argv):
   global myConfigFileName
   global myCSVFileName 
   global myOutputDir
   global mySingleFileName
   global singleFile
   
   try:
      opts, args = getopt.getopt(argv,"hs:i:c:o:",["iFile=","cFile=","oDir=","sFile="])
   except getopt.GetoptError:
      printUsage()
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         printUsage() # 'test.py -i <inputfile> -o <outputfile>'
         sys.exit()
      elif opt in ("-i", "--iFile"):
         myConfigFileName = arg
      elif opt in ("-c", "--cFile"):
         myCSVFileName = arg
      elif opt in ("-o", "--oDir"):
         myOutputDir = arg
      elif opt in ("-s", "--sFile"):
         singleFile = True
         mySingleFileName = arg
   #print 'Input Config file is ./' + myConfigFileName
   #print 'Input CSV file is ./' + myCSVFileName
   #print 'Output directory is ./' + myOutputDir

#################################################################################################
#
# printUsage
#
# DESCRIPTION
# -----------
#
# PPrint a help file, keeping here seperate makes the logic more readable in other parts of the script
# Returns: Nothing
#
def printUsage():
    a=1
    usage = """
                   Config Generator V   
                   -------------------

"""
    usage += __file__ + """ [-h | -i <inputConfigFile> -c <inputCSVFile> -o <outputdir> [-s <singleOutputFileName>]]

Running this script will take input file with variables in <#this#> format
and perform substitution basedon variables stored in a .csv file. A new file will be
created per row in the CSV file.

Applications:
Most useful is a case where you need to provide customised configuration for a large number
of devices based on a template. A good example is the base configuration on each router, including
upstream interfaces, which would be stored in a seperate file per device/row in the CSV file

Alternatively if there is a large number of 'customer' interfaces, VRF's or routing instances
these can be replicated in a consistent way. Use the -s option for all output to a single file.

Unfortunately, with the simple syntax, these use cases cannot be mixed, but could be performed
sequentially.

Where:
  <inputConfigFile>         Template configuration file in any format as long as the vars are uniquely
                            wraped in <#these#> delimiters
  
  <inputCSVFile>            CSV file (ie excel) where the first row is a header row with variable names,
                            variables are made from characters, numbers and underscore only [a-zA-Z0-9_]+
                            No spaces in the variable names are permitted. The first column must have unique
                            values as it is used to generate a unique filename. Best practice is to use HOSTNAME
                            as first column. Unless the singleOutputFileName option is selected ('-s'). 
  
  <outputdir>               Output directory relative to current path, it must already exist

  <singleOutputFileName>    Output filename, when all config should be written to a single file and not
                            a file per row

Options:
  -h            Show this help.
  -s            Send output to a single file, as opposed to multiple files

  
Example: Normal operation;
  
  """ 
    
    usage += __file__ + """ -i junosTemplate.txt -c junosTemplate.csv -o customerDirectory
    
Questions or comments send to Damien holloway@juniper.net
  
     """
    print usage



#################################################################################################
#
# findVar
#
# DESCRIPTION
# -----------
#
# Takes a string and pulls out and changes any 'variables' as defined by the regular expression
# Returns: The original string with changes. It is recursive so more than one variable can exist in a line 
# Example:
#                "scp://<#archive_username#>@<# ARCHIVE_IP #>/<#DIR#>/" password "<#PASSWORD#>";
#    becomes
#                "scp://myUserName@192.1.1.1/myDir/" password "myPassword"; 
#
def findVar(string):
    global matchLines               # declare that we are using the global variable
    newString = ""
    
    match = var.search(string)
    
    # if there is a variable
    if match :
        matchLines += 1
        leftString = match.string[match.pos:match.start()]
        matchString = "{{"+match.group(1)+"}}"                  # this is the variable, later we will do a lookup and replace this value
        
        matchString = eachRow[match.group(1)]
        
        rightString = match.string[match.end():match.endpos ]
        
        # since we check from the left, everything to the left is OK, ie has not variables to be substituted
        newString = leftString + matchString
        
        #if there are more variables
        match = var.search(rightString)
        
        #recursively check the right of the remaining string
        if match :
            newString += findVar(rightString)
        else:
            newString += rightString        # no variables to the right, so append
        #print newString
    else:                                   #no variables in string at all, so return the whole thing
        newString += string
    
    return newString

#####################################################################################################
#
# main program below
#

# process command line arguments
#if __name__ == "__main__":
getOptions(sys.argv[1:]) #send all CLI parameters, excluding filename, to process options
#print "name", __name___


print
print "###########################################################################"
print "#                                                                         #"
print "#                        Config Generator V1.0                            #"
print "#                                                                         #"
print "###########################################################################"

# I like to check how long process is taking
startTime = time.clock()

#
# Open Both Config and CSV files
#

# Open a file in read-only mode, which is default anyway
myConfig = open(myConfigFileName, "r")
print "Opening File: ./" + myConfig.name #," in", myConfig.mode, "mode"

# open CSV file
myCSV = open(myCSVFileName, "rU")
myCSVRows = csv.DictReader(myCSV)
print "Opening CSV File: ./" + myCSV.name#,"' in", myCSV.mode, "mode"

if singleFile == True:
    myOutputFileName = myOutputDir
    myOutputFileName += "/" + mySingleFileName
    myOutput = open(myOutputFileName, "w") # Open the file where we will write the result
    filesCreated += 1
    print "Created Single Config:", myOutputFileName
    
for eachRow in myCSVRows:
    #reset Counters
    countLines = 0
    matchLines = 0
    
    # Build output filename if not using singleFile
    if singleFile == False:
        myOutputFileName = myOutputDir
        myOutputFileName += "/" + eachRow[myCSVRows.fieldnames[0]]  # assumed first column has HOSTNAME or some other unique name, if it's not unique files will write over each other
        myOutputFileName += "-config.txt"
    
        # Open write file
        # Will throw an error if dir does not exist
        myOutput = open(myOutputFileName, "w") # Open the file where we will write the result
        filesCreated += 1
    for myLine in myConfig:
        countLines += 1
        newLine = findVar(myLine);
        myOutput.write(newLine)
    
    
    if singleFile == False:
        print "Created Config: ./" + myOutputFileName
        myOutput.close()  # close outputfile
    myConfig.seek(0)  # reset the config file position pointer to start...(This is needed/wierd in python, so much for local variables!! Grrr!!!)
    
#######################################################################################################
#
# Finished now, just wrap things up, like close open files and report stats
#
print
print "###########################################################################"
print "#"
print "#                                Report"
print "#"
print "Variables Substituted per template = ", matchLines
print "Total Lines in Template = ", countLines
print "Total Files Created = ", filesCreated

#print "CSV file has", myCSVRows.line_num -1, "records"

#clean up before exit
#print "Closing Files:"
myConfig.close()
myCSV.close()

duration = time.clock() - startTime
print "Script took", duration * 1000, "ms to complete\n"





