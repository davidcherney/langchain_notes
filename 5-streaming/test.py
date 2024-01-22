from langchain.chat_models import ChatOpenAI 
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

from langchain.chains import LLMChain

from langchain.callbacks.base import BaseCallbackHandler

#queue 
from queue import Queue

from threading import Thread

load_dotenv()

# queue = Queue()

class StreamingHandler(BaseCallbackHandler):
    """
    There are some special method names we can access
    that reference background processes that are watching for events
    or maybe for observing events somehow broadcast by a chain
    that is using this callback.
    1. when the LLM generates a new token, add it to a queue
    2. When the LLM is done generating tokens, add None to the queue. 
    3. When the LLM throws an error, add None to the queue.
    """

    # We initialize with a Queue object. 
    def __init__(self,queue):
        self.queue = queue 

    def on_llm_new_token(self,
                         token, # required for this special method.
                         **kwargs # required for this special method.
                         ):
        # queue.put(token) # upgrade to an attribute so instances have their own
        self.queue.put(token)
                         

    def on_llm_end(self, 
                   response,  # required for this special method.
                   **kwargs # required for this special method.
                   ):
        self.queue.put(None)

    def on_llm_error(self, 
                   error,  # required for this special method.
                   **kwargs # required for this special method.
                   ):
        self.queue.put(None)


# Instantiate a chat object.
chat = ChatOpenAI(
    # Force OpenAI to stream to LangChain.
    streaming=True, # Controls how OpenAI responds to LangChain.
    # callbacks=[StreamingHandler()] gives all instances the same callbacks.
    # so this is moved to StreamingChain.stream.task.self(here)
    )

prompt = ChatPromptTemplate.from_messages(
    [
        ("human","{content}")
    ]
)

# chain = LLMChain(llm=chat,prompt=prompt)

# for output in chain.stream(input={"content":"tell me a joke" }):
#     print(output)

# messages = prompt.format_messages(
#     content="tell me a joke"
# )

# print(messages)

# Call the chat object.
# This controls 
# 1. how OpenAI responds to LangChain
# 2. how LangChain responds to us.
# output = chat(messages)
# output = chat.__call__(messages) #Exactly the same.
# output = chat.invoke(messages) # Slightly different.
# output = chat.stream(messages) # gave a generator object BaseChatModel.stream.

# print(output) # Not appropriate for streams
# i=0
# for message in chat.stream(messages):
#     # print(message) gives content, additoinal_kwargs, and example as boolean. 
#     print(i,message.content)
#     i+=1

class StreamingChain(LLMChain):
    # chain.stream(<any string>) will be our generator object
    # from which to print new tokens arriving from the LLM.  
    def stream(self,input):
        # Each streamingChain should have its own queue and handler
        # to keep the chats separate. 
        queue = Queue()
        handler =StreamingHandler(queue)

        def task():
            self( # Without threading this blocks our while loop.
                input, 
                callbacks=[handler] # Here instead of chat=OpenAI.
                ) 
        
        Thread(target=task).start()

        # The python `yield` appends to a generator object. 
        while True:
            # if there is something in the queue, then yield it. 
            # That means add it to the generator
            token = queue.get()
            # If the token is None (because LLM is done or because LLM error)
            # Then we are done. 
            if token is None:
                break
            yield token

chain = StreamingChain(llm=chat,prompt=prompt)

# A for loop that prints elements of a generator object.
# Elements get added when an item is added to the queue.
# It must be that 
# this loop does not end when the last element in the generator is reached. 
for output in chain.stream(input={"content": "tell me a joke"}):
    print(output,end="")

