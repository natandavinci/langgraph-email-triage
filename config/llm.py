from config.settings import gemini_client, MODEL_NAME

def call_llm(prompt: str) -> str:
    """
    Função centralizada para chamadas ao modelo de linguagem (LLM).
    Centraliza a versão do modelo, parâmetros de geração e tratamento de erros.
    """

    try:
        response = gemini_client.models.generate_content(
            model = MODEL_NAME,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"❌ [ERRO LLM]: Falha ao comunicar com o Gemini: {e}")
        raise e