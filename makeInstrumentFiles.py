#!/usr/bin/env python

import os
import sys
import argparse
import string
import re
import numpy as np
from astropy.table import Table 
from astropy.io import ascii
from astropy.io.ascii import masked



def printerr(str):
  print ('ERROR: ' + str)
  exit(1)


global args


output_dd_FOR_DB = ''
output_dd_FOR_DISK = ''

prog_description = "Read a tab-delimited version of a KOA instrument keyword table, and generate any/all of the following: dbIngest keyword table; SQL database table creation script; data dictionary files (for disk/database); rows to add to TAP DD "

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=prog_description)

## Optional args:
parser.add_argument("-d", action='store_true', default=False, dest='debug', help='Turn on debugging')
parser.add_argument("-kw", action='store', default='', dest='output_kw', help='Output Keyword Table (dbIngest style)')
parser.add_argument("-dd", action='store', default='', dest='output_dd', help='Prefix for disk/database DD Tables')
parser.add_argument("-tap", action='store', default='', dest='output_tap', help='Output TAP Table')
parser.add_argument("-db", action='store', default='', dest='output_db', help='Output DB Creation Script')

## Positional args:
parser.add_argument("input_tab_file", type=str, help="Input tab-delimited file")
parser.add_argument("table_name", type=str, help="table name (ie koa_nirspec_v4)")

args = parser.parse_args()

input_file            = args.input_tab_file
output_kw             = args.output_kw
output_dd_FOR_DB      = args.output_dd + '.for_database'
output_dd_FOR_DISK    = args.output_dd + '.for_disk'
output_tap            = args.output_tap
output_db             = args.output_db
table_name            = args.table_name.upper()
debug                 = args.debug

if (output_kw == '' and args.output_dd == '' and output_tap == '' and output_db == ''):
  printerr("Must select at least one type of output table (Keyword, DD, DB, TAP)")
  

if debug:
  print ("input_file = %s" % input_file )
  print ("output_dd_FOR_DB = %s" % output_dd_FOR_DB)
  print ("output_dd_FOR_DISK = %s" % output_dd_FOR_DISK)
  print ("output_kw = %s" % output_kw )
  print ("output_tap = %s" % output_kw )
  print ("output_db = %s" % output_kw )


# Read the input table: a tab-delimited ASCII version of the Excel / Google Sheets master table 
try:
  input_t = Table.read(input_file, format='ascii.tab')
except:
  printerr ("Unable to read " + input_file + " - confirm valid tab-delimited table and no binary characters in content")

input_nrows = len(input_t)
if debug:
  print ("input_nrows = ", input_nrows)

#
# Do some replacements for commonly known issues before we really get going:
#






######
# FIRST: dbIngest-style  keyword table - ie KOA_HIRES_Keywords.tbl
#
#
# Keyword table is simple: just an IPAC version of the original but with 
# no spaces in the column headers and a few less columns.
# 
#####

# Prep the table structure
output_kw_t = Table([input_t['DBKeyword'], 
                    input_t['Description'], 
                    input_t['MetadataDatatype'], 
                    input_t['Units'], 
                    input_t['NullsAllowed'], 
                    input_t['DBDatatype'], 
                    input_t['ValidateFormat'], 
                    input_t['CheckValues'], 
                    input_t['MinValue'], 
                    input_t['MaxValue'], 
                    input_t['DiscreteValues']])

# Instead of 'null' nulls, we just want blanks in the keyword table:
fill = [(masked, ' ', 'Description'), (masked, ' ', 'units'), (masked, ' ', 'description'),(masked, ' ', 'Unit'), (masked, ' ', 'mincol'), (masked, ' ', 'maxcol'), (masked, ' ', 'discretevalcol')]

print(input_t['DBKeyword'][0])
print(input_t['DBKeyword'][1])

# Output Keyword table if requested
if (output_kw != ''):
  try:
    ascii.write( output_kw_t, output_kw, format='ipac', fast_writer=False, overwrite=True, fill_values=fill )
  except:
    printerr("Unable to write to: " + output_kw)



######
# SECOND: Initialize DD Table structure

