

import os

from dotenv import load_dotenv
import requests

load_dotenv(dotenv_path=".env")


this_dir = os.path.dirname(os.path.abspath(__file__))



import ollama

from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
class AI_:
    def __init__(self):
        pass


    def search_by_documentation(self, the_contents, question, min_score=500, how_many_result=10):

        from langchain.docstore.document import Document

        texts = []

        for content in the_contents:
            text = content["name"] + ":" + str(content["documentation"])
            texts.append(Document(page_content=text, metadata={"name": content["name"]}))

        oembed = OllamaEmbeddings(base_url="http://localhost:11434", model="nomic-embed-text-upsonic")
        vectorstore = Chroma.from_documents(documents=texts, embedding=oembed)



        docs = vectorstore.similarity_search_with_score(question, k=how_many_result)


        results = []

        for doc in docs:
            if doc[1] < min_score:


                doc = [doc[0].metadata["name"],doc[0].page_content.replace(doc[0].metadata["name"]+":", ""), doc[1]]
                results.append(doc)

        results = [list(t) for t in set(tuple(element) for element in results)]

        return results





    def gemmma(self, input_text):
        print("Gemma q:", input_text)
        response = ollama.chat(model='gemma-2b-upsonic', messages=[
        {
            'role': 'user',
            'content': input_text,
        },
        ])
        result = response['message']['content']
        print("Gemma r:", result)

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


        result = self.gemmma(input_text)
        return result

    def code_to_documentation(self, code):
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


        result = self.gemmma(input_text)
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

Note: Please identify and describe the errors in a clear and informative manner.

"""


        result = self.gemmma(input_text)
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

In your response, give a clear outline of potential security issues present and elaborate on how one might strengthen the overall security. The focus is on text-based analysis, so no need to provide an actual piece of code in your response.
"""


        result = self.gemmma(input_text)
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


        result = self.gemmma(input_text)
        return result        


AI = AI_()
