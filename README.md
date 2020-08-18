# KeywordTables
Instrument keyword definitions and paramaters

These files are used to:
* Create a configuration file at WMKO for creation of metadata tables and verification of data types
* Create the database tables at NExScI
* ...

The files are saved as tab-separated columns with the following information:

| Keyword | Keyword Name |
| ------- | ------------ |
| Source | Original source of keyword value
| Description | Keyword definition
| Data Type | char, double, integer
| Size | Maximum character length of keyword value
| DB Data Type | Data type for database table creation
| Units | Units for the keyword value
| Nulls Allowed? | Are nulls allowed for this keyword?
| Validate Format? | Does the value match the data type for this keyword?
| Check Values? | Verify data range (mincol, maxcol) and verify FITS value is the same as metadata value
| Mincol | Minimum allowed value for the keyword
| Maxcol | Maximum allowed value for the keyword
| Discrete Values | Comma-separated list of allowed values for the keyword
| UI | This keyword is used in the KOA UI
| Calib | This keyword is used for calibration association
| Notes | Any notes pertaining to this keyword and/or value
