#Import the function to profile here
from peerConnections import test

import argparse
import cProfile
import pstats

def profile(function, resultsFile):
    print("Profiling function {}".format(function))
    cProfile.run(function, resultsFile)
    print("Results written to {}".format(resultsFile))

def printStats(resultsFile):
    p = pstats.Stats(resultsFile)
    p.strip_dirs().sort_stats(1).print_stats(20)

def main():
    profile("test()", "results.prf")
    printStats("results.prf")

if __name__ == "__main__":
    #This doesn't work but it'd be cool if it did =)
    #Parse all the arguments
    #parser = argparse.ArgumentParser()
    #parser.add_argument("-f",   "--file",
    #                    help="File to profile")
    #parser.add_argument("-fn", "--function",
    #                    help="Function to profile. Must exist within file.")
    #args = parser.parse_args()
    #Run all the things
    main()
