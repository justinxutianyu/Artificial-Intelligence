"""
Demo Main Function

Author:
Kai Hirsinger (kai.hirsinger@gmail.com)

Since:
25th September 2015

Re-generates raw/clean data sets stored in the
data_frames directory. This should be re-run
each time changes are made the data extraction/cleaning
pipeline.
"""

from explorer.loaders import Project2Data

RAW_DATA   = "./data_frames/raw_data.pkl"
CLEAN_DATA = "./data_frames/clean_data.pkl"

def main():
    #Initialise the loader object
    data = Project2Data()

    print("generating raw data")
    data.load_data()
    raw = data.to_dataframe()
    raw.to_pickle(RAW_DATA)

    print("generating clean data")
    data.clean_data()
    clean = data.to_dataframe()
    clean.to_pickle(CLEAN_DATA)

if __name__ == "__main__":
    main()
