# Approximate Subgraph Matching - Relation Extraction

Code for performing Relation Extraction using the Approximate Subgraph Matching algorithm
Based originally on the NICTA VRL submission to BioNLPST-13.

## Building

First, install the required dependencies:

* ClearNLP with text span tracking (readbiomed clearnlp project)
* JSBD adapted to use Maven (readbiomed jsbd project)
* ESM version 1.1 (not 1.0 -- readbiomed esm project)

The simplest way of doing this is to clone the dependencies hosted in the readbiomed
BitBucket account into a local directory, then changing into the root directory of the
repository associated with each dependency and running:

    `$ mvn install`

This will install the dependency into the local repository used by Maven. On
linux systems this is available in the ~/.m2 directory.

Once all dependencies are installed, clone the asm-re repository, change into
the root directory of the repository and compile using Maven.

    `$ mvn clean compile`

This will compile the code into a 'target' directory, allowing it to be invoked
as described below.

## Running Experiments
Create an 'experiments' directory in the root directory of asm-re to contain
the output from the framework.

    `$ mkdir experiments`

Within the experiments directory, create a symbolic link to subgraph-match.pl,
which is stored in asm-re/src/main/scripts. This is the script used to
configure and execute the framework.

    `$ ln -s ./src/main/scripts/subgraph-match.pl subgraph-match`

The root directory of asm-re should now look as follows:

asm-re
    |- experiments
        |- subgraph-match.pl (symlink)
    |- pom.xml
    |- README.md
    |- src
    |- target

Open subgraph-match.pl and edit the directories on lines 11-17 to point to
the corresponding directories in your local checkout of asm-re (TODO: add more
specific instructions).

When executing subgraph-match.pl, three arguments are expected. If executing
the script from the experiments directory in asm-re the following should work.

    `$ perl subgraph-match.pl ../src/main/scripts TRAIN_DATA OPTIM_DATA TEST_DATA`

Where TRAIN_DATA, OPTIM_DATA and TEST_DATA point to the data used for training,
optimising and testing the framework respectively.
