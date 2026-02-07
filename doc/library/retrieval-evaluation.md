### Retrieval Evaluation

The following metrics are based on the content of retrieved documents.

#### Context Recall@k

The fraction of relevant items among the top *k* recommendations. It answers the question: "Of all items the user cares about, how many did we include in the first k spots?"
* **Formula**:
    $`
    \frac{\text{Number of relevant items in top k}}{\text{Number of relevant items}}
    `$
* **Calculation**: Count the number of relevant items in the top `k` retrieved results; divide that by the first 'k' relevant items.
* **Example**: Suppose there are 4 relevant documents for a given query. Suppose our system retrieves 3 of them in the top 5 results (`k=5`). Recall@5 is `3 / 4 = 0.75`.

```python
recall_at_k(
    relevant_docs={1, 3, 5, 6},
    retrieved_docs=[1, 4, 3, 5, 7],
    k=5
)  # => 0.75
```

#### Context Precision@k

Evaluates a ranked list of recommendations by looking at the precision at the position of each correctly retrieved item. It rewards systems for placing relevant items higher up in the list. It's more sophisticated than just looking at precision at a single cutoff because it considers the entire ranking.
* **Formula**:
    $`
    \frac{\sum_{k=1}^{n} (P(k) \times \text{rel}(k))}{\text{Number of relevant items}}
    `$,\
    where:
    * `P(k)` is the precision at rank `k`
    * `rel(k)` is 1 if the item at rank `k` is relevant and 0 otherwise.
* **Calculation**:
    1. For each retrieved item, if it is relevant, record the precision at that index (i.e., `number of hits / current rank`).
    2. Average all of these precision scores.
    3. Divide that average by the total number of relevant items.
* **Example**:
    * Suppose:
      * The relevant items are `1, 3, 5, 6`
      * Our system retrieves `1, 4, 3, 5, 7`
    * Calculation:
      * Item at index 1 (item 1) is relevant. Precision@1 = 1/1
      * Item at index 3 (item 2) is relevant. Precision@3 = 2/3
      * Item at index 4 (item 5) is relevant. Precision@4 = 3/4
      * AP = (1.0 + 2/3 + 3/4) / 3 = 0.8055...

```python
average_precision(
    relevant_docs={1, 3, 5, 6},
    retrieved_docs=[1, 4, 3, 5, 7]
) # ~=> 0.8056
```
