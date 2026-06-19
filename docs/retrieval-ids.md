# Retrieval evaluation using chunk IDs

[← README](../README.md)

The following metrics are based on the IDs of retrieved document chunks.

## Context recall@k

The fraction of the first $k$ relevant IDs that appear in the top $k$ retrieved IDs.

### Formula

$$
\frac{\text{Number of relevant items in top k}}{\min(k, \text{Number of relevant items})}
$$

## Computation

Count how many IDs appear in both the first $k$ relevant IDs and the first $k$ retrieved IDs; divide by the number of relevant IDs considered, i.e., `min(k, len(relevant_ids))`.

### Example

Suppose there are 4 relevant documents for a given query. Suppose our system retrieves 3 of them in the top 5 results (`k=5`). Then `recall@5` is `3 / 4 = 0.75`.

```python
recall_at_k(
    relevant_ids=[1, 3, 5, 6],
    retrieved_ids=[1, 4, 3, 5, 7],
    k=5,
)  # => 0.75
```

## Average Precision (AP)

Evaluates a ranked list of recommendations by looking at the precision at the position of each correctly retrieved item. It rewards systems for placing relevant items higher up in the list. It's more sophisticated than just looking at precision at a single cutoff because it considers the entire ranking.

### Formula

$$
\frac{\sum_{k=1}^{n} (P(k) \times \text{rel}(k))}{\text{Number of relevant items}}
$$

where:
- $P(k)$ is the precision at rank $k$
- $rel(k)$ is 1 if the item at rank $k$ is relevant and 0 otherwise.

### Computation

1. For each retrieved item, if it is relevant, record the precision at
    that index (i.e., `number of hits / current rank`).
2. Sum all of these precision scores.
3. Divide the sum by the total number of relevant items.

### Example

Suppose:
* The relevant items are `1, 3, 5, 6`
* Our system retrieves `1, 4, 3, 5, 7`

Computation:
* Item at index 1 (item 1) is relevant. Precision@1 = 1/1
* Item at index 3 (item 3) is relevant. Precision@3 = 2/3
* Item at index 4 (item 5) is relevant. Precision@4 = 3/4
* AP = (1.0 + 2/3 + 3/4) / 4 = 0.60416...

```python
average_precision(
    relevant_ids=[1, 3, 5, 6],
    retrieved_ids=[1, 4, 3, 5, 7],
)  # ~=> 0.60416
```
