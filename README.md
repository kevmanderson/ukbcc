ukbcc
===============================

version number: 0.1.16

authors: Isabell Kiral, Nathalie Willems, Benjamin Goudey

Overview
--------

Tool for curation of UK Biobank data to generate cohorts. The tool can filter the main and associated datasets (e.g GP Clinical data) based on search terms provided by the user. It can be used interactively through a command line interface, or imported as a module and integrated into a broader pipeline. Additional functionality, such as automatically downloading large data files (bulk data) is also supported.

Prerequisites
--------

* The provided tool is developed for Python version 3 and can be imported as a package as described below.
* The *`interactive mode`* is developed to be run in the command line and has been developed for and tested on MacOS and Linux systems.
<!--* Some functionality, particularly automated download of files, relies on running a headless browsers. To make sure this runs smoothly, please follow the steps below

### Enabling UKBB direct access to Primay Care databases
1. download [driver](https://chromedriver.storage.googleapis.com/index.html?path=83.0.4103.14/)
2. unzip downloaded file
3. add the directory to the path (`export PATH=$PATH:<pathToInstallation>`)
4. execute driver once to make sure your computer trust the distributor (on mac: right click, open, trust developer. double click will not work)
5. during installation of `ukbcc`, a credentials.conf file will be created if it doens't exist already. Enter correct credentials (application ID, user name, and password) to access UKBB or use file as a template to create your own in the location of choice.
For Firefox:
1. download [driver](https://github.com/mozilla/geckodriver/releases)
2. unzip downloaded file
3. add the directory to the path (`export PATH=$PATH:<pathToInstallation>`)
4. during installation of `ukbcc`, a credentials.conf file will be created if it doens't exist already. Enter correct credentials (application ID, user name, and password) to access UKBB or use file as a template to create your own in the location of choice.-->

Installation
--------

Installing using pip (or pip3):

    $ pip3 install git+shh://git@github.com:tool-bin/ukbcc.git

Installing using pip (pip3) from particular branch

    $ pip3 install git+shh://git@github.com:tool-bin/ukbcc.git@branchname


Or clone the repo:

    $ git clone https://github.com/tool-bin/ukbcc.git
    $ python setup.py install

Usage
--------

There are two ways to use with this module:
1. Running the module from the command line and leveraging the *`interactive mode`* features to dynamically generate cohorts on the fly.
2. Importing the module into an existing pipeline, and using the functions developed to interact with the UKBB databases.

There is more detailed information in [our paper](https://www.biorxiv.org/content/10.1101/2020.07.12.199810v1), if you're interested.

### Downloads
In order to make full use of this module, you will need to download the following files:
* `main_dataset.csv`: The main dataset as downloaded from UK Biobank. Please follow UKBB instructions to obtain this file.
* `showcase.csv` and `codings.csv`: Files that can be found in the data_files directory within this repo in their current version. A function is provided to download potentially updated files from the UKBB server. These files contain descriptions of columns in the main dataset as well as associated codes.
* `readcodes.csv`: A file linking readcodes to descriptions for the 'gp_clinical' table in the UKBB data portal. This file can be found in the data_files directory within this repo.
* `gp_clinical.txt`: The full general practioner (GP) clinical data that forms part of the primary care dataset. The full table (gp_clinical) can be downloaded from the UKBB data portal website. A function is provided to download this dataset automatically by executing the **`ukbcc`** command. Downloading this file is optional, but will provide the most comprehensive search for participants to generate cohorts. Instructions are provided below.
<!-- * [`lookupCodeDescriptions.csv`](https://github.ibm.com/aur-genomics/modellingScripts/blob/master/isabell/cohortPipeline/lookupCodeDescriptions.csv): A file that maps descriptions to codes for the following formats: ICD9, ICD10, read_2, read_3.
* [`coding19.tsv`](https://github.ibm.com/aur-genomics/modellingScripts/blob/master/isabell/cohortPipeline/coding19.tsv): A file that maps the `node_id`s from the main dataset to ICD10 codes.    -->

### Downloading the GP clinical dataset
The GP clinical dataset can be downloaded directly from the UK Biobank showcase website, through the Data Portal webpage. Instructions for how to download this file are provided below:
1. Log into the UK Biobank showcase website (https://bbams.ndph.ox.ac.uk/ams/resApplications)
2. Navigate to your Project by clicking the "Project" button on the left-hand side of the page
3. Click on the "Data" tab on the right of the page
4. Click on the "Go to Showcase" tab - this will take you to the UK Biobank Showcase landing page
5. Click the "Data Portal" tab and click on the "Connect" button. Note! The user requires access permissions to access the Data Portal webpage - if you do not see this button, you do not have access to this page.
6. Click on the "Table Download" button
7. Type in "gp_clinical" into the search bar and click the "Fetch Table" button
8. Click on the generated link. This will automatically start downloading the gp_clinical table, as tab-separated plain-text file.
9. Provide the path and name of the GP clinical file to the main.py module in order to use this dataset within the *`interactive`* mode of the UKBCC module

## Interactive mode

There are two ways to run *`interactive mode`*:
1. Through a web-based interface
2. Through a command-line interface

### Web-based interface

In order to run the web-based interface, please run the following commands:
1. Navigate to the **"webapp"** folder
2. Execute:

    $ python index.py

3. The above command will setup the web-based interface and generates a web address where this can be accessed:

![Alt text](images/web_setup.png?raw=true "Start web-interface")

4. Paste the generated web address into a web browser.
5. Follow the web page instructions to use the tool.


### Command-line interface

In order to use the command-line interface functionality, the module can simple be called from the command line.

1. To start the configuration process, type:
```shell
$ ukbcc
```
<!-- If interaction with the portal is not necessary because all files are local, no configuration file is necessary.
Use the `portal_access` flag and provide the location and filename of the gp_clinical dataset:
```shell
$ ukbcc --portal_access False --gp_clinical_file ./pathtodata/gp_clinical.txt
``` -->
2. You will be asked to provide certain information. Make sure to provide the full or relative path (and filename if asked).
```shell
>> Please specify directory for config file [`.` for current directory]:
>> Please specify the full path and name of main dataset:
>> Please specify the full path and name of the GP clinical dataset - if you do not want to query this dataset, please type "No"
>> Please specify the name of the file to store the list of ids for the cohort:
```
The created config and credentials files can be reused in subsequent runs, using flags:
```shell
$ ukbcc --config ./config.conf
```
3. You will be asked to specify search terms used to generate the cohort (e.g `glaucoma`, `optical cohorence tomography`). Provide them as a comma-separated list:
```shell
>> Please enter comma-separated search terms: glaucoma, optical coherence tomography
```
4. Go through all fields that may be relevant and decide if a field or condition will be of interest or not. This process can take some time.
5. For all included fields and conditions, you will then be asked to provide logical pointers. Choose if all participants should have a certain condition, none of them, or if every participant should have any of a number of different conditions. Refer to the graphic below for a visual explanation of the logic pointers.

Once these selections are made, the module will query the UKBB databases in order to generate a list participants IDs that match the specified criteria. These IDs can then be used in downstream processing and analysis pipelines, for example generating statistics about the cohort (**stats** module), or downloading bulk imaging files for the individuals within the cohort (**bulk** module).

There are 3 files that will be created by running the module in *`interactive mode`*:
1. cohort_criteria -- this file contains the dictionary data structure that is created as part of the selection of desired datafield:code combinations (step 2 above)
2. cohort_criteria_updated -- this file contains the update dictionary data structure with the appropriate conditional logic (step 3 above)
3. out_filename -- this file contains the list of participant IDs that match the criteria for the cohort. out_filename is a placeholder for the file name specified during the Configuration process (step 1)

The module will write all the relevant files to the specified output directory. As such, the generated dictionary data structure can be updated and reused in other pipeplines (e.g when importing the module within an existing pipeline).


<!-- 1. Configuration process: specify paths to the main dataset and optionally the gp_clinical datasets
![Alt text](images/config_process.png?raw=true "Configuration Process")
2. Cohort generation process: specify search terms used to generate the cohort (e.g `glaucoma`, `optical cohorence tomography`)
![Alt text](images/search_terms.png?raw=true "Search Terms")
3. Selection of desired datafield:code combinations (e.g datafields with codes that refer to conditions of `glaucoma`)
![Alt text](images/cohort_selection.png?raw=true "Datafield:code Selection")
4. Selection of conditional logic to apply (e.g all participants can have *`any of`* the subtypes of `glaucoma`)
![Alt text](images/update_inclusion_logic.png?raw=true "Conditional Logic") -->

## Stand-alone mode

The ukbcc module uses dictionaries in order to represent the various datafield:code combinations and conditional logic to be applied in generating a cohort.
This dictionary will be automatically generated through the *`interactive mode`*.
Alternatively, the user can write this dictionary themselves, and use the **query** submodule to further interact with UKBB databases.
Further information about the expected structure of the dictionary is provided in the docstrings of the functions within this module.
It is recommended the user leverage the `interactive mode` if using the ukbcc module for the first time.

To learn about how to use modules in this package in your existing pipeline, see example-module notebook in the examples directory in this repo.

Contributing
------------

As a collaborator, please make a branch and create a pull request when ready.
To contribute otherwise, please fork directory and create pull requests.
Github issues are also welcome.

Citation
------------

If you found this tool useful in your work, please use the following citation:
--INSERT CITATION--
