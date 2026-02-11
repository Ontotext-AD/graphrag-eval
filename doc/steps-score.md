### Steps score

The steps score is a real number in the interval [0, 1], 
which indicates how closely the actual steps match to the reference ones.
A score of 1 indicates a perfect match.

Going in reverse order of the reference groups and in reverse order of the 
actual steps, for each reference group we try to match each step in the group 
to an actual step:
- If all steps from the current reference group are matched, we proceed to the 
previous group, but we only search among the actual steps before the earliest 
actual step already matched for the current group. Thus, we ignore the 
execution order of steps within a reference group, but groups are matched 
in order: actual steps that match earlier groups must be executed before all 
steps matching later groups.
- If some steps in the current reference group are not matched, then the 
matching stops, and the score is computed from the matches found so far.

An actual step can match at most one reference step, and only if the actual 
step is successful (i.e., it didn’t result in an error). There are a few ways 
a reference step can match an actual one. In all cases except for 
the "retrieval" steps, the matching score is either 0 or 1. A score above 0 
indicates a match.

- if both are named "sparql_query" and the "output_media_type" of the 
reference step is "application/sparql-results+json", then we try to match them 
using the [SPARQL queries comparison algorithm](#sparql-queries-comparison).
- if both are named "retrieval" and the reference step has "output", then we 
compute [recall@k](#context-recallk).
- if both are named "retrieve_time_series", then we check if the arguments of 
the steps are matching.
- if both are named "retrieve_data_points", then we check if the arguments of 
the steps are matching.
- if the reference step is named "iri_discovery" and the actual step name is 
"autocomplete_search", тhen check if the IRI specified as "output" of the 
"iri_discovery" step is present in the "output" of the "autocomplete_search".
- if the reference and actual step names are the same and the 
"output_media_type" of the reference step is "application/json", then the steps 
match, if the json outputs are the same. 
- we fallback to match the outputs of the two steps. 

The final steps score is the macro mean of scores over the groups. That is, it 
is the sum of the scores of all reference groups divided by their number. Each 
group score is the sum of scores of its steps divided by their number.

#### SPARQL queries comparison

The algorithm iterates over all subsets of columns in the actual result of the same size as in the reference result.
For each subset, it compares the set of columns (skipping optional columns).
It matches floating-point numbers up to a 1e-8 precision. It does not do this for special types such as duration.

The average time complexity is О(nr\*nc_ref!\*binomial(nc_act, nc_ref)), where

* *nr* is the number of rows in the actual result
* *nc_ref* is the number of columns in the reference result
* *nc_act* is the number of columns in the actual result
