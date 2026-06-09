# Spec: `generate_response()`

**File:** `generator.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Given a user query and a list of retrieved rule chunks, generate a response that directly answers the question using only the retrieved text as context. The response must be grounded — it should not draw on the model's general knowledge of board games, only on what was retrieved.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The user's original question |
| `retrieved_chunks` | `list[dict]` | Ranked list of chunks from `retrieve()`, each with `"text"`, `"game"`, and `"distance"` |

**Output:** `str`

A plain string containing the response to show the user. The response should:
- Answer the question using only the retrieved rule text
- Identify which game the answer comes from
- Acknowledge clearly when the answer is not found in the loaded rules

Returns a fallback string (not an error) when `retrieved_chunks` is empty.

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Context formatting

*How will you format the retrieved chunks before passing them to the LLM? Describe the structure — not the code. Consider: will you label chunks by game? Include distance scores? Separate chunks with delimiters?*

```
Structure example:
Game: Catan
[chunk text]

---
Game: Catan
[chunk text]


The game will be labeled, the distance scores will be removed, and chunks are separated by clear delimiters (blank lines or section headers)
```

---

### System prompt — grounding instruction

*Write the exact system prompt instruction you will use to prevent the model from answering beyond the retrieved text. This is the most important design decision in this function.*

```
You are a grounded board-game rules assistant. You must answer ONLY using the information provided in the retrieved context. 

Rules:
- If the answer is not explicitly contained in the retrieved context, say: "I do not have enough information in the rule books to answer." 
- Do not use outside knowledge, general knowledge, or assumptions. Treat the retrieved context as the only source of truth.
- Do not infer missing rules or fill gaps.
- If context is partially relevant, only use the relevant parts and explicitly state uncertainty.
- Every answer must be fully traceable to the context

```

---

### System prompt — citation instruction

*Write the exact instruction you will use to tell the model to identify which game its answer comes from.*

```
You must cite the source game for every rule or statement you use.
Format Requirements:
- Each claim must include the game name in brackets.
- If multiple games are used, separate them clearly by section.
- Do not mix rules across games without explicit labeling

Example format:
- [Catan] Players may trade resources on their turn.
- [Monopoly] Players collect rent when others land on owned properties. 
```

---

### Fallback behavior

*What should the response say when the answer isn't found in the loaded rule books? Write the exact fallback message.*

```
I couldn’t find this information in the provided rule books.
Try rephrasing your question or checking if the rule exists in another section.
```

---

### Handling low-relevance chunks

*`retrieved_chunks` may include chunks with high distance scores (weak relevance). Will you filter these out before building context, pass them all in, or handle them another way? What are the tradeoffs?*

```
I will use a two-stage relevance strategy:

1. Retrieve top K chunks from the vector database.
2. Filter chunks using a similarity threshold to remove weak matches.

Only chunks that are sufficiently relevant will be included in the context.

Tradeoffs:
- Higher threshold → better precision, lower recall (risk missing useful context)
- Lower threshold → better recall, more noise and hallucination risk

To balance this:
- Prefer top-K with moderate filtering
- If no chunks pass threshold, fall back to top 1–2 results instead of returning empty context
```

---

### Message structure

*Describe how you will structure the messages list for the API call — what goes in the system message vs. the user message?*

```
I will structure the API call as follows:

System message:
- Strict grounding rules (only use provided context)
- Citation rules (must attribute every claim to a game)
- Fallback instruction (what to say if context is insufficient)
- No external knowledge allowed under any condition

User message:
- The user’s question
- A clearly delimited context block containing retrieved chunks

Context format:
Each chunk will be formatted as:

[Game: <game name>]
<chunk text>
---
```

---

## Implementation Notes

*Fill this in after implementing and testing.*

**Test query and response:**

```
Query: How do you get out of Jail in Monopoly?
Response: [Monopoly] To get out of Jail, players can pay a $50 fine before rolling on any of their next three turns, use a Get Out of Jail Free card, or roll doubles on any of their three turns in Jail.
Correctly grounded? Yes
Cited the right game? Yes
```

**One thing you changed from your original spec after seeing the actual output:**

```
n/a
```