# We will need the DD Table structure whether or not we are actually
# outputting DD files - SQL script, for instance, relies on some of this
#
# This lets us set all the data types and widths as per the canonical spreadsheet,
# instead of relying on dbin to do it for us

dd_col_names = ('cntr', 'name', 'original_name', 'description', 'units', 'intype', 'format', 'dbtype', 'nulls', 'tableflg', 'groupid', 'irsadef', 'sel', 'indx', 'label')
dd_col_types = ('i4', 'S12', 'S12', 'S80', 'S20', 'S20', 'S10', 'S20', 'S6', 'i4', 'S6', 'S6', 'S6', 'S6', 'S12')
  
output_dd_t = Table(names=dd_col_names, dtype=dd_col_types)

# Initialize SQL script if requested
if (output_db != ''):
  try:
    db = open(output_db, "w+")
  except:
    printerr ("Unable to write " + output_db)
  db.write("CREATE TABLE \"" + table_name + "\"\n")
  db.write("  (\n")

# Loop over the rows and generate correct DD contents and SQL script names/types

has_ra_dec = 0
for i in range(input_nrows):
    output_dd_type = input_t['MetadataDatatype'][i].lower()
    output_dd_format = input_t['OutputFormat'][i].lower()

    # Database script 
    if (output_db != ''):
      db.write("    \"" + input_t['DBKeyword'][i].strip().upper() + "\" " + input_t['DBDatatype'][i] + ",\n");

    # Table structure
    output_dd_t.add_row([i+1,                                     #cntr
                         input_t['DBKeyword'][i], #name
                         input_t['DBKeyword'][i],                   #original_name
                         input_t['Description'][i],               #description
                         input_t['Units'][i],                      #units
                         output_dd_type,                          #intype
                         output_dd_format,                        #format
                         input_t['DBDatatype'][i],              #dbtype
                         input_t['NullsAllowed'][i],             #nulls
                         '2',                                     #tableflg
                         i+1,                                     #groupid
                         'y',                                     #irsadef
                         'y',                                     #sel
                         'n',                                     #indx
                         input_t['DBKeyword'][i]])                  #label



# Add the IPAC-only rows to the data dictionary table (both versions):

input_nrows = input_nrows +1
output_dd_t.add_row([input_nrows, 'CRA', 'CRA', 'Original character string RA before conversion to Eq2000', 'null', 'char', '11s', 'varchar2(11)', 'y', '2', input_nrows, 'y', 'y', 'n', 'CRA'])

input_nrows = input_nrows +1
output_dd_t.add_row([input_nrows, 'CDEC', 'CDEC', 'Original character string DEC before conversion to Eq2000', 'null', 'char', '11s', 'varchar2(11)', 'y', '2', input_nrows, 'y', 'y', 'n', 'CDEC'])

if ("hires" in table_name.lower()):
  input_nrows = input_nrows +1
  output_dd_t.add_row([input_nrows, 'HA_D', 'HA_D', 'Original HA in decimal before conversion to sexagesimal', 'null', 'double', '12.6s', 'float(126)', 'y', '2', input_nrows, 'y', 'y', 'n', 'HA_D'])

input_nrows = input_nrows +1
output_dd_t.add_row([input_nrows, 'UTDATETIME', 'UTDATETIME', 'Combined DATE_OBS and UT as a timestamp', 'null', 'char', '11s', 'timestamp', 'y', '2', input_nrows, 'y', 'y', 'n', 'UTDATETIME'])


input_nrows = input_nrows +1
if ("hires" in table_name.lower()):
  output_dd_t.add_row([input_nrows, 'MD_INGTIME', 'MD_INGTIME', 'Time of metadata ingestion', 'null', 'char', '19.19s', 'timestamp', 'y', '2', input_nrows, 'y', 'y', 'n', 'L0_INGTIME'])
  output_dd_t.add_row([input_nrows, 'DVD_INGTIME', 'DVD_INGTIME', 'Time of metadata ingestion', 'null', 'char', '19.19s', 'timestamp', 'y', '2', input_nrows, 'y', 'y', 'n', 'DVD_INGTIME'])
