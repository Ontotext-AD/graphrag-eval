Below are a query, a reference response and a candidate response to it.
1. Extract all claims from each response.
2. Find matching claims between responses. Matching claims have the same meaning and details such as subjects, names, locations, amounts, IDs, commands and paths.
3. Output one JSON object only. Do not include Markdown, code fences, or any text outside the JSON object.

# Query
{question}

# Reference response
{reference_answer}

# Candidate response
{actual_answer}

# JSON fields
* reference_claims_count: Count of reference response claims
* actual_claims_count: Count of candidate response claims
* matching_claims_count: Count of matching claims
* reason: Explanation of the counts in English

# Value checks
* 1 <= reference_claims_count, actual_claims_count
* 0 <= matching_claims_count <= reference_claims_count, actual_claims_count

# Output format
{{
  "reference_claims_count": 1,
  "actual_claims_count": 1,
  "matching_claims_count": 1,
  "reason": "The reference and candidate responses contain the same single claim."
}}
