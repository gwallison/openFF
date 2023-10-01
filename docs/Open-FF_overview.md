<center> <img src="images/header_logo.png" width="100"/></center>
<!-- this is a test of a comment 
To do:
--->

# Open-FF Overview
Open-FF is an independent project to transform the FracFocus data into a useful resource for researchers, journalists and community advocates. The open source project has been evolving for several years and FracTracker Alliance has recently started sponsoring the effort.

At its core, Open-FF simply takes the FracFocus data and pairs it with corrections, clarifications, calculations, and alerts that add perspective to the industry’s published data. This core data set is then packaged in a number of ways to make it available online to everyone from the hard-core data analyst to the non-technical casual browser. Two of the most important features of a chemical disclosure are unambiguous chemical identity and quantity.

Open-FF uses the two chemical identifiers reported  in FracFocus to resolve identity in the many cases that FracFocus data is ambiguous.  The primary identifier is the CAS Registry Number that is a standard authoritative number widely used to uniquely characterize materials.  While the FracFocus website advises users to give priority to this CASRN, there are many errors and omissions that require us to also use the second identifier, an ingredient name. This work is accomplished with a combination of software and manual curation.  See the [resolving chemical identity](Resolving_chemical_identity.md) page for more details.

Throughout the FracFocus website and data, the quantity of chemicals is represented by limited perspective: the percent of the mass of the entire fracking fluid that the individual chemical comprises.  These numbers are typically very small because in a typical frack, all chemical additives together (everything but the water and sand) are usually less than one percent.  But this perspective obscures very large absolute masses of chemical reports when fracking jobs are very large.  Open-FF uses data contained in FracFocus disclosures to calculate and verify those masses and make them available to users.  See the [calculating mass](Calculating_mass.md) page for more details.

In addition to these two core features, Open-FF performs other checks and clarifications, tries to resolve non-standardized text fields, and provide perspective to the chemical data reported in FracFocus.  The data set is updated regularly with new disclosures available for download.  Further, Open-FF generates an online "browser" with which users can explore many features of the FracFocus data without needing to download files.

Open-FF history

Uses of Open-FF

Affiliations of Open-FF

<!--
### Other features
1. Links to ChemInformatics and other data sources of chemical and health/env summaries
1. Attempts to standarize and/or aggregate text fields to help searching across the whole data set
1. Cross-checking location data to verify that reported locations are consistent and flagging them when they are not.
1. An online "browser" with which users can explore many features of the FracFocus data without needing to download files. The browser lets users explore:
    - detailed chemical reports of how more than 1,300 materials are used across FracFocus
    - detailed company reports of operators - where and when they are active, their water use, their suppliers, their use of classes of known "chemicals of concern" and the frequency of their proprietary claims.
    - summaries based on state and county uses.
    - big picture summaries of the FracFocus data
    - a data dictionary for the Open-FF data set
    - an interactive chemical synonym table to help connect chemical names with their CAS numbers.
-->