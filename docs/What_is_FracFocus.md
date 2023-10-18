<center> <img src="images/header_logo.png" width="100"/></center>

<!-- 
To do:

What should be here:
X PDF vs bulk
X third party organization
Xnot responsible for accuracy of data
overview of complaints
list of obstacles
-->

# What is FracFocus?

In its own words, the [FracFocus website](https://fracfocus.org/) is the "national hydraulic fracturing chemical disclosure registry." FracFocus serves as the collector and manager of fracking chemical disclosures of the oil and gas industry. It delivers published disclosures to state regulators and its website  makes those disclosures public, allowing anyone to view the industry's reports. While it started in 2011 as an experiment, its use is now required by many states.

As of late 2023, there are over 200,000 disclosures of fracturing events performed by over 1,500 companies with well over 5,000,000 individual chemical records.

These data are delivered in two forms to the public: 
- through a bulk download of the data (as either SQL database or CSV files)
<!-- provide several examples of the PDF -->
- PDF files of individual disclosures found through a search page called 'Find-a-Well'. (An website addition in 2023 facilitates searching by map and an *abbreivated* chemical list before the PDF is delivered.) 

### Responsibilities 
As a third party entity, FracFocus asserts that it is not responsible for the accuracy of the data published there.  For example, with respect to trade secrets in the data, the website[^1] explains: 

[^1]: Accessed Sept. 30, 2023.

>"1. FracFocus is a third-party reporting system, operating as an unbiased resource for information. No legal authority is granted to FracFocus to determine what is or is not officially categorized and protected as a trade secret. This is solely at the discretion of the individual states in which the companies operate."

>"2. The capabilities of FracFocus are limited to functioning as a database and educational resource. All system operations are focused on providing the most robust and user-friendly structure possible, and do not extend to determining the legal classification of chemicals or maintaining current knowledge of changing state laws.

### Data weaknesses
<!-- FracFocus provides minimal data checking and standardization.-->  
While the FracFocus data set is one onf the largest single collections documenting the use of fracking chemicals, many data issues prevent its widespread use and understanding. Some of the more serious weaknesses include:

1. Most disclosures in the bulk download from 2011 through May 2013 do not include chemical records. (PDF files for those fracks document the full disclosure, but typically must be examined individually.)
1. 'Quantity' is presented throughout the FracFocus system as a chemical's fraction (by weight) of the entire fracking fluid.  This proportional perspective obscures large chemical uses.  A non-documented field `MassIngredient` is provided for only about half of records and for many of those disclosures, it is internally inconsistent.
1. For some wells, there may be multiple disclosures for a single fracking event.  The data provide no indication if these are the original disclosures followed by corrected ones or if they are partial disclosures to be combined.  No justification is supplied.
1. There are many records in which the chemical identity is ambiguous due to typos, conflicting information, missing information, or other errors.
1. Some major text fields such as `Supplier` and `IngredientName` are not standardized.  For example, there are more than 80 distinct names recorded for the company "Halliburton".
1. The data available at FracFocus can apparently be changed without notification, justification or audit trail.  We have found that some disclosures have been changed silently several years after they were first published.
1. The single indicator of the size of the fracking job is the `TotalBaseWaterVolume` which ranges from under 10,000 gallons to over 50,000,000 gallons. In a sizable number of disclosures, that value is not recorded.
<!-- 1. A substantial number of disclosures duplicate chemical records. To keep from overestimating chemical quantity, users must  find and remove such redundancy. -->

### An important but flawed resource
Despite these weaknesses, FracFocus remains the primary instrument by which we can learn of chemical uses in the fracking industry.  Working to overcome these weaknesses can lead to a better public understanding of this controversial process.