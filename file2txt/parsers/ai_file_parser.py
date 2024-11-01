import logging
from typing import Dict, List
from .core import BaseParser
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import IndexNode, TextNode
from openai import OpenAI
from openai.types.beta import Assistant

class AIParser(BaseParser):
    ai_processor = None
    instruction = ""
    client: OpenAI = None
    assistant: Assistant = None
    # def load_file(self):
    #     if not self.instruction:
    #         raise AIParserError("unable to continue, instruction must be set")
    #     self.ai_processor = OpenAIAssistantAgent.from_new(
    #         name="File Conversion",
    #         files=[self.file_path],
    #         instructions="You are a document converter",
    #         verbose=True,
    #         model="gpt-4-turbo",
    #         openai_tools=[{"type": "code_interpreter"}],
    #     )
        
    #     # print(self.ai_processor.chat("start"))
    #     self.ai_processor.add_message(self.instruction, list(self.ai_processor.file_dict))
    #     print(self.ai_processor.run_assistant())

    def __init__(self, *args, **kwargs):
        self.client = OpenAI()
        self.assistant = self.client.beta.assistants.create(
            name="Document Converter",
            instructions="You are a document converter. You do not reply with anything other than the converted MD document. You are just a converter, you are not to summarize, you are to reply with the document as exact as possible.",
            tools=[{"type": "file_search"}],
            model="gpt-4o",
        )
        # self.thread = self.client.beta.threads.create()
        
        
    def add_files(self, paths: List[str]) -> Dict[str, str]:
        files = []
        for file in paths:
            file_obj = self.client.files.create(file=open(file, "rb"), purpose="assistants")
            files.append(dict(file_id=file_obj.id, tools=[{"type": "file_search"}]))
            # files.append(dict())

        message = dict(
            # thread_id=self.thread.id,
            role="user",
            content=self.instruction,
            attachments=files,
        )
        logging.debug("all files %s", files)
        self.thread = self.client.beta.threads.create(messages=[message])
        logging.debug("Thread url: %s", self.thread_url)
    
    def get_output(self):
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            # instructions="Please address the user as Jane Doe. The user has a premium account."
            additional_instructions="do not include anything other than the markdown in your reply"
        )

        if run.status == 'completed': 
            messages = self.client.beta.threads.messages.list(
                thread_id=self.thread.id,
                run_id=run.id
            )
            print( messages)
        else:
            print(run.status)

    @property
    def thread_url(self):
        return f"https://platform.openai.com/playground/assistants?assistant={self.assistant.id}&thread={self.thread.id}"
        
    
class AIParserError(BaseException):
    pass