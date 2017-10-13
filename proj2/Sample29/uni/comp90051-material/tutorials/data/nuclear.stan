// Author: Andrew Bennett
// Date: August 2015
//
// Stan file for the nuclear power plant example
// from The University of Melbourne COMP90051 lectures

data {
  int<lower=1> N; // number of observations
  // for each of these, 0 means false, 1 means true
  int<lower=0, upper=1> HT[N];  // whether core temperature high
  int<lower=0, upper=1> FG[N];  // whether gague is faulty
  int<lower=0, upper=1> FA[N];  // whether alarm is faulty
  int<lower=0, upper=1> HG[N];  // whether gague reads high
  int<lower=0, upper=1> AS[N];  // whether alarm sounds

  real<lower=0> ALPHA; // alpha to use for beta distributions
  real<lower=0> BETA; // beta to use for beta distributions
}

parameters {
  //probability table for each variable
  real<lower=0, upper=1> ht_prob;
  real<lower=0, upper=1> fg_prob;  
  real<lower=0, upper=1> fa_prob;
  real<lower=0, upper=1> hg_prob[2,2];
  real<lower=0, upper=1> as_prob[2,2];
}
    
model {
  // likelihood of probability tables
  ht_prob ~ beta(ALPHA, BETA);
  fg_prob ~ beta(ALPHA, BETA);
  fa_prob ~ beta(ALPHA, BETA);
  for (i in 1:2) {
    for (j in 1:2) {
      hg_prob[i, j] ~ beta(ALPHA, BETA); 
      as_prob[i, j] ~ beta(ALPHA, BETA);
    }
  }
  
  // likelihood of observing data
  for (n in 1:N) {
    HT[n] ~ bernoulli(ht_prob);
    FG[n] ~ bernoulli(fg_prob);
    FA[n] ~ bernoulli(fa_prob);
    // +1 in indexing below because Stan arrays count from 1
    HG[n] ~ bernoulli(hg_prob[HT[n]+1, FG[n]+1]);
    AS[n] ~ bernoulli(as_prob[FA[n]+1, HG[n]+1]);
  }
}

