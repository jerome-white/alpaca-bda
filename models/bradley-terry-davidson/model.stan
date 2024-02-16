/**
 * Bradley-Terry Model
 **/

data {
  int<lower = 1> K;                          // players
  int<lower = 1> N;                          // pairs
  array[N] int<lower=1, upper = K> player_1; // player 1 for pairs n
  array[N] int<lower=1, upper = K> player_2; // player 2 for pairs n
  array[N] int<lower = 0> win_1;             // number of wins for player 1
  array[N] int<lower = 0> win_2;             // number of wins for player 2
  array[N] int<lower = 0> ties;
}

transformed data{
  array[N] int<lower = 0> n_win;
  array[N] int<lower = 0> n_tie;

   for (i in 1:N) {
      n_win[i] = win_1[i] + win_2[i];
      n_tie[i] = n_win[i] + ties[i];
   }
}

parameters {
  real<lower = 0.001> sigma_beta; // scale of ability variation
  real<lower = 0.001> sigma_nu;
  real<lower = 0> nu;             // Davidson
  vector[K] beta;                 // ability for player n
}

transformed parameters{
  vector[K] w;
  vector[N] p_win;
  vector[N] p_tie;

  w = exp(beta);

  for (i in 1:N) {
    real aux;
    real agg;

    aux = exp(nu + (beta[player_1[i]] + beta[player_2[i]]) / 2.0);
    agg = w[player_1[i]] + w[player_2[i]] + aux;

    p_win[i] = w[player_1[i]] / agg;
    if (is_nan(p_win[i])) { // get some nan errors sometimes
      p_win[i] = 0.0;
    }

    p_tie[i] = aux / agg;
    if (is_nan(p_tie[i])) { // get some nan errors sometimes
      p_tie[i] = 0.0 ;
    }
  }
}

model {
  sigma_beta ~ lognormal(0, 0.5);
  sigma_nu ~ lognormal(0, 0.5);

  beta ~ normal(0, sigma_beta);
  nu ~ normal(0, sigma_nu);

  win_1 ~ binomial(n_win, p_win);
  ties ~ binomial(n_tie, p_tie);
}

/*
generated quantities {
  array[N] int win_1_rep;
  array[N] int tie_rep;
  array[N] real log_lik;

  win_1_rep = binomial_rng(n_win, p_win);
  tie_rep = binomial_rng(n_tie, p_tie) ;

  for (i in 1:N) {
      log_lik[i] =
	binomial_lpmf(ties[i]  | n_win[i], p_tie[i]) +
	binomial_lpmf(win_1[i] | n_win[i], p_win[i]);
  }
}
*/
