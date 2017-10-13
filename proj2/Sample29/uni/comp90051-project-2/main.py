"""
Demo Main Function

Author:
Kai Hirsinger (kai.hirsinger@gmail.com)

Since:
25th September 2015

This demonstrates how to load the project 2
data into memory. In a general sense we load
the data from Excel into a Python class
representation, then coerce that representation
into a Pandas dataframe.


"""

from explorer.loaders import Project2Data

def main():
    #Initialise the loader object
    data = Project2Data()

    print("loading data")
    data.load_data()
    print("cleaning data")
    data.clean_data()

    #Coerce the data into a dataframe
    data = data.to_dataframe()
    print(data)

if __name__ == "__main__":
    main()
