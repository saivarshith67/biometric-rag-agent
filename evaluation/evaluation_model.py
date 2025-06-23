
from deepeval.models.base_model import DeepEvalBaseLLM # Ensure this 
import json
import re
from langchain_openai import ChatOpenAI


class EvaluationModel(DeepEvalBaseLLM):
    def __init__(self, model):
        self.model = model

    def load_model(self):
        return self.model

    def _clean_json_response(self, response: str) -> str:
        """Clean and extract JSON from response"""
        # Remove any markdown formatting
        response = re.sub(r'```json\n?', '', response)
        response = re.sub(r'```\n?', '', response)

        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                # Validate JSON
                json.loads(json_str)
                return json_str
            except json.JSONDecodeError:
                pass

        # If no valid JSON found, return the original response
        return response.strip()

    def generate(self, prompt: str) -> str:
        enhanced_prompt = f"""
        {prompt}

        IMPORTANT: Your response must be valid JSON only. Do not include any explanations, markdown formatting, or additional text outside the JSON structure.
        """
        chat_model = self.load_model()
        response = chat_model.invoke(enhanced_prompt).content
        return self._clean_json_response(response)

    async def a_generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        res = await chat_model.ainvoke(prompt)
        return self._clean_json_response(res.content)

    def get_model_name(self):
        return "llama3-8b-8192"


# model = model = ChatOpenAI(
#     model="llama3-8b-8192",
#     temperature=0,
#     base_url="https://api.groq.com/openai/v1",  # ✅ Corrected URL
#     api_key="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",
# )



if __name__ == "__main__":

    model = ChatOpenAI(
        model="meta-llama/llama-3.3-8b-instruct:free",
        temperature=0,
        base_url="https://openrouter.ai/api/v1",  # ✅ Corrected URL
        api_key="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",
    )
    evaluation_model = EvaluationModel(model=model)
    print(evaluation_model.generate("""Write me a joke in JSON format like IMPORTANT: Your response must ONLY contain valid JSON. DO NOT include ANY text, explanations, or markdown. Respond ONLY with raw JSON like: {"joke": "..."}"""))