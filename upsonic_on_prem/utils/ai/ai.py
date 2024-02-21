from transformers import AutoTokenizer, AutoModelWithLMHead, SummarizationPipeline
import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
ai_model = os.environ.get("ai_model", "SEBIS/code_trans_t5_base_code_documentation_generation_python_multitask/")

min_length = os.environ.get("min_length", 30)
max_length = os.environ.get("max_length", 512)
num_beams = os.environ.get("num_beams", 4)
repetition_penalty = os.environ.get("repetition_penalty", 2.5)
temperature = os.environ.get("temperature", 1.2)
do_sample = os.environ.get("do_sample", "true").lower() == "true"

this_dir = os.path.dirname(os.path.abspath(__file__))

code_to_document_pipeline = None
code_to_document_pipeline_folder = os.path.join(this_dir, ai_model)

build_my_languages = os.path.join(this_dir, "build/my-languages.so")
tree_sitter_python = os.path.join(this_dir, "tree-sitter-python")

from tree_sitter import Language, Parser

Language.build_library(
    build_my_languages,
    [tree_sitter_python]
)

PYTHON_LANGUAGE = Language(build_my_languages, 'python')
parser = Parser()
parser.set_language(PYTHON_LANGUAGE)



def create_code_to_document_pipeline():
    global code_to_document_pipeline
    model = AutoModelWithLMHead.from_pretrained(code_to_document_pipeline_folder)
    tokenizer = AutoTokenizer.from_pretrained(code_to_document_pipeline_folder, skip_special_tokens=True)
    code_to_document_pipeline = SummarizationPipeline(
        model=model,
        tokenizer=tokenizer,
        max_length=max_length,
        min_length=min_length,
        num_beams=num_beams,
        repetition_penalty=repetition_penalty,
        temperature=temperature,
        do_sample=do_sample,
    )


def get_code_to_document_pipeline():
    global code_to_document_pipeline
    if code_to_document_pipeline is None:
        create_code_to_document_pipeline()
    return code_to_document_pipeline


class AI_:
    def __init__(self):
        pass

    def code_to_documentation(self, code):
        self.code_to_document_pipeline = get_code_to_document_pipeline()
        code_list = []

        def get_string_from_code(node, lines):
            line_start = node.start_point[0]
            line_end = node.end_point[0]
            char_start = node.start_point[1]
            char_end = node.end_point[1]
            if line_start != line_end:
                code_list.append(
                    ' '.join([lines[line_start][char_start:]] + lines[line_start + 1:line_end] + [
                        lines[line_end][:char_end]]))
            else:
                code_list.append(lines[line_start][char_start:char_end])

        def my_traverse(node, code_list):
            lines = code.split('\n')
            if node.child_count == 0:
                get_string_from_code(node, lines)
            elif node.type == 'string':
                get_string_from_code(node, lines)
            else:
                for n in node.children:
                    my_traverse(n, code_list)

            return ' '.join(code_list)

        tree = parser.parse(bytes(code, "utf8"))
        code_list = []
        tokenized_code = "function documentation generation python: " + my_traverse(tree.root_node, code_list)
        print("AI", code)
        print("AI tokenized", tokenized_code)
        result = self.code_to_document_pipeline([tokenized_code])[0]["summary_text"]
        print("AI", result)
        return result


AI = AI_()
