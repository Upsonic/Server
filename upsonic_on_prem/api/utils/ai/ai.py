

import os

os.environ["TRACELOOP_TRACE_CONTENT"] = "false"

from dotenv import load_dotenv
import requests

load_dotenv(dotenv_path=".env")


this_dir = os.path.dirname(os.path.abspath(__file__))

import hashlib

import ollama
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from langchain_community.embeddings import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from upsonic_on_prem.api.utils import storage
from upsonic_on_prem.api.utils.ai.ai_history import active_ai_history, save_ai_call
from upsonic_on_prem.api.tracer import tracer,  Status, StatusCode, provider

from upsonic_on_prem.api.utils import debug, info, warning, failed, successfully

import traceback
from openai import OpenAI

OpenAIInstrumentor().instrument(tracer_provider = provider)

from opentelemetry.instrumentation.chromadb import ChromaInstrumentor

ChromaInstrumentor().instrument(tracer_provider = provider)

bypass_ai = os.environ.get("bypass_ai", "false").lower() == "true"


class AI_:
    def __init__(self):
        pass

    @property
    def default_search_model(self):
        return os.environ.get("default_search_model", "nomic-embed-text-upsonic")
    

    def search_by_documentation(self, the_contents, question, min_score=0, how_many_result=10):
        with tracer.start_span("search") as span:
            info(f"Searching by documentation for {len(str(question))}")
            span.set_attribute("AI.default_search_model", AI.default_search_model)
            try:
                from langchain.docstore.document import Document

                texts = []
                ids = []
                for content in the_contents:
                    text = content["name"] + ":" + str(content["documentation"])
                    ids.append(content["name"])
                    texts.append(Document(page_content=text, metadata={"name": content["name"]}))

                text_salt = " ".join([text.page_content for text in texts])


                if not self.default_search_model.startswith("text-embedding"):

                    oembed = OllamaEmbeddings(base_url="http://localhost:11434", model=self.default_search_model)
                else:

                    oembed = OpenAIEmbeddings(model=self.default_search_model, openai_api_key=os.environ.get("openai_api_key"))

                sha256_of_model = hashlib.sha256(self.default_search_model.encode()).hexdigest()

                the_directory = "/db/embed_by_documents"+sha256_of_model
                the_salt_name = ":embed_by_documents_salt"+sha256_of_model


                if not os.path.exists(the_directory):
                    debug("Creating the_directory")
                    os.makedirs(the_directory)

                pass_generate = False

                if not os.path.exists(the_directory+"/chroma.sqlite3"):
                    debug("Generating new vectorstore")
                    vectorstore = Chroma.from_documents(documents=texts, ids=ids, embedding=oembed, persist_directory=the_directory, collection_metadata={"hnsw:space": "cosine"})
                    storage.set(the_salt_name, hashlib.sha256(text_salt.encode()).hexdigest())
                    pass_generate = True
                    debug("Generated new vectorstore")



                vectorstore = Chroma(persist_directory=the_directory, embedding_function=oembed, collection_metadata={"hnsw:space": "cosine"})

                if (len(texts) > 0 and vectorstore._collection.count() == 0) or hashlib.sha256(text_salt.encode()).hexdigest() != storage.get(the_salt_name) and not pass_generate:
                    debug("Regenerating vectorstore")
                    span.set_attribute("regenerated_vectorstore", True)
                    vectorstore = Chroma.from_documents(documents=texts, ids=ids, embedding=oembed, persist_directory=the_directory, collection_metadata={"hnsw:space": "cosine"})
                    storage.set(the_salt_name, hashlib.sha256(text_salt.encode()).hexdigest())
                    debug("Regenerated vectorstore")
                    
                currenly_get = vectorstore._collection.get()
        
                currently_docs = []
                for doc in currenly_get["documents"]:
                    index_number = currenly_get["documents"].index(doc)
                    data = {"page_content": doc, "metadata": currenly_get["metadatas"][index_number]}
                    currently_docs.append(Document(page_content=data["page_content"], metadata=data["metadata"]))
        
                for doc in currently_docs:
                        
                        if doc.metadata["name"] not in [text.metadata["name"] for text in texts]:
                            _name = doc.metadata["name"]
                            debug(f"Removing {_name}")
                            vectorstore._collection.delete([doc.metadata["name"]])
                        else:
                            new_doc = None
                            for text in texts:
                                if doc.metadata["name"] == text.metadata["name"]:
                                    new_doc = text

                            if new_doc != None:
                                if doc.page_content != new_doc.page_content:
                                    _name = doc.metadata["name"]
                                    debug(f"Updating {_name}")
                                    vectorstore.update_document(new_doc.metadata["name"], new_doc)

                


                docs = vectorstore.similarity_search_with_relevance_scores(question, k=how_many_result)
                debug(f"Found {len(docs)} results")
                span.set_attribute("found_results", len(docs))

                results = []

                for doc in docs:
                    if doc[1] >= min_score:
                        doc = [doc[0].metadata["name"], doc[0].page_content.replace(doc[0].metadata["name"]+":", ""), doc[1]]
                        results.append(doc)

                results = [list(t) for t in set(tuple(element) for element in results)]

                info(f"Returning {len(results)} results")
                results = sorted(results, key=lambda x: x[2], reverse=True)
                span.set_status(Status(StatusCode.OK))
            except Exception as ex:
                traceback.print_exc()
                failed("Failed to search by documentation")
                results = []
                span.set_status(Status(StatusCode.ERROR))
                span.record_exception(ex)
            return results


    def completion(self, input_text, model):
        if bypass_ai:
            return "BYPASSED"
        result = None

        if model == "upsonic_local_model":
            result = self.gemmma(input_text)
        elif model == "gpt-3.5-turbo":
            result = self.gpt(input_text, model=model)
        elif model == "gpt-4":
            result = self.gpt(input_text, model=model)
        elif model == "gpt-4o":
            result = self.gpt(input_text, model=model)              


        if active_ai_history:
            save_ai_call(input_text, result, model)
         
        return result


    def default_completion(self, input_text):
        return self.completion(input_text, self.default_model)

    @property
    def default_model(self):
        return os.environ.get("default_model", "upsonic_local_model")



    def gpt(self, input_text, model):
        client = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get("openai_api_key"),
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": input_text,
                }
            ],
            model=model,
        )

        return chat_completion.choices[0].message.content


    def gemmma(self, input_text):

        response = ollama.generate(model='upsonic_local_model', prompt=input_text)
        result = response['response']


        return result


    def code_to_time_complexity(self, code):
        input_text = f"""
In this task, your goal is to generate the time complexity of a given piece of Python code. The complexity should be expressed in Big-O notation which describes the worst-case scenario in terms of time complexity. The time complexity would describe how the runtime of the code scales with the size of its input. Here's an example:

**Input:**
```python
def add_numbers(a, b):
    return a + b
```

**Output:** 
O(1) - The time complexity is constant because the code does not contain any loops or recursive calls, thus the runtime does not change with the size of the input.

Now, please generate the time complexity of the following code:

```python
{code}

```

Consider loops, recursive calls, and other structures that might affect the scalability of the code when determining the time complexity.
"""


        result = self.default_completion(input_text)
        return result

    def code_to_documentation(self, code, return_prompt=False):
        input_text = f"""
The task is to generate a summary of a given piece of Python code. The summary should explain the purpose of the code, the input variables and the operation it performs. High level understanding of the logic behind the code should also be provided. The code for analysis will be provided as input in string format. Here's an example:

Input: 
```python
def add_numbers(a, b):
  return a + b
```

Output: 
This code defines a function named 'add_numbers' that takes two arguments, a and b. It returns the sum of these two numbers. The logic behind this code is to utilize the built-in '+' operator to add the values of a and b together.

Try to make your explanations as clear, concise, and accessible as possible to a wide range of users.

And now make a summary for this code:

```python
{code}
    
```

"""

        if return_prompt:
            return input_text

        result = self.default_completion(input_text)
        return result


    def code_to_mistakes(self, code):

        input_text = f"""
In this task, your goal is to identify and describe potential mistakes, including syntax errors and logical errors, in a given Python code. You should provide suggestions on how to fix these errors when possible. Here's an example:

**Input:**
```python
deff add_numbers(a, b)
    return a ++ b
```

**Output:** 
Two mistakes are identified in this code. First, the function definition uses 'deff', which is not a valid keyword in Python. This should be corrected to 'def'. Second, the operation '++' is not valid in Python. To add two numbers in Python, the '+' operator is used.

Now, please identify potential mistakes in the following code:


```python
{code}
```

Note: Please identify and describe the errors in a clear and informative manner. Libraries already imported. There is no `Missing Imports`

"""


        result = self.default_completion(input_text)
        return result



    def code_to_security_analysis(self, code):

        input_text = f"""
In this task, you're required to conduct a security analysis of the provided Python code snippet. It requires you to find potential security risks, pitfalls or weak practices from a security perspective and propose enhancements to address them.

For instance:
**Input:**
```python
password = "123456"
```
**Output:**
This code displays a plain text password which is a significant security vulnerability. Passwords stored in plain text can be easily identified and exploited if the code is exposed or attacked. Passwords such as these that consist of consecutive numbers do not offer substantial security, as they can be easily guessed. A more secure approach would be storing passwords in an encrypted format in a secure environment or using OS environment variables for sensitive pieces of data.

Now, considering a fresh scenario, please perform a security audit of the following Python code:

```python
{code}
```

In your response, give a clear outline of potential securityissues present and elaborate on how one might strengthen the overall security. Libraries already imported. The focus is on text-based analysis, so no need to provide an actual piece of code in your response.
"""


        result = self.default_completion(input_text)
        return result


    def code_to_required_test_types(self, code):
        input_text = f"""
In this task, you're asked to critically evaluate the Python code provided below from a testing perspective. You're expected to identify the critical sections which would require testing, recommend types of tests (unit tests, functional tests, integration tests, etc.) that would be appropriate, and highlight any potential edge cases that need to be addressed.

Additionally, please comment on the overall testability of the code: is it structured in a way that's conducive to testing? Where relevant, suggest any alterations that could be made to enhance test coverage and ease testing efforts.

Let's illustrate with an example:

**Input:**
```python
def add(a, b):
    return a + b
```

**Output:**
This is a simple function, add, which returns the sum of two inputs. In terms of testing, different types of tests could be used:
  - **Unit tests** to confirm that the function correctly adds numbers together.
  - **Edge case testing** to verify its behavior with edge inputs like very large numbers, zero, or negative numbers.
Furthermore, attention should be given to test whether the function handles non-numeric input gracefully, potentially raising an appropriate error.

Now, please perform a test analysis on the following piece of Python code:

```python
{code}
```

Note down list the types of tests you would run to ensure the function behaves as expected. And just give text not code.
"""


        result = self.default_completion(input_text)
        return result        





    def code_to_tags(self, code):
        input_text = f"""
Your objective is to develop an automated system that can extract and generate informative tags based on the functionality and characteristics of the provided Python code snippets. The generated tags should succinctly summarize the key aspects and features of each code segment.

Your system needs to analyze the code snippets and produce descriptive tags that capture the essence of the code's purpose and functionality. Consider elements like variable names, function calls, control flow structures, and any unique patterns present in the code to generate meaningful tags.

**Example:**

**Input:**
```python
def check_prime(number):
    if number <= 1:
        return False
    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            return False
    return True
```

**Output:**
Tags: 'prime numbers', 'number validation', 'loop iteration', 'mathematics'

For this example, the generated tags highlight key concepts related to prime number checks, number validation, loop iteration, and mathematical operations within the code.

Now, analyze the Python code snippet provided below and generate descriptive tags that encapsulate the primary functionalities and characteristics of the code:

```python
{code}
```

Produce meaningful tags that succinctly summarize the significant components and operations illustrated in the provided code snippet. Focus on extracting essential details from the code content to generate informative tags without diving into actual code generation.
"""


        result = self.default_completion(input_text)

        return result        





    def generate_readme(self, top_library, summary_list):
        result = None
        with tracer.start_span("readme-generate") as span:
            try:
                span.set_attribute("AI.default_model", AI.default_model)
                span.set_attribute("summary_list_len", len(str(summary_list)))
                prompt = f"""
Hi there is an list of elements and summaries:

{summary_list}


Explain the purpose of this '{top_library}' library and its elements in a few sentences.
"""



                summary = self.default_completion(prompt)

                # Also generate the usage aim
                prompt = f"""
Hi there is an list of elements and summaries:

{summary_list}


Explain the usage aim of this '{top_library}' library and its elements in a few sentences.
"""
                

                            
                usage_aim = self.default_completion(prompt)

                result = '<b class="custom_code_highlight_green">Explanation:</b><br>' + summary + '\n\n<b class="custom_code_highlight_green">Use Case:</b><br>' + usage_aim
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR))
                span.record_exception(e)


        return result




    def difference_to_commit_message(self, code_old, code_new):
        input_text = f"""
In this task, your goal is to generate a commit message for the differences.


```python old version
{code_old}
```

```python new version
{code_new}
```

Generate a smalll commit message. Maybe 1 or 2 sentence.

```
Example commit messages:
Add feature for a user to like a post

Drop feature for a user to like a post

Fix association between a user and a post

Bump dependency library to current version

Make build process use caches for speed

Start feature flag for a user to like a post

Stop feature flag for a user to like a post

Optimize search speed for a user to see posts

Document community guidelines for post content

Refactor user model to new language syntax

Reformat home page text to use more whitespace

Rearrange buttons so OK is on the lower right

Redraw diagram of how our web app works

Reword home page text to be more welcoming
  
Revise link to update it to the new URL
```


Answer only with your commit message suggestion:
"""



        result = self.default_completion(input_text)


        return result


    def commits_to_release_note(self, code):
        input_text = f"""
In this task, your goal is to generate a releate note by the commits.


```commit messages
{code}
```

Generate a small release note. Maybe 1 or 2 pharagraph and a list.


"""




        result = self.default_completion(input_text)

        return result


    def generate_releate_note(self, top_library, small_parts, version):
        input_text = f"""
In this task, your goal is to generating a library release note by the smaller parts release notes.

Library name: {top_library}
Release version: {version}

```smaller parts
{small_parts}
```

Generate a small release note. Maybe 1 or 2 pharagraph and a list.
"""




        result = self.default_completion(input_text)


        return result




AI = AI_()
