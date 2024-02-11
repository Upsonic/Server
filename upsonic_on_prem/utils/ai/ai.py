from transformers import AutoTokenizer, AutoModelWithLMHead, SummarizationPipeline
import os

this_dir = os.path.dirname(os.path.abspath(__file__))

code_to_document_pipeline = None
code_to_document_pipeline_folder = os.path.join(this_dir, "SEBIS",
                                                "code_trans_t5_small_code_documentation_generation_python")


def create_code_to_document_pipeline():
    global code_to_document_pipeline
    code_to_document_pipeline = SummarizationPipeline(
        model=AutoModelWithLMHead.from_pretrained(code_to_document_pipeline_folder),
        tokenizer=AutoTokenizer.from_pretrained(code_to_document_pipeline_folder,
                                                skip_special_tokens=True),
    )


def get_code_to_document_pipeline():
    global code_to_document_pipeline
    if code_to_document_pipeline is None:
        create_code_to_document_pipeline()
    return code_to_document_pipeline


class AI_:
    def __init__(self):
        pass

    def code_to_documentation(self, data):
        self.code_to_document_pipeline = get_code_to_document_pipeline()
        return self.code_to_document_pipeline([data])[0]["summary_text"]


AI = AI_()
