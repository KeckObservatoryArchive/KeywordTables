# KeywordTables
These tables contain definitions and paramaters for all archived instrument keywords and any additional database information added during archiving of FITS data.

These files are used to:
* Create a configuration file at WMKO for creation of metadata tables and verification of data types
* Create the configuration file at NExScI used by dbIngest to vet incoming metadata
* Create the Oracle database tables (metadata + DD file) at NExScI, which in turn are used to generate TAP_SCHEMA contents


The files are saved as tab-separated columns with the following information:

| FITSKeyword | Keyword Name from FITS file|
| ------- | ------------ |
| DBKeyword | Name in database table 
| Source | Original source of keyword value
| MetadataDatatype | Datatype in metadaa table (ie char, double, integer)
| Size | Maximum character length of keyword value
| DBDatatype | Data type for database table creation
| Units | Units for the keyword value
| NullsAllowed | Are nulls allowed for this keyword?
| ValidateFormat | Does the value match the data type for this keyword?
| CheckValues | Verify data range (mincol, maxcol) and verify FITS value is the same as metadata value
| OutputFormat | Format in the DDs and TAP schema
| SpecialIngest | Is there special treatment by dbIngest (i.e. hard-coded alterations to contents or name)
| MininimumVal | Minimum allowed value for the keyword
| MaximumVal | Maximum allowed value for the keyword
| DiscreteValues | Comma-separated list of allowed values for the keyword
| Metadata | Include in meatadata sent from WMKO to NExScI
| UI | This keyword is used in the KOA UI
| Calib | This keyword is used for calibration association
| TAP_visible | This keyword wil be exposed to the TAP service
| TAP_principal | Value of 'principal' in TAP_SCHEMA.columns - some TAP clients use to determine whether to include in default selection
| Description | Keyword definition
| Notes | Any notes pertaining to this keyword and/or value


As of Sep 2020,  not all keyword table functionality is actually implemented yet:
* dbIngest currently hard-codes transformations between FITSKeyword and DBKeyword (ie DATE-OBS to DATE_OBS); future ingestion code updates will use  the contents of FITSKeyword/DBKeyword to make such changes in the metadata header
* The TAP_columns will be used when TAP_SCHEMA table output is added
* The UI, Calib, and SpecialIngest columns are currently informational only 

# makeInstrumentFiles.py

To generate the NExScI configuration and SQL files:

`makeInstrumentFiles.py [-h] [-d] [-kw OUTPUT_KW] [-dd OUTPUT_DD] [-db OUTPUT_DB] input_tab_file table_name`                                                                  
Where:

* OUTPUT_KW = keyword table used by dbIngest ($CM_KOA_DIR/src/svc/dbIngest/data/KOA_INSTR_Keywords.tbl)
* OUTPUT_DD = prefix for two DD files: 
  * OUTPUT_DD.for_disk to be used by dbIngest ($CM_KOA_DIR/src/svc/dbIngest/data/KOA_INSTR_DD.tbl)
  * OUTPUT_DD.for_database for initialization of DD in Oracle database using dbin ($CM_KOA_DIR/src/svc/sqlscripts/koa_instr_vX_scripts)
* OUTPUT_DB = SQL script to be run to initialize instrument table and indices / sequences / privileges ($CM_KOA_DIR/src/svc/sqlscripts/koa_instr_vX.sql)
* input_tab_file = tab-delimited keyword table from this repo, 
* table_name = name of instrument table (ie KOA_INSTR_VX)
