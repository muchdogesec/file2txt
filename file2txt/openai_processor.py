

class BaseCleaner:
    def do_cleanup(self, text: str):
        raise NotImplementedError("this cleaner is not implemented")
    
class OpenAIMDCleaner(BaseCleaner):
    instruction = """
    You are a markdown file cleaner, you are to clean up this text input and convert into markdown, do not format your response
     
    Process:
    - recognized tables should be morphed into a markdown table
    - add bullets and numbering where appropriate
    - only add code blocks when applicable and language is identified
    - escape html tags when needed
    - other markdown features

    do not add extra text. do not add extra headers.
    """
    def do_cleanup(self, text):
        from llama_index.llms.openai import OpenAI
        from llama_index.core.chat_engine import SimpleChatEngine
        from llama_index.core.base.llms.types import ChatMessage, MessageRole

        chat_history = [
            ChatMessage(
                role=MessageRole.SYSTEM,
                content=self.instruction
            ),

        ]
        llm = OpenAI(model="gpt-4o", timeout=120)
        engine = SimpleChatEngine.from_defaults(chat_history=chat_history, llm=llm)
        response = engine.chat(f"clean up this file\n\n{text}")
        return response.response
