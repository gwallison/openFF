<center> <img src="images/header_logo.png" width="100"/></center>
<!-- this is a test of a comment 
To do:
--->

|[Prev](Resolving_chemical_identity.md)|[Index](Top.md)|[Next](Standardizing_text_fields.md)|
# Calculating Mass


### Quantity by percentage...
FracFocus provides a limited perspective of chemical quantity; that is, FracFocus  reports quantity as the percentage (by weight) of the chemical compared to the overall fracking fluid. So, for the chemical “water,” FracFocus may record something like 85%.  For “sand,” it will probably be something like 14%. The fracking “additives” together are typically less than 1%. (The figure below is modelled after a figure from the [FracFocus website](https://fracfocus.org/learn/what-is-fracturing-fluid-made-of)[^1].)The percentages of individual additives are often tiny.  Viewing chemical quantity from only this perspective does indeed make the chemical’s contribution seem insignificant. 

[^1]: Accessed Sept. 30, 2023.

<center> <img src="images/quant_FF_pie.png" width="300"/></center>


### ... and by mass.

However, another way to view chemical quantity is by mass; that is, the absolute weight of the chemical material used. Open-FF uses the FracFocus data to calculate that weight. 

### An Example
A typical fracking job in 2022 used [16 million gallons of water](https://storage.googleapis.com/open-ff-browser/Open-FF_Scope_and_Aggregate_Stats.html#water_use). Taking the simple fact that one gallon of water weighs about 8.3 pounds, we find that 
> the base water weighs **about 130 million pounds.** 


If we use that typical 85% for water, that means 

> the total fracking fluid weighs about **156 million pounds.**

Finally, if we use a [typical percentage of hydrochloric acid](https://storage.googleapis.com/open-ff-browser/7647-01-0/analysis_7647-01-0.html#detailedAbundance) (0.06% of the whole fracking fluid), we find that translates into 
> over **90,000 pounds of acid**,

which is hardly insignificant. 

There are many fracking jobs where hydrochloric acid use is much greater. As of Sept. 2023, there are:

> more than 300 fracking jobs in the data set reporting over **1,000,000 pounds** of the acid.

While a user could calculate those weights directly from the data provided in FracFocus, Open-FF calculates weights for all FracFocus records (where data are sufficient) and users have easy access to those values. 

### Some details
#### Required data
This simple method of calculating masses with in a fracking disclosure has been verified by the technical staff of FracFocus.  It depends on a few important pieces of data: 
1. The total base water volume which is given in most disclosures,
1. a specific indication which records in the disclosure are the carrier water, 
1. and an assumption that the carrier is indeed water.

For item 1, there are many disclosures without this value in FracFocus, or a value of zero gallons is given. For these deisclosure, we cannot calculate mass of any records.

For item 2, this value is clear for a large majority of disclosures. But in the remainng, Open-FF employs algorithms to identify the carrier record(s). Roughly 0.5% of disclosures cannot be characterized this way.

For item 3, we assume simple water is the carrier for our denisty multiplier when the density is not specified directly.  While this simplifying assumption may be off when recycled or produced water is used, those other products are typically of higher density.  Therefore our simple assumption likely underestimates masses.

#### An important caveat
The quantity as recorded in disclosures is the "Maximum Ingredient Concentration in Additive (by % mass)." The mass we calculate is a MAXIMUM in a range of possibilities. This comes about because chemical information in a disclosure is often extracted from Material Safety Data Sheets (MSDS) for a trade-named product in a fracking job. In the MSDS, the amount of each component in the product is usually given as a range. Manufacturers of these products may report a range to reflect variation in the manufacturing process or to protect confidential recipes. Here's an example of a product by Chemplex[^2]:

<center> <img src="images/Plexbor_msds.png" width="700"/></center>

[^2]:The figure shows a portion of an MSDS downloaded from https://ohiodnr.gov/wps/portal/gov/odnr/discover-and-learn/safety-conservation/about-ODNR/oil-gas/sds in Aug., 2021.

In this case, Ethylene glycol may be as low as 12% in the product or as high as 15%. FracFocus requires companies using this product to report the 15% number in the disclosure and this will be reflected in the PercentHFJob value and, therefore, our calculated mass.

This dependence on MSDS and maximum values creates an odd situation: sometimes the total percentage for a product (and for a whole disclosure) will be greater that 100%. Other times they will even be less than 100% because MSDS don't necessarily report all the ingredients in a product, only the "hazardous" ones.

In Open-FF, when evaluating whether a disclosure's total percentage is ok, a 5% tolerance is acceptable: 95-105%.

#### A mass measurement buried in FracFocus
There is a field in the bulk download of FracFocus, `MassIngredient`, that is undocumented. (We had to verify by email with FracFocus's technical staff that the quantities were in pounds).  This field has non-zero values in roughly two-thirds of FracFocus records. We have found that, even when it does have values, they can be inconsistent[^3] within the disclosure or too coarse to be useful. Given this unreliable nature, we have chosen to use them to provide feedback to our mass calculations described above.   That is, when we determine that these 'MassIngredient' values are internally consistent, we compare them to Open-FF's `calcMass`.  If the difference between the two is outside a pre-determined tolerance, we do not report the calculated mass and we flag the record.  

Currently, there are over 2.7 million records in which the `calcMass` and `MassIngredient` agree and only around 50,000 where they do not (and therefore we do not report `calcMass`). When we have investigated those discrepancies, they seem often attributable to `MassIngredient` issues.

[^3]: Because FracFocus typically provides both the mass (`MassIngredient`) and the percentage of the whole fracking fluid (`PercentHFJob`), we can calculate the total mass of the fracking fluid from *every record* in a disclosure.  We judge `MassIngredient` values to be internally consistent when this set of calculated total mass values are essentially the same (within a tolerance).  When they are not, we flag the `MassIngredient` values for that disclosure as internally inconsistent and do not use them for comparisons to Open-FF's `calcMass`. Currently there are about 24,000 *disclosures* with inconsistent `MassIngredient`.

|[Prev](Resolving_chemical_identity.md)|[Index](Top.md)|[Next](Standardizing_text_fields.md)|
