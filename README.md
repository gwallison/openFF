<center> <img src="docs/images/header_logo.png" width="100"/></center>
<!-- this is a test of a comment 
To do:
--->

# Open-FF

An open source project to make the fracking industry's chemical disclosures accessible 


[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10050984.svg)](https://doi.org/10.5281/zenodo.10050984)

---

   
|[Read <br>the documents](docs/Top.md)|[Browse <br>the data](https://storage.googleapis.com/open-ff-browser/Open-FF_Catalog.html)|[Visit <br>the Blog](https://frackingchemicaldisclosure.wordpress.com/)|
| --- | --- | --- |
---

# Summary
The [FracFocus.org website](https://fracfocus.org/) serves as the “national hydraulic fracturing chemical disclosure registry” for the US fracking industry. It contains over 200,000 disclosures of fracking events, encompassing approximately 6 million individual chemical records.  Besides chemical identity and quantity, this data set is rich in details about water usage, operator and supplier companies, and trade-named products (as well as a large number of proprietary claims) throughout a major portion of the twenty-first century's fracking boom.

However, FracFocus is underutilized as a research resource because it is full of errors, contains multiple formats, and many important features are obscured or not standardized(). It is a major undertaking to prepare the FracFocus data for all but trivial research questions.  In addition, FracFocus data is frustratingly opaque to non-expert members of the public that may be directly impacted by the environmental and health effects of fracking and have no access to better information.

The Open-FF project aims to remedy these issues to provide an independent, free and reliable source of the industry’s own chemical reporting. At its core, Open-FF simply takes the FracFocus data and pairs it with corrections, clarifications, calculations, and alerts that add perspective to the industry’s published data.  This core data set is then packaged in a number of ways to make it available online to everyone from the hard-core data analyst to the non-technical casual browser.  

The project uses a combination of automated methods and manual curation to remove much of the ambiguity of both chemical identification and quantity in the FracFocus data.

Open-FF’s development between 2019 and 2023 is documented at [CodeOcean](https://doi.org/10.24433/CO.1058811.v16) and is currently being developed at GitHub. Publications using the Open-FF data include [an analysis of chemicals regulated](https://doi.org/10.1016/j.envpol.2022.120552) by the Safe Drinking Water Act, from which the industry has been exempted and [examinations of PFAS](https://psr.org/wp-content/uploads/2022/01/fracking-with-forever-chemicals-in-colorado.pdf) use and [trade secret claims](https://doi.org/10.1016/j.jenvman.2023.119611).  Up-to-date data sets and an online data browser are currently maintained through the sponsorship by [the FracTracker Alliance](https://www.fractracker.org/).


# Installation

Important Note: **Installing Open-FF code is NOT required to *use* the Open-FF data.**  The data is available in a number of ways online and is updated frequently.  The installation notes below are provided for those users who wish to modify the data set generation process.

The code in this repository has been designed to run in a python environment. To create such an environment on a local machine, you can:
- Download and install [Anaconda](https://www.anaconda.com/download)  Once completed, you should be able to open an Anaconda prompt.
- Set up a local environment for Open-FF work.  You will use this for just about everything:
    - In an Anaconda prompt, navigate to your working directory (I use "c:\MyDocs") and create a new environment named "openff"
    > conda create --name openff
    - To enter this environment, you will use this command:  
    > conda activate openff
- Install the modules for this environment.  First activate the environment (above), then execute each of the following:

    > conda install spyder

    > pip install geopandas

    > conda install -c conda-forge matplotlib jupyterlab geopy openpyxl ipyleaflet pyarrow plotly nodejs folium pytest statsmodels seaborn reportlab xlrd

    > pip install requests-html

    > pip install itables

A simpler approach may be to execute the code remotely.  You can use services such as Google's Colaboratry.  The notebooks of this repository are setup to run in Colab. 
