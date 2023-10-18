<center> <img src="images/header_logo.png" width="100"/></center>
<!-- this is a test of a comment 
To do:
--->

# Standardizing Text Fields

The fields in FracFocus that specify companies, commercial names of products, names and purposes of chemicals and several location names are text fields.  These can be important fields for searching through the entire data set (for example: finding all chemicals supplied by Halliburton).  Therefore, consistency throughout the data set is essential.  Unfortunately, consistency is apparently not enforced at the data-entry stage at FracFocus and searching with terms in the raw text fields is very frustrating.

Implemented solutions in open-FF

Using a translation table for OperatorName and Supplier

To create more usable fields of OperatorName and Supplier, we manually create a simple translation table that is used during database generation to create "best guess" versions of the raw fields.   First we convert each value in the field to all lowercase and strip any non-alphanumerics from the front and back.  Then we make a list of all unique values for the field - this is our list of 'originals' for which we will then create a translation.  For example,  in the Supplier field we find a huge number of variations of the name Halliburton.  In the 'primary' column, we specify what we want them to be called; in this case, simply 'halliburton.'

In this way, we are able to create a much cleaner field upon which to search.  Now, our search for all the Halliburton records requires a single search in the generated field bgSupplier instead of  ~80 searches in the raw Supplier field.  



## data checking problems
For a database to have integrity, data should be checked for validity as it is entered.  The reason is simple: Manual data entry is a tedious process that is prone to mistakes.  Anyone that has had to enter sheets of numbers and labels to a spreadsheet can attest to that.  Even automated data entry can occasionally misrepresent the original numbers.

Unfortunately,  validity checks in FracFocus seem to be inconsistently used.  It has been mentioned in web instructions to operators that there are some checks built in to the data entry, but that operators are only warned of problems and can still publish a disclosure with those errors.  We know that because it is not unusual for values to show up in disclosures that are obviously wrong.

StateName and CountyName are normalized in the location routines.

Other fields where errors can be obvious are the Latitude/Longitude fields.  In some disclosures, latitude and longitude values appear to be swapped.  For example, in one disclosure, the latitude is given as: -103.618841667, but latitudes range between -90 and 90 degrees.  However, using the swapped coordinates lands directly on a fracking well pad:

Yet another field in which obvious errors jump out is the TotalBaseWaterVolume, which is also included in most disclosures and, while it has been increasing throughout the FracFocus years, is typically in the 1 million to 30 million gallon range.  In March, 2020, ConocoPhillips published a disclosure with 1.87 billion gallons.   When I brought the mistake to their attention, they corrected it (a rare instance in which a company has replied to me).  The list of 25 largest water uses in FracFocus (as of Oct. 2020) is:

Within FracFocus, there are several fields that indicate the location of the fracking event.  StateNumber and CountyNumber are the official codes for the state and county of the fracking pad.  Latitude and Longitude provide geographic coordinates of the well. StateName and CountyName provide the text names.  And APINumber has the state and county numbers encoded in the upper 5 digits of the number.  Having such a range of fields should make it easy to search for or display data in a variety of ways.

Unfortunately, these fields are not always consistent across a record.  Plotting wells on a map reveals obvious mistakes in lat/lon data (e.g., wells in the ocean where there are none).  State and county fields are inconsistently abbreviated, spelled  and/or capitalized.  Searching for all events in a specific state or county would require multiple searches without some corrections.  There are state names that don't match state codes.

Implemented solution

The open-FF method normalizes state and county names by a manually created translation table. This corrects for misspellings and abbreviations in the field and the results are put into the fields bgStateName and bgCountyName.  Latitude and Longitude are also checked to be in a reasonable range for the given county coordinates; if they are outside that area, they are set to the geographic center of the county in bgLatitude and bgLongitude.  For both the names and the lat/lon changes, flags are set in the record_flags field to indicate where these problems were found (look for 'N' and 'L' flags).  The unchanged FracFocus values of those fields are still available to the user in the data set in the original names.

In these solutions, the APINumber is assumed to be the authority: that is, that the location code in the number is correctly assigned.  

As of Nov. 2020, there are about 200 disclosures where just the lat/lon was corrected and about 750 disclosures where both names and lat/lon were corrected.  Many of these are from the early years of FracFocus.