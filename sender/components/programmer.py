# The programmer creates implementations depending on a protocol specification

import json
import os

from toolformers.base import Toolformer
from utils import extract_substring

TASK_PROGRAMMER_PROMPT = '''
You are ProtocolProgrammerGPT. You will act as an intermediate between a machine (that has a certain input and output schema in JSON) \
and a remote server that can perform a task following a certain protocol. Your task is to write a routine that takes some task data \
(which follows the input schema), sends query in a format defined by the protocol, parses it and returns the output according to the output schema so that \
the machine can use it.
The routine is a Python file that contains a function "send_query". send_query takes a single argument, "task_data", which is a dictionary, and must return \
a dictionary, which is the response to the query formatted according to the output schema.
In order to communicate with the remote server, you can use the function "send_to_server" that is already available in the environment.
send_to_server takes a single argument, "query" (which is a string formatted according to the protocol), and returns a string (again formatted according \
to the protocol). Do not worry about managing communication, everything is already set up for you. Just focus on preparing the right query.

Rules:
- The implementation must be written in Python.
- You can define any number of helper functions and import any libraries that are part of the Python standard library.
- Do not import libraries that are not part of the Python standard library.
- send_to_server will be already available in the environment. There is no need to import it.
- Your task is to prepare the query, send it and parse the response.
- Remember to import standard libraries if you need them.
- If there is an unexpected error that is not covered by the protocol, throw an exception.\
 If instead the protocol specifies how to handle the error, return the response according to the protocol's specification.
- Do not execute anything (aside from library imports) when the file itself is loaded. I will personally import the file and call the send_query function with the task data.
Begin by thinking about the implementation and how you would structure the code. \
Then, write your implementation by writing a code block that contains the tags <IMPLEMENTATION> and </IMPLEMENTATION>. For example:
```python
<IMPLEMENTATION>

def send_query(task_data):
  ...

</IMPLEMENTATION>
'''

# TODO: Prompts should be key-valued and overridable
class SenderProgrammer:
    def __init__(self, toolformer : Toolformer, num_attempts : int = 5):
        self.toolformer = toolformer
        self.num_attempts = num_attempts

    def __call__(self, task_schema, protocol_document : str):
        conversation = self.toolformer.new_conversation(TASK_PROGRAMMER_PROMPT, [], category='programming')
        message = 'JSON schema:\n\n' + json.dumps(task_schema) + '\n\n' + 'Protocol document:\n\n' + protocol_document

        for _ in range(self.num_attempts):
            reply = conversation.chat(message, print_output=True)

            implementation = extract_substring(reply, '<IMPLEMENTATION>', '</IMPLEMENTATION>')

            if implementation is not None:
                break

            message = 'You have not provided an implementation yet. Please provide one by surrounding it in the tags <IMPLEMENTATION> and </IMPLEMENTATION>.'

        implementation = implementation.strip()

        # Sometimes the LLM leaves the Markdown formatting in the implementation
        implementation = implementation.replace('```python', '').replace('```', '').strip()

        implementation = implementation.replace('def send_query(', 'def run(')

        return implementation
