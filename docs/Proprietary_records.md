<center> <img src="images/header_logo.png" width="100"/></center>
<!-- this is a test of a comment 
To do:
--->

|[Prev](Standardizing_text_fields.md)|[Index](Top.md)|[Next](Duplication_in_FracFocus.md)|

# Proprietary records

Most states allow companies to designate some chemical records as Trade Secrets.   Within FracFocus, the typical way those designations are expressed is by reporting the `CASNumber` as something like "trade secrets" or "proprietary" or "confidential business information,"  but the format is not standarized and for a user to find all of them is a chore.

In Open-FF's curation of chemical identity, a `bgCAS` value is assigned to "proprietary" when any part of a chemical record explicitly indicates the designation. Although there are many records in FracFocus without indentity information (due to typos, sloppiness or intentional hiding), Open-FF does not assign the "propritary" `bgCAS` without that explicit designation.  Instead, they are usually assigned a `bgCAS` of "ambiguousID."

By labelling all trade secret records with a single label, Open-FF helps users look across all such records to see the big picture of how widely they are used, what companies use them and how their use changes over time.

|[Prev](Standardizing_text_fields.md)|[Index](Top.md)|[Next](Duplication_in_FracFocus.md)|