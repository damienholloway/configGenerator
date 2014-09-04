  

## Summary
Running this script will take input file with variables in <#this#> format
and perform substitution basedon variables stored in a .csv file. A new file will be
created per row in the CSV file.

#Usage

    configGen.py [-h | -i <inputConfigFile> -c <inputCSVFile> -o <outputdir> [-s <singleOutputFileName>]]

##Applications:
Most useful is a case where you need to provide customised configuration for a large number
of devices based on a template. A good example is the base configuration on each router, including
upstream interfaces, which would be stored in a seperate file per device/row in the CSV file

Alternatively if there is a large number of 'customer' interfaces, VRF's or routing instances
these can be replicated in a consistent way. Use the -s option for all output to a single file.

Unfortunately, with the simple syntax, these use cases cannot be mixed, but could be performed
sequentially.

##Where:
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

###Options:
    -h            Show this help.
    -s            Send output to a single file, as opposed to multiple files

  
##Example: Normal operation;
  
    configGen.py -i junosTemplate.txt -c junosTemplate.csv -o customerDirectory
    
