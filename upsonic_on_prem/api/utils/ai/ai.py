import os
import json
import re
os.environ["TRACELOOP_TRACE_CONTENT"] = "false"

from dotenv import load_dotenv

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
from upsonic_on_prem.api.tracer import tracer, provider
from opentelemetry.trace import Status, StatusCode

from upsonic_on_prem.api.utils import debug, info, failed

from upsonic_on_prem.api.utils.kot_db import kot_db

import traceback
from openai import OpenAI, AzureOpenAI

OpenAIInstrumentor().instrument(tracer_provider=provider)

from opentelemetry.instrumentation.chromadb import ChromaInstrumentor

ChromaInstrumentor().instrument(tracer_provider=provider)

bypass_ai = os.environ.get("bypass_ai", "false").lower() == "true"





class AI_:
    def __init__(self):
        pass

    @property
    def default_search_model(self):
        return kot_db.get("default_search_model")
    

    def search_by_documentation(
        self, the_contents, question, min_score=0, how_many_result=10
    ):
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
                    texts.append(
                        Document(page_content=text, metadata={"name": content["name"]})
                    )

                text_salt = " ".join([text.page_content for text in texts])

                if not self.default_search_model.startswith("text-embedding"):
                    oembed = OllamaEmbeddings(
                        base_url="http://localhost:11434",
                        model=self.default_search_model,
                    )
                else:
                    oembed = OpenAIEmbeddings(
                        model=self.default_search_model,
                        openai_api_key=kot_db.get("openai_apikey"),
                    )

                sha256_of_model = hashlib.sha256(
                    self.default_search_model.encode()
                ).hexdigest()

                the_directory = "/db/embed_by_documents" + sha256_of_model
                the_salt_name = ":embed_by_documents_salt" + sha256_of_model

                if not os.path.exists(the_directory):
                    debug("Creating the_directory")
                    os.makedirs(the_directory)

                pass_generate = False

                if not os.path.exists(the_directory + "/chroma.sqlite3"):
                    debug("Generating new vectorstore")
                    vectorstore = Chroma.from_documents(
                        documents=texts,
                        ids=ids,
                        embedding=oembed,
                        persist_directory=the_directory,
                        collection_metadata={"hnsw:space": "cosine"},
                    )
                    storage.set(
                        the_salt_name, hashlib.sha256(text_salt.encode()).hexdigest()
                    )
                    pass_generate = True
                    debug("Generated new vectorstore")

                vectorstore = Chroma(
                    persist_directory=the_directory,
                    embedding_function=oembed,
                    collection_metadata={"hnsw:space": "cosine"},
                )

                if (
                    (len(texts) > 0 and vectorstore._collection.count() == 0)
                    or hashlib.sha256(text_salt.encode()).hexdigest()
                    != storage.get(the_salt_name)
                    and not pass_generate
                ):
                    debug("Regenerating vectorstore")
                    span.set_attribute("regenerated_vectorstore", True)
                    vectorstore = Chroma.from_documents(
                        documents=texts,
                        ids=ids,
                        embedding=oembed,
                        persist_directory=the_directory,
                        collection_metadata={"hnsw:space": "cosine"},
                    )
                    storage.set(
                        the_salt_name, hashlib.sha256(text_salt.encode()).hexdigest()
                    )
                    debug("Regenerated vectorstore")

                currenly_get = vectorstore._collection.get()

                currently_docs = []
                for doc in currenly_get["documents"]:
                    index_number = currenly_get["documents"].index(doc)
                    data = {
                        "page_content": doc,
                        "metadata": currenly_get["metadatas"][index_number],
                    }
                    currently_docs.append(
                        Document(
                            page_content=data["page_content"], metadata=data["metadata"]
                        )
                    )

                for doc in currently_docs:
                    if doc.metadata["name"] not in [
                        text.metadata["name"] for text in texts
                    ]:
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
                                vectorstore.update_document(
                                    new_doc.metadata["name"], new_doc
                                )

                docs = vectorstore.similarity_search_with_relevance_scores(
                    question, k=how_many_result
                )
                debug(f"Found {len(docs)} results")
                span.set_attribute("found_results", len(docs))

                results = []

                for doc in docs:
                    if doc[1] >= min_score:
                        doc = [
                            doc[0].metadata["name"],
                            doc[0].page_content.replace(
                                doc[0].metadata["name"] + ":", ""
                            ),
                            doc[1],
                        ]
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
        return kot_db.get("default_model")

    def gpt(self, input_text, model):
        if kot_db.get("openai") == True:
            client = OpenAI(
                # This is the default and can be omitted
                api_key=kot_db.get("openai_apikey"),
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
    
        if kot_db.get("azureopenai") == True:
            client = AzureOpenAI(
                azure_endpoint=kot_db.get("azureopenai_baseurl"),
                api_version=kot_db.get("azureopenai_version"),
                api_key=kot_db.get("azureopenai_key")
            )

            completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": input_text,
                    }
                ],
                model=model,
            )

            return completion.choices[0].message.content

    def gemmma(self, input_text):
        response = ollama.generate(model="upsonic_local_model", prompt=input_text)
        result = response["response"]

        return result

    def code_to_time_complexity(self, code, return_prompt=False):
        input_text = f"""
Hi, in this task you will find the time complexity of python code. In start please read the knowledge between <knowledge> </knowledge>

<knowledge>
To write a time complexity analysis of a Python function, you need to follow these steps:

1. **Identify the input size**: Determine the variable that represents the size of the input. This is usually `n`.

2. **Analyze the function**: Break down the function into its individual operations and understand how these operations relate to the input size. Focus on loops, recursive calls, and non-constant time operations.

3. **Determine the time complexity for each part**: Evaluate the time complexity of each part of the function separately.

4. **Combine the complexities**: Combine the time complexities of all parts of the function to get an overall time complexity.

5. **Express the result**: Use Big-O notation to express the time complexity in the simplest form.

Here's a step-by-step example:

### Example Function

```python
def example_function(arr):
    total = 0
    for i in range(len(arr)):
        for j in range(i, len(arr)):
            total += arr[j]
    return total
```

### Steps for Analyzing Time Complexity

1. **Identify the input size**:
   - The input is `arr` and its size is `n` (i.e., `len(arr) = n`).

2. **Analyze the function**:
   ```python
   total = 0  # O(1) time
   for i in range(len(arr)):  # Outer loop runs n times
       for j in range(i, len(arr)):  # Inner loop runs (n - i) times
           total += arr[j]  # O(1) time for each operation
   return total  # O(1) time
   ```

3. **Determine the time complexity for each part**:
   - Initialization (`total = 0`): O(1)
   - Outer loop (`for i in range(len(arr))`): Runs `n` times.
   - Inner loop (`for j in range(i, len(arr))`): Runs `(n - i)` times for each `i`.
     - When `i = 0`: Inner loop runs `n` times.
     - When `i = 1`: Inner loop runs `n - 1` times.
     - Continue until `i = n-1`: Inner loop runs 1 time.

4. **Combine the complexities**:
   - Summing up all iterations of the inner loop:
     \[
     \sum_"""+"""{i=0}^{n-1} (n - i) = n + (n - 1) + (n - 2) + ... + 1
     \]
     This is an arithmetic series that sums up to:
     \[
     \frac{n(n + 1)}{2}"""+f"""
     \]
     The dominant term is `n^2`, so the complexity is O(n²).

5. **Express the result**:
   - The overall time complexity of the `example_function` is **O(n²)**.


<knowledge>



Okey now track the <task_steps> </task_steps>

<task_steps>

- Analyze the given python function that in <python> </python>
- Decide to time complexity with time time complexity knowledge steps

- Return ONLY time complexity no any other text.


</task_steps>


<python>
{code}
</python>


Return only the time complexity
"""
        





        if return_prompt:
            return input_text

        result = self.default_completion(input_text)


        explaination = f"""
Hi, in this task you should explain given time complexity in just two sentences.

Time Complexity: {result}

Return the meaning of this time complexity in just two sentences. Don’t write any other text. Just return meaning.
"""

        return result + " - " + self.default_completion(explaination).replace(result, "this")

    def code_to_documentation(self, code, return_prompt=False):

        tldr = f"""
Generate a tldr message of python code. The output should be max four sentence. There is an information about writing tldr.

How can I write Tl;DR
Writing a TL;DR (too long; didn't read) summary involves condensing the content down to its most essential points. Here's how you can write an effective TL;DR:

1. **Read and Understand the Content**: Fully comprehend the material you'll be summarizing.
2. **Identify Key Points**: Focus on the main ideas, themes, and conclusions.
3. **Be Concise**: Use clear and direct language. Avoid unnecessary details.




Steps to do this task:
1) Read and understand How can I write Tl;DR

2) Analyze the python code its in <user_input> and </user_input>

3) Read And Understand the Content

4) Identify Key Points

4) Return the tldr message and be concise



Trick for return type, you return should be an message only. You should think before of the result.
You should not responsible to explain your return. Only return message answer



<user_input>
```python
{code}    
```
</user_input>



HEY, Don't forget the before prompt of <user_input>. Return only the message. 

HEY Just return message don't write any other message just like explain return content. Dont say TL;DR. The message should only 2 sentence maximum.



"""
        
        




        input_text = f"""
Generate a code Summary of python code. The output should be max eight sentence. There is an information about code summaries. 

Code Summaries
To write a summary of a Python function (other than the docstring, inputs, and outputs), you can focus on its purpose, logic, and any important algorithms or decisions it makes. Here’s a general approach you can follow:

1. **Function Purpose:** Briefly describe what the function is intended to do.
2. **Core Logic:** Summarize the main steps or logic the function employs to achieve its purpose.
3. **Key Algorithms or Decisions:** Highlight any significant algorithms, data structures, or decision points within the function.
4. **Side Effects:** Note any side effects or changes to the state (e.g., modifying global variables, I/O operations).




Steps to do this task:
1) Read and understand Code Summaries

2) Analyze the python code its in <user_input> and </user_input>

3) Understant function purpose

4) Understant core logic

5) Understant Key Algorithms or Decisions

6) Understant Side Effects

7) Write Function Purpose

8) Write core logic

9) Write Key Algorithms or Decisions

10) Write Side Effects

12) Return the code summary message


<user_input>
```python
{code}
```
</user_input>


Trick for return type, you return should be an only message. You should think before of the result. 
You should not responsible to explain your message return. Only return message. Only return the message. Don't write any other text

"""


        if return_prompt:
            return tldr + "\n---------SECOND STEP---------\n" + input_text

        tldr_result = self.default_completion(tldr)




        input_text = self.default_completion(input_text)
        




        last_step = f"""
Hi, please make a summary of this code analyses:

{input_text}

Generate a summary with 4 sentences and retur it. Only return summar no other text

"""
        result = self.default_completion(last_step)



    


        total_result = f"""
**TL;DR:**
{tldr_result}

**Summary:**
{result}

"""

        return total_result




    def code_to_tags(self, code, return_prompt=False):
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
        if return_prompt:
            return input_text

        result = self.default_completion(input_text)

        return result

    def generate_readme(self, top_library, summary_list, return_prompt=False):
        result = None
        with tracer.start_span("readme-generate") as span:
            try:
                span.set_attribute("AI.default_model", AI.default_model)
                span.set_attribute("summary_list_len", len(str(summary_list)))
                prompt_1 = f"""
Hi there is an list of elements and summaries:

{summary_list}


Explain the purpose of this '{top_library}' library and its elements in a few sentences.
"""

                

                # Also generate the usage aim
                prompt_2 = f"""
Hi there is an list of elements and summaries:

{summary_list}


Explain the usage aim of this '{top_library}' library and its elements in a few sentences.
"""


                if return_prompt:
                    return prompt_1 + "\n---------SECOND STEP---------\n" + prompt_2

                summary = self.default_completion(prompt_1)
                usage_aim = self.default_completion(prompt_2)

                result = (
                    '<b class="custom_code_highlight_green">Explanation:</b><br>'
                    + summary
                    + '\n\n<b class="custom_code_highlight_green">Use Case:</b><br>'
                    + usage_aim
                )
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR))
                span.record_exception(e)

        return result

    def difference_to_commit_message(self, code_old, code_new, return_prompt=False):
        input_text = f"""
Generate a small commit message. The output should be one sentence. There is an information about conventional commit message. 


Conventional Commits
The Conventional Commits specification is a lightweight convention for commit messages. It provides a set of rules for adding human—and machine-readable meaning to commit messages. Thus, the main purpose is to make it easier to create automated tools on top of commit messages.

In this sense, this convention adds some specific elements to commit messages. One main element is the commit type. The table below shows the most common commit types included in the specification:

Type	Description
feat	Introduce a new feature to the codebase
fix	Fix a bug in the codebase
docs	Create/update documentation
style	Feature and updates related to styling
refactor	Refactor a specific section of the codebase
test	Add or update code related to testing
chore	Regular code maintenance



Steps to do this task:
1) Read and understand conventional commits

2) Find the change of old version and new_version they are between of <user_input> and </user_input>

3) Chose the type of change by conventional commits

4) Return the commit message



Trick for return type, you return should be an message only. You should think before of the result. 
You should not responsible to explain your message return. Only return message answer

<user_input>
```python old version
{code_old}
```

```python new version
{code_new}
```
</user_input>


Don't forget the before prompt of <user_input>. Return only the message




"""

        if return_prompt:
            return input_text

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
