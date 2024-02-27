<center> <img src="images/header_logo.png" width="100"/></center>
<!-- this is a test of a comment 
To do:
--->

|[Prev](Open-FF_overview.md)|[Index](Top.md)|[Next](Resolving_chemical_identity.md)|
# Data Limitations

While FracFocus has a huge repository of data and the Open-FF project tries to correct errors and fill omissions, several important data limitations remain.  It is essential for users of the data to recognize these limitations.

1. Many of the chemicals listed in FracFocus use the Safety Data Sheets from trade-named products to document the concentration of the chemical in the product (`PercentHighAdditive`).  Often, that number is expressed as a range in the Safety Data Sheet and FracFocus instructs the company to use the highest value in the range.  Because this value is used to calculate the overall concentration of the chemical in the Hydraulic fluid (`PercentHFJob`), this may be an overestimate of the actual concentration used and the mass as well.  This apparently applies to the directly reported mass field, `MassIngredient,` also.
2. The mass of many records is not available; thus when aggregate statistics such as total mass used of a chemical is calculated, it is likely to be an underestimate.
3. There are a number of records in which the chemical identity is ambiguous or conflicting.  These records are tagged that way and therefore taken out of the analysis of known chemicals, again, leading to underestimates.
4. There are, unfortunately, many chemicals added to the well during that do not make it onto the disclosures.  These include the records designated as proprietary, chemicals that are not listed on Safety Data Sheets because they were deemed "inert" or "non-hazardous" by the manufacturer, the additional chemicals besides water that are included in the carrier (produced water is a growing source of water), and the component chemicals of the many UVCB materials used.  All of these will lead to underestimates of mass and incomplete chemicals lists.
5. A disclosure format commonly used in FracFocus called **Systems Approach**, reports individual chemicals and their quantities separately from the products that contain them (such as the trade-named products), their suppliers and purposes.  This disconnect between chemical and product and cheical and supplier limits our ability to connect, say, a toxic chemical with the product that contains it and the company that supplies or manufactures it.  As of Feb 2024, The Systems Approach format is the default format for data entry.
