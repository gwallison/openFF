Although it is controversial for a disclosure instrument, FracFocus allows companies to hide the identity of chemicals in disclosure forms.  The rationale for the so-called 'Proprietary Claim' is that some chemicals in a fracking operation are trade secrets and disclosing them would be a competitive disadvantage for the reporting company.  

The upshot is that throughout the raw FracFocus data are CASNumber values that are not valid CAS registry numbers but text that somehow indicates the proprietary condition.   

However, these claims are not in a consistent format in the raw data.  One might think that there are only two states for the CASNumber field: either a valid CAS registry number or a proprietary claim.  In reality there are many values of CASNumber that are neither.  Therefore, we must actively identify the proprietary values and label them as such in the output data sets.  

Current implemented solution

Starting with version 10 at CodeOcean, Open-FF uses the casing_curation_master.csv file to manually decide which CASNumber/IngredientName pairs are intended to be proprietary claims.  For these pairs, the category and bgCAS are set to "proprietary."  

Previously implemented solution (CodeOcean versions 9 and earlier)

To properly separate those CASNumber values that explicitly make a proprietary claim from the values that also hide the identity of a chemical but not by an explicit claim, we use a translation table approach.  The table (cas_labels.csv in the /data directory of open-FF) has all unique CASNumber values and a column to indicate whether a given value is proprietary or not.