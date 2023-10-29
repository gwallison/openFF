<center> <img src="images/header_logo.png" width="100"/></center>
<!-- this is a test of a comment 
To do:
--->

|[Prev](Calculating_mass.md)|[Index](Top.md)|[Next](Proprietary_records.md)|

# Normalizing Text and Numeric Fields

The fields in FracFocus that specify companies, commercial names of products, names and purposes of chemicals and several location names are text fields.  These can be important fields for searching through the entire data set (for example: finding all chemicals supplied by Halliburton).  Therefore, consistency throughout the data set is essential.  Unfortunately, consistency is apparently not enforced at the data-entry stage at FracFocus.  For example, the company Halliburton is represented by over 100 unique labels which include formal names, shortened names, abbreviations, typos, and combinations with other companies.  Searching for all records of this company with the raw `Supplier` values is very frustrating and tedious.  

### Implemented solutions in open-FF

To create more usable fields of `OperatorName` and `Supplier`, we manually create a simple translation table that is used during database generation to create "best guess" versions of the raw fields.   First we convert each value in the field to all lowercase and strip any non-alphanumerics from the front and back.  Then we make a list of all unique values for the field - this is our list of 'originals' for which we will then create a translation.   In the 'primary' column for our example above, we specify what we want them to be called; in this case, simply 'halliburton.'

In this way, we are able to create a much cleaner field upon which to search.  Now, our search for all the Halliburton records requires a single search in the generated field `bgSupplier` instead of >100 searches in the raw `Supplier` field.  



# Data checking 
For a database to have integrity, data should be checked for validity as it is entered.  The reason is simple: Manual data entry is a tedious process that is prone to mistakes.  Anyone that has had to enter sheets of numbers and labels to a spreadsheet can attest to that.  Even automated data entry can occasionally misrepresent the original numbers.

Unfortunately,  validity checks in FracFocus seem to be inconsistently used.  It has been mentioned in web instructions to operators that there are some checks built in to the data entry, but that operators are only warned of problems and can still publish a disclosure with those errors.  We know that because it is not unusual for values to show up in disclosures that are obviously wrong.


Within FracFocus, there are several fields that indicate the location of the fracking event.  `StateNumber` and `CountyNumber` are the official codes for the state and county of the fracking pad.  `Latitude` and `Longitude` provide geographic coordinates of the well. `StateName` and `CountyName` provide the text names.  And `APINumber` has the state and county numbers encoded in the upper 5 digits of the number.  Having such a range of fields should make it easy to search for or display data in a variety of ways.

Unfortunately, these fields are not always consistent across a record.  Plotting wells on a map reveals obvious mistakes in lat/lon data (e.g., wells in the ocean where there are none).  State and county fields are inconsistently abbreviated, spelled  and/or capitalized.  Searching for all events in a specific state or county would require multiple searches without some corrections.  There are state names that don't match state codes.

### Implemented solutions in open-FF

The open-FF method normalizes state and county names by a manually created translation table. This corrects for misspellings and abbreviations in the field and the results are put into the fields `bgStateName` and `bgCountyName`.  `Latitude` and `Longitude` are also checked to be within the reported county; if they are outside that area, Open-FF tries to use the state-reported location of the well for the values `bgLatitude` and `bgLongitude`. (Those state-reported values are also reported even when the FracFocus versions aren't detected as errors as `stLatitude` and `stLongitude`.)  Open-FF generates flags to warn users when such issues are detected for a disclosure.  The unchanged FracFocus values of those fields are still available to the user in the data set in the original names.  In addition, Iin FracFocus, lat/lon values can be one of three different projections.  In Open-FF, `bgLatitude` and `bgLongitude` are normalized across the data set to be the same geographic projection.


# Other text fields

Some other text fields such as `TradeName`, `Purpose`, and `WellName` are currently not curated for consistency.  

# Other numeric fields

Three important numeric fields are `PercenHFJob`, `PercentHighAddive` and `MassIngredient` that provide information about quantity of chemicals.  While Open-FF does not attempt to correct errors, it checks for consistency within disclosures and flags problems to keep users from using error-prone data.

Some numeric fields are not checked.  An example is `TVD`, (Total Vertical Depth, in feet) though we know there are some disclosures with comical errors.

|[Prev](Calculating_mass.md)|[Index](Top.md)|[Next](Proprietary_records.md)|