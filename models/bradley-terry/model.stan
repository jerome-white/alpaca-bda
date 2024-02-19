/**
 * Bradley-Terry Model
 *
 * Modified from the Stan development team
 **/

data {
  int<lower=1> K; // players
  int<lower=1> N; // games
  array[N] int<lower=1, upper=K> player_1; // player 1 for game n
  array[N] int<lower=1, upper=K> player_2; // player 0 for game n
  array[N] int<lower=0, upper=1> y;        // winner for game n
}

parameters {
  vector[K] alpha;         // ability for player k
  real<lower=0.001> sigma; // scale of ability variation
}

model {
  sigma ~ lognormal(0, 0.5); // boundary avoiding
  alpha ~ normal(0, sigma);  // hierarchical
  y ~ bernoulli_logit(alpha[player_1] - alpha[player_2]);
}