else:
  output_dd_t.add_row([input_nrows, 'L0_INGTIME', 'L0_INGTIME', 'Time of metadata ingestion', 'null', 'char', '19.19s', 'timestamp', 'y', '2', input_nrows, 'y', 'y', 'n', 'L0_INGTIME'])


input_nrows = input_nrows +1
output_dd_t.add_row([input_nrows, 'FILEHAND', 'FILEHAND', 'Path to file in the archive', 'null', 'char', '151s', 'varchar2(151)', 'y', '2', input_nrows, 'y', 'y', 'n', 'FILEHAND'])

input_nrows = input_nrows +1
output_dd_t.add_row([input_nrows, 'FILEURL', 'FILEURL', 'URL to file in the archive', 'null', 'char', '151s', 'varchar2(151)', 'y', '2', input_nrows, 'y', 'y', 'n', 'FILEURL'])

input_nrows = input_nrows +1
output_dd_t.add_row([input_nrows, 'SEMID', 'SEMID', 'SEMESTER and PROGID', 'null', 'char', '11.11s', 'varchar2(11)', 'y', '2', input_nrows, 'y', 'y', 'n', 'SEMID'])


# Output the disk-version (that dbIngest will use for dbin)
if (output_dd_FOR_DISK != ''):
  ascii.write( output_dd_t, output_dd_FOR_DISK + '.tmp', format='ipac', fast_writer=False, overwrite=True, fill_values=fill)

# Fix 0.0 null value bug for description/unit fields 
fixme_t = Table.read(output_dd_FOR_DISK + '.tmp', format='ipac')
for r in range(len(fixme_t)):
  if (fixme_t['description'][r] == '0.0'):
    fixme_t['description'][r] = ''
  if (fixme_t['units'][r] == '0.0'):
    fixme_t['units'][r] = ''
ascii.write(fixme_t, output_dd_FOR_DISK + '.tmp2', format='ipac', fast_writer=False, overwrite=True)

# Make a version with the header
try:
  input_dd = open(output_dd_FOR_DISK + '.tmp2', "r")
except:
  printerr ("Unable to read DD")

output_dd = open(output_dd_FOR_DISK, "w")
output_dd.write("\\fixlen = T\n")
output_dd.write("\\alias = none\n")
output_dd.write("\\longitude = RA2000\n")
output_dd.write("\\latitude = DEC2000\n")
output_dd.write("\\primary = cntr\n")
output_dd.write("\\spt_ind = spt_ind\n")
output_dd.write("\\x = x\n")
output_dd.write("\\y = y\n")
output_dd.write("\\z = z\n")
for line in input_dd:
  output_dd.write(line)
output_dd.close()

# DONE with disk version

# For database version: add the DD database rows

# Gotta have RA/DEC rows that mimic RA2000/DEC2000, for isisql select as purposes:
if has_ra_dec == 0:
  input_nrows = input_nrows +1
  output_dd_t.add_row([input_nrows, 'RA', 'RA', 'Right Ascension (J2000)', 'null', 'float', '12.6f', 'FLOAT(126)', 'y', '2', input_nrows, 'y', 'y', 'n', 'RA'])
  input_nrows = input_nrows +1
  output_dd_t.add_row([input_nrows, 'DEC', 'DEC', 'Declination (J2000)', 'null', 'float', '12.6f', 'FLOAT(126)', 'y', '2', input_nrows, 'y', 'y', 'n', 'DEC'])
input_nrows = input_nrows + 1
output_dd_t.add_row([input_nrows, 'X', 'X', '', 'null', 'double', '12.6f', 'FLOAT(126)', 'y', '2', input_nrows, 'y', 'y', 'n', 'X'])
input_nrows = input_nrows + 1
output_dd_t.add_row([input_nrows, 'Y', 'Y', '', 'null', 'double', '12.6f', 'FLOAT(126)', 'y', '2', input_nrows, 'y', 'y', 'n', 'Y'])
input_nrows = input_nrows + 1
output_dd_t.add_row([input_nrows, 'Z', 'Z', '', 'null', 'double', '12.6f', 'FLOAT(126)', 'y', '2', input_nrows, 'y', 'y', 'n', 'Z'])
input_nrows = input_nrows + 1
output_dd_t.add_row([input_nrows, 'SPT_IND', 'SPT_IND', '', 'null', 'integer', '12d', 'NUMBER(38)', 'y', '2', input_nrows, 'y', 'y', 'n', 'SPT_IND'])
input_nrows = input_nrows + 1
output_dd_t.add_row([input_nrows, 'CNTR', 'CNTR', '', 'null', 'integer', '12d', 'NUMBER(38)', 'y', '2', input_nrows, 'y', 'y', 'n', 'CNTR'])

