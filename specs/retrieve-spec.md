# Spec: `retrieve()`

**File:** `retriever.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Given a user's natural language query, find the most relevant chunks from the vector store using semantic similarity search. Return them ranked by relevance so that `generate_response()` can use them as context.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The user's natural language question |
| `n_results` | `int` | Maximum number of chunks to return (default: `N_RESULTS` from `config.py`) |

**Output:** `list[dict]`

Each dict in the returned list must contain exactly these keys:

| Key | Type | Description |
|-----|------|-------------|
| `"text"` | `str` | The chunk text |
| `"game"` | `str` | The game name this chunk came from |
| `"distance"` | `float` | Cosine distance score — lower means more similar to the query |

Results should be ordered from most to least relevant (lowest to highest distance). Returns an empty list `[]` if the collection contains no documents.

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Query approach

*Describe how you will use `_collection.query()` to find relevant chunks. What arguments will you pass, and why?*

```
I will use the query to return a semantic similarity search against the chunks stored in ChromaDB. I will pass in the user query to compare, n_results to limit top chunks, and include "documents", "metadatas", and "distances" to identify which game each chunk is from and their similarity score. 
```

---

### Return structure

*Sketch out what one item in your return list looks like as a concrete example. Where does each field come from in the query results?*

```
{
    "ids": [["catan_1", "catan_0"]],
    "documents": [[
        "Catan is a strategy board game for 3–4 players (5–6 with an expansion).",
        "expansion). Players take on the roles of settlers, building roads,"
    ]],
    "metadatas": [[
        {"game": "Catan"},
        {"game": "Catan"}
    ]]
}
```

---

### Handling the nested result structure

*`_collection.query()` returns nested lists. Describe what index you need to access to get the actual list of results for a single query, and why the nesting exists.*

```
Index 0. The query returns a list of responses; since we only send one query at a time, it is always just the first item on the list of responses.
```

---

### Relevance threshold

*Will you filter out results above a certain distance score, or return all `n_results` regardless of how relevant they are? What are the tradeoffs of each approach?*

```
My retrieve approach is to filter out results above a certain distance score threshold. 
Pros: Using a relevance threshold reduces irrelevant context, decreases hallucination, saves tokens, and improves precision.
Cons: Can return nothing for a valid query, difficult to choose threshold, differences in normalizing embeding model, and possibility of missing useful information.

Returning all n results
Pros: Always give LLM something to work with, simple, no threshold tuning, and better recall
Cons: Can return hallucinated or unrelated chunks, noise may confuse LLM, higher token costs, and lower precisions
```

---

### Edge cases

*How does your implementation behave when: (a) the collection is empty, (b) the query matches no chunks well, (c) the query matches chunks from multiple games?*

```
(a). Returns empty array
(b). Returns empty array
(c). Returns all chunks regardless of multiple games 
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 3.*

**Test query and top result returned:**

```
Query: "What happens when you roll a 7?"
Top result game: Catan
Distance score: 0.466
Does it make sense? Yes. The chunk included what happens when a 7 is rolled
```

**One thing about the query results that surprised you:**

```
I am surprised how high the distance score was for the top result that did contain the result and how close the distance score was to the top result even when it was the wrong game.
```
