# Steps evaluation

If a reference answer specifies reference steps and the target answer specifies
the actual steps taken by the target agent, then the library tries to match
steps in the two sets and computes match scores (Section
[Steps matching](#steps-matching)). It outputs the matches and an overall
`steps_score` for the question (section [Steps score](#steps-score)).

The matches are also used to compute quality metrics for "retrieval" steps
if the necessary input variables are supplied. (section [Metrics](metrics.md).)

The reference can specify some constraints on step execution order.
Specifically, reference steps are specified as an ordered list of "groups", 
while each group is not ordered, as illustrated below:

```
+-----Reference answer----+
|        (ordered)        |
|                         |
|  +------Group 1------+  |
|  |    (unordered)    |  |                  +---Actual answer---+
|  |                   |  |                  |                   |
|  |  +--> Step A      |  |                  |                   |
|  |  |                |  |                  |                   |
|  |  |    Step B <------------matches-------------> Step B      |
|  |  |                |  |                  |                   |
|  +--|----------------+  |                  |                   |
|      \                  |                  |                   |
|       +--------------------- matches-------------> Step A      |
|                         |                  |                   |
|  +------Group 2------+  |                  |                   |
|  |    (unordered)    |  |                  |                   |
|  |                   |  |                  |                   |
|  |       Step C <------------matches-------------> Step C      |
|  |                   |  |                  |                   |
|  +-------------------+  |                  +-------------------+
+-------------------------+                  
```

## Steps matching

The library tries to match steps in reference groups to actual steps, such that:

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

The output contains the reference groups where each step that has a matching
actual step, the actual step's ID is keyed by the additional key `matches`.

## Match score

The match score quantifies how well a reference step aligns with an actual
step. Scores are 0 (no match) or 1 (full match), except for "retrieval" steps,
where scores range between 0 and 1. A score greater than 0 indicates at least
a partial match.

The match score of a reference step to an actual step is computed by following
these rules in order:

- if both steps are named `sparql_query` and the reference step's
`output_media_type` is `application/sparql-results+json`:
  - match score = [SPARQL queries comparison](#sparql-queries-comparison)
- if both steps are named `retrieval` and the reference step has key `output`:
  - match score = [recall@k](retrieval-ids.md#context-recallk)
- if both steps are named `retrieve_time_series`:
  - match score = 1 if the steps have the same sets of arguments, otherwise 0
- if both steps are named `retrieve_data_points`:
  - match score = 1 if the steps have the same sets of arguments, otherwise 0
- if the reference step name is `iri_discovery` and the actual step name is 
`autocomplete_search`:
  - match score = 1 if the reference (`iri_discovery`) `output` (an IRI)
  is present in the actual (`autocomplete_search`) step `output`, otherwise 0
- if the step names are the same and the reference step `output_media_type` is
  `application/json`:
  - match score = 1 if the json outputs are identical, otherwise 0
- match score = 1 if the outputs are identical, otherwise 0

## SPARQL queries comparison

To check whether an actual SPARQL query matches a reference SPARQL query, we
compare their results. This does not work for certain types of queries:

- If one query is SELECT or ASK and the other is a DESCRIBE or CONSTRUCT, they
do not match (the score is 0).

For all other queries, we compare their results as follows:

- If the reference result has $n$ columns, consider all subsets of $n$ columns
in the actual result
- For each subset and for each column in it, look for its matching reference
column by comparing each reference column listed under `required_columns`
- Two columns match if all rows have matching values
- Text values and special types such as duration must match exactly
- Floating-point numbers must match up to a precision of 1e-8

The algorithm has average time complexity

$$
O(|\text{rows}| \cdot { |\text{cols}_{\text{ref}}| }! \cdot \binom{|\text{cols}_{\text{act}}|}{|\text{cols}_{\text{ref}}|})
$$

where:

- $\text{rows}$ = the set of rows in the actual result
- $\text{cols}_\text{ref}$ = the set of columns in the reference result
- $\text{cols}_\text{act}$ = the set of columns in the actual result

## Steps score

`steps_score` is a metric of the overall correctness of the steps the agent
executed to respond to the user's query. It can be used to understand how to
improve the agent.

`steps_score` is a real number in the interval [0, 1] which indicates how
closely the actual steps match the reference steps. A score of 1 indicates a
perfect match.

`steps_score` is computed as the macro mean of scores of individual steps over
the reference steps groups. That is, it is the sum of reference groups scores
divided by the number of groups. Each group score is the sum of scores of its
matching steps divided by the number of steps in the group:

$$
\text{steps\\_score} = \frac{1}{|G|} \sum_{g \in G} \left( \frac{1}{|g|} \sum_{m \in \text{matches}(g)} \text{score}(m) \right)
$$

where:

- $G$ = the set of reference groups
- $|g|$ = the number of steps in group $g \in G$
- $T$ = the sequence of actual steps $ \langle t_1, t_2, ... \ringle $
- $\text{score}(\langle s, t \rangle)$ = the score of $s \in g$ with actual
step $t \in T$
- $\text{matches}(g)$ = $\\{ \langle s, t \rangle \mid s \in g, t \in T, \text{score}(\langle s, t \rangle) > 0 \\}$