if (output_dd_FOR_DB != ''):
  ascii.write( output_dd_t, output_dd_FOR_DB + '.tmp', format='ipac', fast_writer=False, overwrite=True, fill_values=fill)


fixme_t = Table.read(output_dd_FOR_DB + '.tmp', format='ipac')
for r in range(len(fixme_t)):
  if (fixme_t['description'][r] == '0.0'):
    fixme_t['description'][r] = ''
  if (fixme_t['units'][r] == '0.0'):
    fixme_t['units'][r] = ''
ascii.write(fixme_t, output_dd_FOR_DB, format='ipac', fast_writer=False, overwrite=True)

# Finish the SQL script

if (output_db != ''):
  db.write("    \"CRA\" VARCHAR2(11 BYTE),\n")
  db.write("    \"CDEC\" VARCHAR2(11 BYTE),\n")
  if ("hires" in table_name.lower()):
    db.write("    \"HA_D\" FLOAT(126),\n")
  db.write("    \"UTDATETIME\" TIMESTAMP (6),\n")
  if ("hires" in table_name.lower()):
    db.write("    \"MD_INGTIME\" TIMESTAMP (6),\n")
    db.write("    \"DVD_INGTIME\" TIMESTAMP (6),\n")
  else:
    db.write("    \"L0_INGTIME\" TIMESTAMP (6),\n")
  db.write("    \"FILEHAND\" VARCHAR2(151 BYTE),\n")
  db.write("    \"FILEURL\" VARCHAR2(151 BYTE),\n")
  db.write("    \"SEMID\" VARCHAR2(21 BYTE),\n")
  db.write("    \"X\" FLOAT(126),\n")
  db.write("    \"Y\" FLOAT(126),\n")
  db.write("    \"Z\" FLOAT(126),\n")
  db.write("    \"SPT_IND\" NUMBER(38),\n")
  db.write("    \"CNTR\" NUMBER(38)\n")
  db.write("  )\n")
  db.write("  TABLESPACE \"KOA_DATA\" ;\n")
  db.write("  CREATE INDEX IKOAIMTYP_" + table_name + " ON " + table_name + "(KOAIMTYP) TABLESPACE KOA_DATA;\n")
  db.write("  CREATE INDEX ISPT_IND_" + table_name + " ON " + table_name + "(SPT_IND) TABLESPACE KOA_DATA;\n")
  db.write("  CREATE INDEX IPROGTITL_" + table_name + " ON " + table_name + "(PROGTITL) TABLESPACE KOA_DATA;\n")
  db.write("  CREATE INDEX IDATE_OBS_" + table_name + " ON " + table_name + "(DATE_OBS) TABLESPACE KOA_DATA;\n")
  db.write("  CREATE UNIQUE INDEX UKOAID_" + table_name + " ON " + table_name + "(KOAID) TABLESPACE KOA_DATA;\n")
  db.write("  CREATE SEQUENCE " + table_name + "_SQ START WITH 1 INCREMENT BY 1 MINVALUE 0 CACHE 20;\n")
  db.write("  GRANT ALL ON " + table_name + " TO KOAADMIN;\n")
  db.write("  GRANT ALL ON " + table_name + " TO KOA_APP;\n")
  db.write("  GRANT ALL ON " + table_name + "_dd TO KOAADMIN;\n")
  db.write("  GRANT ALL ON " + table_name + "_dd TO KOA_APP;\n")
  db.write("  GRANT ALL ON " + table_name + "_sq TO KOAADMIN;\n")
  db.write("  GRANT ALL ON " + table_name + "_sq TO KOA_APP;\n")

print ("...Done!")
exit
