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
| Description | Keyword definition
| Notes | Any notes pertaining to this keyword and/or value
