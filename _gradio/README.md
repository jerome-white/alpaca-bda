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
model](https://en.wikipedia.org/wiki/Bradley%E2%80%93Terry_model). Given
a collection of items and pairwise comparisons of those items,
Bradley–Terry estimates the "ability" of each item based known
pairwise comparisons. The strength of a given sports team, for
example, based on previous games played. Once calculated, the ability
can be used to estimate the probability that one item will be
better-than another, even if those two items have not been formally
compared in the past. The Alpaca framework is a good opportunity to
apply this model in practice.

This Space has two sections: the first presents a ranking of models
based on estimated ability; the other estimates the probability that
one model will be preferred to another. Metrics in this section are a
result of a pipeline that parses Alpaca data, then estimates ability
using a Bayesian formalization of Bradley–Terry modelled in
[Stan](https://mc-stan.org/). Please see the disclaimer for details of
the workflow, and to put results into perspective.
