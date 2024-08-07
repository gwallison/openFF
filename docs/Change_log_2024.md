<center> <img src="images/header_logo.png" width="100"/></center>
<!-- this is a test of a comment 
To do:
--->

[Return to Index](Top.md) 

# Change Log - 2024
This file is used to summarize changes that we make at Open-FF and to document changes that we find at FracFocus, either in the bulk data download or the online interface.  We also point out our communication with FracFocus.  This log was started in early 2024, soon after FracFocus introduced its Version 4. 

## Issues around FFV4
**Dec. 2023** - FracFocus announces the implementation of their "version 4." :
> The FracFocusData.org Upgrade to version 4.0 was officially launched on 12/4/2023.  This new site updates the features of the previous version to a modern architecture, providing stability and features for the future.  A few of the additions include:

> - Water Source – added to allow companies to easily identify water reuse.
> - Security – 2 Factor Authentication Required
> - Modernization of User and Organization updates
> - Enhancement to data viewing, edits, and download features for users
> - Additional Validation testing for better data quality

([source visited March 3, 2024](https://fracfocus.org/FracFocus4Launch))

This new version has numerous implications for Open-FF:
- A few important fields were renamed, thereby touching almost all of Open-FF code.
- The disclosure and chemical identifying keys that had been stable since at least 2018 were thrown out and new ones reassigned.
- Other fields, such as `TradeName`, `Supplier` and `Purpose` were changed so that empty cells were filled with values (e.g. "Ingredient Container"). This change impacted how Open-FF could detect internal disclosure problems like duplicate records.  

**Dec 26, 2023** We contacted FracFocus about the difficulty detecting duplicate records in FFV4 and pointed out that [we had alerted them](https://frackingchemicaldisclosure.wordpress.com/2019/12/06/spurious-duplicate-records-within-a-fracking-event/) to the issue in 2019 as well.  We detect about 17,000 disclosures by over 500 companies with the issue and find that the duplicated records add a median of about 60,000 lbs of materials that shouldn't be there.

**Jan 2, 2024** FracFocus replied to the above email that in their investigation of the duplication problem we reported, they found a different problem where a large number of records were duplicated.  They submitted a patch and corrected the issue they found. (Archives of downloads between Dec 4 and early January will contain this problem.)  They explained that if the records we pointed out are not really intended, there is not much they can do about it:
> "As for there being true submissions of duplicates by the operators of individual ingredients, this is still something we cannot remove from the submissions.  There is no assurance that the submission is not correct and since it is an official record of submission to the State we cannot delete.  We do have a new feature in the system for the users that allows us to create data reports.  We will investigate creating a report that will identify to the operator disclosures where duplicate ingredient records exist on the same disclosure."

In a later email, they add:
> "As for the records you have identified in the disclosures that are duplicate, those records are either manually entered or uploaded by the operator/service company as representative of the chemicals used during the job.  The system does not create these records the user does.  Operators are responsible for the creation of and submission of the data and must review/validate the data prior to submission.  We cannot say if they are mistaken duplicates or valid records but can only maintain that the operator submitted them. "

At this point, Open-FF's strategy to detect and remove duplicate records is as follows:
- if the disclosure is a FFV4, we look for a `TradeName` of "Other Chemicals."  So far we have found lots of duplicates in this set of chemicals.  It appears that the PDF format used in earlier versions with the duplication problem (those chemicals below the red line), is no longer being used.
- if the disclosure is an easlier version, we use a translation table between the old `UploadKey` and the new `DisclosureId` keys to find the disclosure we know had duplicates in the past (even though we can't detect them the same way.)  Finding the duplicates with the TradeName 'Ingredient container' catches most of the ones we had found before.

**Jan 14, 2024** We found that many records with duplicate `IngredientsId` and the duplicates appeared to replace other records in the disclosure.  In an email to FracFocus we wrote:
> " This probably only happens in the CSV download version because it seems to happen when a disclosure straddles two FracFocusRegistry files in the zip file.  The two duplicate records are in different files. "

FracFocus replied on Jan 18 that they found the issue and corrected it.  We added a test in the final build to detect any duplicated `IngredientsId`s.

**March 2, 2024** We found that the bulk download from today is significantly smaller than the Feb 19 version.  It appears that this is largely due to significant changing of the `TradeName`, `Supplier` and `Purpose` fields in a large set of records (over a million).  It seems that they are replacing the "Ingredient Container" value with an empty cell - where that was the situation before FFV4.  As of now that seems to affect mostly 2013-2015.  Maybe they are doing a general cleanup and get to the later dates soon?  

At this point, we are taking a wait-and-see approach until the data settle down.  For now, no more code adaptations.  We are going to build this disclosure-to-disclosure check into the build to flag such massive changes as soon as possible.

Incidentally, over those two weeks, about 60 disclosures were removed including 6 from CNX, but all of them were replaced under a new DisclosureId with some changes.  On March 3, at least 4 of the CNX disclosures were removed again, at least judging from the FracFocus search page.

**March 4, 2024** Upon comparing the PDFs and bulk download data from early disclosures, it appears that one of the recent changes taken by FracFocus in FFV4 is put back the initial TradeName, Purpose and Supplier that were originally in the disclosures (mostly 2013-2025) that had been replaced with "Ingredient Container" etc.  It seems this returns the disclosures to their original states.  Perhaps they will be doing the same for the disclosure with `dup_recs` as well.

**March 7, 2024** Indeed, a large number of disclosures have been modified and now Open-FF can detect the duplicate records in the same way both pre and post FFV4.  This means that we do not have to rely on a translation table between UploadKey and DisclosureId.  With that code resolved, we now detect more that 235,000 records as duplicates.

<!-- this is a test of a comment 
This text is not correct
to separate the "multiple TradeName" entries (for example, common for Schlumberger, [42389328870000](https://fracfocus.org/wells/42389328870000)) from the chemical records.  These are the numerous disclosures in which companies created their own version of the Systems Approach by just reporting that all chemicals came from a long list of products.  I believe that this change in FracFocus will make the difference between System Approach and MSDS+ more distinguishable, though it may be odd to have multiple copies when that non_chemical record that previously corresponded to multiple chemical records.

However, in initial spot checking we are also finding places where FracFocus is transforming MSDS+ formats to SysApp ([example](https://fracfocus.org/wells/49037278610000)).  That is, the chemicals in this disclosure were previously linked to their products.  This would be a big loss if it is widespread, because it is in the MSDS+ formats that we learn about the incredible inconsistency of reporting individual products.

Furthermore, during this change, their entire PDF data is acting weird.  All PDFs are in error.
--->

## Water Source data
**Jan 2024** FracFocus V4 introduced a new optional  table of data that allows operators to report what types of water source(s) they used as the carrier.  Here is FracFocus's description:

>"The Water Source data is strictly a voluntary submission.  It was added after observing the efforts of operators attempting to show similar water source data by breaking out the carrier fluid into multiple ingredient records representing different sources of water being used on a job (e.g., produced, brackish, etc.).  Entering the data into the disclosure in this manner added complexity in presenting the story of Produced Water Reuse. Companies were trying to show that the water being used on a fracturing job was not all fresh water and be proactive with representing their company’s ESG mission. Adding the ability to submit water source data provides a means to address this issue and a simpler way to present the information. Showing a clearer picture of water use during Hydraulic Fracturing."

([source visited Mar 3, 2024](https://fracfocus.org/news/water-source-data))

Open-FF summarized the data in the "[new disclosure report](https://frackingchemicaldisclosure.wordpress.com/2024/02/21/new-disclosure-summary-feb-2024/)" in late Feb and the data look promising.  

**Feb 29, 2024** We found that some disclosures did not conform to what appeared to be the format and we contacted FracFocus via email about it:
> "Close to 40 disclosures don't report 100% of the water used.  I count twelve different companies with this issue (below).   In many of those cases, it appears that companies are just reporting the  PercentHFJob of the carrier  as the water source percentage (42439372970000,  35019065480000).  In at least one case (30015501010000) the company uses fraction instead of percentage. (from data download 2/17/2024)."

We supplied the breakdown of companies involved and we asked:
>"Should I contact the companies (through you and this email channel) to let them know about the problems or is that something that FraFocus does directly?  "

**Mar 1, 2024** FracFocus replied that:
> "The water source data is voluntarily submitted information.  Thank you for providing the information and we will review it for inclusion as part of a training email sent to users on a periodic basis.  "

## Colab notebooks

**March 2, 2024** We recently released a new version of the ["Explore Near Location"](https://colab.research.google.com/github/gwallison/openFF/blob/master/notebooks/Explore_near_location_v2.ipynb) notebook that is aligned with FFV4 data sets.  This notebook has 
- added some more instructions in the notebook and (hopefully) makes the workflow through the notebook more intuitive
- added a report generator that creates a PDF of the results you assemble.

**March 6, 2024** We released a notebook that allows users to create customized data set. Unfortunately the size of the current FracFocus data set prevents this notebook from running in Colab. (If you want to try, go to ["Data Set Customizer"](https://colab.research.google.com/github/gwallison/openFF/blob/master/notebooks/Data_set_customizer.ipynb)).  Until we get that worked out, please contact us if you want a custom data set.

## More duplicated records

**March 22, 2024**
We have changed the Bulk data reading module to include the field `IngredientComment` into the data set.  (Previously it was used only to document the reported density of a chemical record.) This change was precipitated by the discovery of more duplicated records, this time in Systems Approach disclosures and that, seemingly, the only way to detect these was by the values in that commnet field, in particular the word 'None'.  This change required that we slightly change how we deal with 'missing values' in the pandas function, read_csv.  Essentially, we had to disable the automatic detection of missing values ('None' is normally considered an empty value) in that column.  In addition, it appears that this 'None' value is not always consistent between the PDF version and the bulk download version.

**April 12, 2024**
We added code to TableManager to detect these additional duplicates.  They are labeled the same way as the initial set, `dup_rec` == True.  Therefore they will be flagged with the others in the FF_issues module.  There are still other duplicates that we detect, but it is not clear yet what conditions we can use to to flag the record that is erroneous.  It may make sense to flag these in FF_issues as "possible unintended duplicates" to leave it up to the user's discretion.

**March 26, 2024**
Using the `IngredientComment` field, we could then detect an additional 1200 disclosures (though there are probably more) with unintended duplicates. (We alerted FracFocus to this disclovery on Mar 23 by email.) It is important to note that we checked a different source of the disclosures, PA DEP completion data, on a handful of the disclosures and the state data DID NOT have the duplications.  That, and the fact that these duplicated records happen to at least 500 different operators, leads us to believe that the genesis of these duplications is either in the FracFocus software itself or in some software tool that many companies use to prepare their data for FracFocus submission.  (We mentioned that in our letter to FracFocus.)

## Starting a daily download test
**March 28, 2024**
With all of the recent flux in the FracFocus data due to the recent version change, and how important those changes could be to the proper operation of FracFocus, we felt the need to regularly test the bulk data download for major changes, day to day.  We implemented a simple comparison of the current download to a previous download (ususally the previous day) to document the changes that occured in that period.  Currently the results from this test is not public, but we may change that so users can regularly see what kinds of changes are happening at FracFocus.

## FracFocus Issues/Flaws flags
**March 28, 2024**
We have been developing code to not only detect errors and other issues in the FracFocus data, but to classify and flag it so that users of the Open-FF system can be aware of specific problems that other people have found.  The current set of issues flagged is still small (but we have a growing todo list!).  Today we added code so the full_df data set now has summary flags.  The are disclosure and record level flags, depending on what organizational level is affected.  Further, we added preliminary hooks to the Open-FF disclosures so that users can ee them directly.

## MassIngredient issues
**May 8, 2024**
Before FFV4, Open-FF used the FracFocus field `MassIngredient` only to confirm the calculated mass values.  With the new FFV4, FracFocus included the field in their data dictionary and so we began to include it directly in Open-FF's `mass` field.  (see [the calculating mass page](Calculating_mass.md)). While that change gives us access to the mass of many more records, we are finding that some of those values of `MassIngredient` are suspect, even the disclosures that pass the MI_inconsistent test.  For example, there are a substantial number of disclosures for which no water carrier record is provided and the sand record takes on a large percentage, often over 90%. In many of these disclosures, the `MassIngredient` value for sand is clearly out of whack.    Today I am finding other chemicals that are similarly affected.  We will need to find a way to systematically identify these crazy numbers and alert the reader.

**May 24, 2024**
I am finding more situations where `mass` is sourced only by `MassIngredient` and the values are clearly wrong.  Because users of the Open-FF data may not know to check for conditions that imply outlier masses, I have decided to fall back to the previous, more conservative, method of using just `calcMass' as the source of `mass`.  The addition of the field `mass` is relatively new with the usage of `MassIngredient`; I will keep `mass` because it is now embedded in a lot of downstream code.  This means that roughly 250,000 records for which `MassIndgreient` was the only souce of mass, will no longer be directly included in `mass`.  I am sure than many of those values are completely acceptable, but we currently have no easy way to descriminate good from bad.    My goal is to eventually produce algorithms that detect conditions that make `MassIngredient` unreliable and get back to using the reliable values.

## Updates for the July 18, 2024 repo

**July 19, 2024**
To identify PFAS chemicals in the FF data, I have been using the EPA list called PFASMASTER.  THey have recently retired that list and replaced it with two lists, PFASDEV and PFASSTRUCT.  These lists will be regularly updated as EPA is actively investigating PFAS materials.  For Open-FF, we will combine the two lists into the list used to flag PFAS. The PFASDEV list includes many chemicals that do not yet have CAS numbers.  Open-FF keeps those in the attempt to find FF matches, but of course they are unlikely to be used in FF.  There are simply  no other standardized ways of identifying those materials in FF besides CASRN. 

I am also integrating the most recent [non-confidential TSCA inventory](https://www.epa.gov/tsca-inventory/how-access-tsca-inventory) into the data set. This will used for the UVCB flag as well as commercial status, EPA regulatory flags and the TSCA chemical definition.

These changes are implemented in `build\core\external_dataset_tools.py`.





[Return to Index](Top.md)
