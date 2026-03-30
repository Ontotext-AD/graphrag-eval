# Steps score

The steps score is an overall metric of the correctness of the steps the agent
executed to respond to the user's query. It can be used to understand how to
improve the agent.

The steps score is a real number in the interval [0, 1] which indicates how
closely the actual steps match the reference steps. A score of 1 indicates a
perfect match.

Recalling that reference steps are specified in groups, the steps score is
computed as the macro mean of scores of individual steps over the groups. That
is, it is the sum of reference groups scores divided by the number of groups.
Each group score is the sum of scores of its matching steps divided by the
number of steps in the group:

$$
\text{steps\\_score} = \frac{1}{|G|} \sum_{g \in G} \left( \frac{1}{|g|} \sum_{match \in \text{matches}(g)} \text{score}(match) \right)
$$

where:

- $G$ = the set of reference groups
- $|g|$ = the number of steps in group $g \in G$
- $T$ = the sequence of actual steps $ \langle t_1, t_2, ... \ringle $
- $\text{score}(\langle s, t \rangle)$ = the score of $s \in g$ with actual
step $t \in T$
- $\text{matches}(g)$ = $\{ \langle s, t \rangle \mid s \in g, t \in T, \text{score}(\langle s, t \rangle) > 0 \}$

## Steps matching

To compute the steps score, we try to match steps in reference groups to actual
steps, such that:

- Each reference step matches a unique actual step
- The actual step was successful (i.e., it didn’t result in an error)
- The actual step occurred before all steps matching later groups
- (Within a reference group, actual steps can be matched regardless of the
order in which they were executed)
 
The matching algorithm is as follows:

- Examine reference groups and actual steps in reverse order
- If all steps in the group are matched, then proceed to the previous group,
matching actual steps executed before the earliest actual step already matched
for the current group.
- If some steps in the group are not matched, then stop matching and compute
the score from the matches found so far.

## Match score

The match score quantifies how well a reference step aligns with an actual
step. Scores are 0 (no match) or 1 (full match), except for "retrieval" steps,
where scores range between 0 and 1. A score greater than 0 indicates at least
a partial match.

Matching of a reference step to an actual step works as follows:

- if both steps are named "sparql_query" and the "output_media_type" of the 
reference step is "application/sparql-results+json", then compare the steps
using [SPARQL queries comparison](#sparql-queries-comparison).
- if both steps are named "retrieval" and the reference step has "output", then
compute [recall@k](retrieval-evaluation-using-chunk-ids.md#recall-k).
- if both are named "retrieve_time_series", then check if the arguments of 
the steps match.
- if both are named "retrieve_data_points", then check if the arguments of 
the steps match.
- if the reference step is named "iri_discovery" and the actual step name is 
"autocomplete_search", then check if the IRI specified as "output" of the 
"iri_discovery" step is present in the "output" of the "autocomplete_search".
- if the reference and actual step names are the same and the 
"output_media_type" of the reference step is "application/json", and the json
outputs are the same then the steps match.
- match the outputs of the two steps.

## SPARQL queries comparison

To check whether an actual SPARQL query matches a reference SPARQL query, we
compare their results. This does not work for certain types of queries:

- If one query is SELECT or ASK and the other is a DESCRIBE or CONSTRUCT, they
do not match (the score is 0).

For all other queries, we compare their results as follows:

- If the reference result has $n$ columns, consider all subsets of $n$ columns
in the actual result
- For each subset and for each column in it, look for its matching reference
colum by comparing reference columns in turn (skipping optional columns)
- Two columns match if all rows have matching values
- Text values and special types such as duration must match exactly
- Floating-point numbers must match up to a precision of 1e-8

The algorithm has average time complexity

$$
O\left( |\text{rows}| \cdot |\text{cols}_{\text{ref}}| \cdot \frac{ { |\text{cols}_{\text{act}}| }!}{(|\text{cols}_{\text{act}}| - |\text{cols}_{\text{ref}}|)! \cdot |\text{cols}_{\text{ref}}|!} \right)
$$

where:

- $\text{rows}$ = the set of rows in the actual result
- $\text{cols}_\text{ref}$ = the set of columns in the reference result
- $\text{cols}_\text{act}$ = the set of columns in the actual result
