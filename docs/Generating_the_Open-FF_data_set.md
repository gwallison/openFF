<center> <img src="images/header_logo.png" width="100"/></center>
<!-- this is a test of a comment 
To do:
--->

|[Prev](Proprietary_records.md)|[Index](Top.md)|[Next](External_data_in_Open-FF.md)|

# Generating the Open-FF data set

The Open-FF data set is regenerated roughly every month to update with new fracking disclosures and to incorporate and changes that were make to existing disclosures.  The process is performed by the developers of Open-FF and is sponsored by the FracTracker Alliance.  

The process has many steps, some automated, some manual.  It is guided by [a jupyter notebook](https://github.com/gwallison/openFF/blob/master/build/builder_nb.ipynb) that includes instructions, code and tests to validate the process through each step.  The primary steps are:

## Set up
1. Downloading the materials needed: 
    - the previous data repo
    - the external data sets used
    - a fresh FracFocus download

## Curation
2. Determine the disclosures that are new
1. Search the fresh data for new `CASNumber`s; fetch authoritative data about them (SciFinder, CompTox)
1. Search the fresh data for new `IngredientName`s; try to resolve to an authoritive CASRN.
1. Assign final `bgCAS` value to each new `bgCAS`:`IngredientName` pairs
1. Search for new company names and link them to other existing company names is appropriate
1. Check geographic and location data - flag errors and curate any new counties
1. Determine the carrier record(s) of every disclosure to facilitate mass calculations

## Generation
9. Search for duplicate disclosures and duplicate records; flag them
1. Flag disclosures without chemicals
1. Assemble chemical, disclosure, and company tables
1. Apply external lists to chemical list
1. Calculate mass where enough data is available
1. Produce full data set

## Post processing
15. Perform dataset-wide integrity tests
1. Construct a full data repository

|[Prev](Proprietary_records.md)|[Index](Top.md)|[Next](External_data_in_Open-FF.md)|