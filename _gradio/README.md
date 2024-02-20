[Alpaca](https://github.com/tatsu-lab/alpaca_eval) is an LLM
evaluation framework. It maintains a set of prompts, along with
responses to those prompts from a collection of LLMs. It then presents
pairs of responses to a judge that determines which response better
addresses the prompt. Rather than compare all response pairs, the
framework identifies a baseline model and compares all models to
that. The standard method of ranking models is to sort by baseline
model win percentage.

This Space presents an alternative method of ranking based on the
[Bradley–Terry
model](https://en.wikipedia.org/wiki/Bradley%E2%80%93Terry_model)
(BT). Given a collection of items, Bradley–Terry estimates the
_ability_ of each item based on pairwise comparisons between them. In
sports, for example, that might be the ability of a given team based
on games that team has played within a league. Once calculated,
ability can be used to estimate the probability that one item will be
better-than another, even if those items have yet to be formally
compared.

The Alpaca project presents a good opportunity to apply BT in
practice; especially since BT fits nicely into a Bayesian analysis
framework. As LLMs become more pervasive, quantifying the uncertainty
in their evaluation is increasingly important. Bayesian frameworks are
good at that.

This Space is divided into two primary sections: the first presents a
ranking of models based on estimated ability. The figure on the right
presents this ranking for the top 10 models, while the table below
presents the full set. The second section estimates the probability
that one model will be preferred to another. A final section at the
bottom is a disclaimer that presents details about the workflow.
