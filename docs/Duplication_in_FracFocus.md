<center> <img src="images/header_logo.png" width="100"/></center>
<!-- this is a test of a comment 
To do:
--->

|[Prev](Proprietary_records.md)|[Index](Top.md)|[Next](Generating_the_Open-FF_data_set.md)|
# Duplication in FracFocus

The bulk download of FracFocus is not quite a database but more a collection of disclosures that are in different formats and often with extraneous records.  Open-FF tries to unify these different formats to provide a coherent data set.

One aspect that requires attention is the **duplication** that occurs in FracFocus.

## Duplicated disclosures
Operators sometimes submit more than one disclosure for a particular fracking event.  This might be to correct mistakes in the initial disclosure or to add more ingredients to that initial disclosure.  Unfortunately, there is no way to tell which of those possibilities it is, or even which disclosure was entered first. (There is no direct record of publication date.)  Because of this ambiguity, Open-FF flags multiple disclosures at a given `APINumber` and `date` as unusable duplicates to be excluded from statistics.

## Duplicated records

An odd problem exists in thousands of disclosures: Some materials appear twice or more. In these duplicates, `CASNumber`, `IngredientName`, `MassIngredient`, `PercentHighAdditive`, and `PercentHFJob` are identical.

Within any typical FracFocus disclosure, occasional duplication is common and normal. This occurs because chemicals are recorded in the disclosure based *on the product* that is actually used. When two or more products contain the same chemical (even water), that chemical will validly appear more than once. Sometimes those multiples will be the same quantity, too. That is valid.

However, there are other duplications that do not occur because of separate product use. Instead, it appears that they are an unintended by-product of the way data are entered by the operators (according to the FracFocus team (via a 2019 email)).

In these affected disclosures, there can be many duplicates.  For these disclosures (at least in FFVersion 3), the PDF shows one of the duplicates above the red line with the text *“Ingredients shown above are subject to 29 CFR 1910.1200(i) and appear on Material Safety Data Sheets (MSDS). Ingredients shown below are Non-MSDS“*.  The other duplicate is below that line. However, not all of the records below the line are duplicates, but many may be.

These duplications, while they do not add unique checmicals to a disclosure, erroneously inflate the calculated mass of the chemicals there.  

As of March 2024, Open-FF can now detect these duplicate records regardless of the FracFocus version. (Between Dec. 2023, the launch of FFVersion 4, and Feb 2024, we had to use archived indications of duplicates to flag them.  In addition, FracFocus data sets downloaded from that period are rife with other unintended duplications.  FracFocus subsequently corrected some coding and reinstated the cues in FFV3 data that Open-FF uses to distinguish the unintended duplicates from valid ones.)  

<!-- Before December 2023 and the introduction of FracFocus version 4, Open-FF was able to detect those duplicated records (over 200,000) and flag them to be removed before any statisitcal operations were performed.  Unfortunately, FracFocus Version 4 has changed the format and undermined Open-FF's ability to detect those duplicates.  We are currently using archived indications of duplicates to flag them.  While this is not ideal, it allows us to continue to remove duuplicates until FracFocus can provide a better solution.
-->

## Using Open-FF without these duplicates
The full version of the Open-FF data set contains all records and disclosures that are included in the FracFocus bulk download.  However, for many operations, users may want to avoid the duplicate disclosures and records.  

Three fields can be used to remove these duplicates: 
- The field `is_duplicate` is a flag that, when True, indicates that a given disclosure has a duplicate in FracFocus; that is, they have the same APINumber and JobEndDate.
- The field `dup_rec` is a flag that, when True, indicates that the given record is a detected erroneous duplicate.
- The field `in_std_filtered` is a flag that, when True, allows a user to keep only the dsclosures and records in Open-FF that are not duplicated.  The Data Browser (with a few exceptions) uses ths data set.

Users should be aware that the unintended duplications created by FracFocus at the start of FFVersion 4 (Dec 2023 - Feb 2024; mentioned above) were not detectable by Open-FF and should be wary of using archived data from that period.  

|[Prev](Proprietary_records.md)|[Index](Top.md)|[Next](Generating_the_Open-FF_data_set.md)|