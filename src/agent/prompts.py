GRADE_PROMPT = (
    "You are an AI grader. Decide whether the retrieved document is directly relevant to the user's question.\n\n"
    "Only respond 'yes' or 'no'.\n\n"
    "Consider the document relevant if it contains factual information or context that helps answer the user's question.\n"
    "Do NOT try to answer the question. Only judge the relevance.\n\n"
    "User Question:\n{question}\n\n"
    "Retrieved Document:\n{context}\n\n"
    "Respond with only one word: yes or no."
)


REWRITE_PROMPT = (
    "You are a helpful assistant improving questions to make them more specific and aligned with the BioStar 2 system.\n"
    "BioStar 2 is a security and biometric access control platform. When rewriting the question:\n"
    "- Remove vague or general phrases.\n"
    "- Avoid placeholders like [Operating System] or [Platform].\n"
    "- Include keywords specific to BioStar 2 if applicable (e.g., 'register user', 'admin credential', 'face authentication').\n"
    "- Make the question clearer and more relevant for document retrieval.\n\n"
    "Original Question:\n"
    "{question}\n\n"
    "Rewritten Question:"
)



GENERATE_PROMPT = (
    "You are a helpful assistant. Answer the question using the information provided in the context below.\n"
    "You may use reasoning or inference, but do not use any external knowledge beyond the context.\n\n"
    "Context:\n{context}\n\n"
    "Question:\n{question}\n\n"
    "If the answer cannot be confidently inferred from the context, respond with:\n"
    "'I don't know based on the provided context.'\n\n"
    "Otherwise, provide a short, accurate, and direct answer."
)
