from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = (
    "You are a grounded board-game rules assistant. You must answer ONLY using the information provided in the retrieved context. \n"
    "Rules: \n"
    "- If the answer is not explicitly contained in the retrieved context, say: 'I do not have enough information in the rule books to answer.' \n"
    "- Do not use outside knowledge, general knowledge, or assumptions. Treat the retrieved context as the only source of truth. \n"
    "- Do not infer missing rules or fill gaps. \n"
    "- If context is partially relevant, only use the relevant parts and explicitly state uncertainty. \n"
    "- Every answer must be fully traceable to the context \n\n"
    "You must cite the source game for every rule or statement you use.\n"
    "Format Requirements:\n"
    "- Each claim must include the game name in brackets.\n"
    "- If multiple games are used, separate them clearly by section.\n"
    "- Do not mix rules across games without explicit labeling\n"
    "Example format:\n"
    "- [Catan] Players may trade resources on their turn.\n"
    "- [Monopoly] Players collect rent when others land on owned properties. \n"
)

def generate_response(query, retrieved_chunks):
    """
    Generate a grounded answer from retrieved rule chunks.

    Milestone 3:

    `retrieved_chunks` is the list returned by retrieve(). Each item is a dict:
      - "text"     : the chunk text
      - "game"     : the game name
      - "distance" : similarity score (you can use this to filter weak matches)

    Before writing code, talk through these with your group:
      - How will you format the chunks into a context block for the prompt?
      - What instructions will stop the model from answering beyond what the
        rules say? (Grounding is the whole point — a confident wrong answer
        is worse than an honest "I don't know.")
      - How will you surface which game each answer comes from?

    Your response should:
      1. Answer using only the retrieved context — not the model's general knowledge
      2. Make clear which game the answer comes from
      3. Say so clearly when the answer isn't in the loaded rules

    Return the response as a plain string.
    """
    if not retrieved_chunks:
        return (
            "I couldn't find anything relevant in the loaded rule books. "
            "Try rephrasing your question — or check that your ingestion pipeline is working."
        )

    # build context block.
    # format:
    #   Game: <game> \n <chunk_text>
    context_block = "\n\n".join(
        f"Game: {chunk['game']}\n{chunk['text']}" for chunk in retrieved_chunks
    )

    user_prompt = (
        f"Context:\n{context_block}\n\n"
        f"Question: {query}\n\n"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
    )

    return response.choices[0].message.content.strip()
