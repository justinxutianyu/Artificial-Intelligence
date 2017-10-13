# README #

#What Do I Do?
Analyse the data. All of it. To do this, follow this handy guide.

1. Make sure you have the latest version of the repository checked out.

2. Run generate_data.py to generate the latest data set.

3. Run an ipython notebook and load the data into memory with the following code:

*import pandas as pd*
*data = pd.read_pickle("./data_frames/clean_data.pkl")*

The data set will now be stored as a Pandas dataframe in the "data" variable.

Have fun! Make sure you save your notebooks for sharing later.

##Useful Libraries
The following Python libraries are good for analysing stuff:

*pandas - what we're using for representing the data. Good for grouping, aggregating etc..

*sklearn - machine learning library. Good for clustering, regression etc.

*numpy - has some basic modelling functions (the polyfit function is kind of cool) which are nice.

*matplotlib - for plotting.