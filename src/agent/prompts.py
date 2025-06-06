GRADE_PROMPT = (
    "You are a strict binary grader evaluating whether a retrieved document is relevant to a user's question.\n\n"
    "Retrieved Document:\n{context}\n\n"
    "User Question:\n{question}\n\n"
    "If the document contains any relevant keywords or has semantic overlap with the user's question, respond with 'yes'.\n"
    "Otherwise, respond with 'no'.\n\n"
    "Respond with only a single word: either 'yes' or 'no'. Do not provide any explanation or additional text."
)



REWRITE_PROMPT = (
    "Look at the input and try to reason about the underlying semantic intent / meaning.\n"
    "Here is the initial question:"
    "\n ------- \n"
    "{question}"
    "\n ------- \n"
    "Formulate an improved question:"
)

GENERATE_PROMPT = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer the question. "
    "If you don't know the answer, just say that you don't know. "
    "Use three sentences maximum and keep the answer concise.\n"
    "Question: {question} \n"
    "Context: {context}"
)