# The China Study -- Raw Data

This is an attempt to make the original data of [The China Study](https://en.wikipedia.org/wiki/The_China_Study) more accessible.

The data was previously available from [this page of Oxford University](http://www.ctsu.ox.ac.uk/~china/monograph/),
but the link is dead by now.
Fortunately, it is still possible to retrieve the data from the internet archive. Specifically:

- The [main page](https://web.archive.org/web/20120203022945/http://www.ctsu.ox.ac.uk/~china/monograph/) containing PDFs
  describing the study. 
- The [Download mortality and survey data](https://web.archive.org/web/20120208141622/http://www.ctsu.ox.ac.uk/~china/monograph/chdata.htm)
  subpage containing various CSVs.
  
As the page states:

> These files are not particularly user-friendly

This repo comes with a re-structured version of the data to make it easier to work with.
The repo structure is:

- All original PDF documents are stored in the [original_documents](original_documents) subfolder.
- All original data is stored in the [original_data](original_data) subfolder.
- The [data](data) folder contains the re-structured CSVs.
- The [src](src) folder contains the scripts to convert the original CSVs.


## Direct links to original documents

- [Foreword](original_documents/Mono_Foreword.pdf)
- [Study description and methods](original_documents/Mono_Study_Description.pdf)
- [Summary statistics for all 639 variables](original_documents/Mono_Statistic_Summary.pdf)
- [Mortality rates](original_documents/Mono_Mortality.pdf)
- [Laboratory measurements](original_documents/Mono_Laboratory.pdf)
- [Diet survey intake](original_documents/Mono_Diet_Survey.pdf)
- [Questionnaire responses](original_documents/Mono_Questionnaire_Surveys.pdf)
- [Full listings of the six questionnaires](original_documents/Mono_Questionnaires.pdf)
- [ANNEX: Age-specific deaths and death rates in urban and rural China](original_documents/Mono_Annex.pdf)


## Explanatory notes

I didn't spend much time understanding the data, here is my take on it:

- There are actually 4 datasets: 83, 89, 93, and TAI. 
  The first three are data collections from mainland China in different years;
  the latter is for Taiwan.
  If I understand it correctly, only 83 and 89 were used in The China Study.
- In the original data, the datasets are split into different CSV files.
  They share the columns `County`, `Sex`, and `Xiang`.
  Other variables come from the individual files:
  
    - The "M" file contains mortality variables.
    - The "PRU" file contains plasma, red blood cell and urine variables.
    - The "DG" file contains diet and geographic variables.
    - The "Q" file contains questionnaire variables.
    
 - The meaning of the column names is documented in [original_data/CHNAME.TXT](original_data/CHNAME.TXT).
 - All data rows are indexed by `County`, `Sex`, and `Xiang`.
   What makes this a bit confusing is that some rows are aggregates of other rows.
   If I understand it correctly:
   In the best case, the data of a `County` was collected individually 
   for sex and two randomly chosen "xiangs" (= smaller administrative areas).
   The subgroups can be access in the data by selecting rows with `Sex == "F"`, `Sex == "M"`,
   `Xiang == 1`, `Xiang == 2`.
   However some variables are missing on the subgroup level.
   The data also contains the group aggregates in rows with `Sex == "T"` and/or `Xiang = 3`.
   In many cases only this combined aggregate is available.
   
 
 ## Re-structured data
 
 What the conversion script does:
 - Joins the data together on the `County`, `Sex`, and `Xiang` columns.
 - Applies the column names from [original_data/CHNAME.TXT](original_data/CHNAME.TXT).
 - Handles missing data
 