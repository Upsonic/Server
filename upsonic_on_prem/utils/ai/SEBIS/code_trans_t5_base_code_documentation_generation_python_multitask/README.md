---
tags:
- summarization
widget:
- text: "def e ( message , exit_code = None ) : print_log ( message , YELLOW , BOLD ) if exit_code is not None : sys . exit ( exit_code )"

---


# CodeTrans model for code documentation generation python
Pretrained model on programming language python using the t5 base model architecture. It was first released in
[this repository](https://github.com/agemagician/CodeTrans). This model is trained on tokenized python code functions: it works best with tokenized python functions.


## Model description

This CodeTrans model is based on the `t5-base` model. It has its own SentencePiece vocabulary model. It used multi-task training on 13 supervised tasks in the software development domain and 7 unsupervised datasets.

## Intended uses & limitations

The model could be used to generate the description for the python function or be fine-tuned on other python code tasks. It can be used on unparsed and untokenized python code. However, if the python code is tokenized, the performance should be better.

### How to use

Here is how to use this model to generate python function documentation using Transformers SummarizationPipeline:

```python
from transformers import AutoTokenizer, AutoModelWithLMHead, SummarizationPipeline

pipeline = SummarizationPipeline(
    model=AutoModelWithLMHead.from_pretrained("SEBIS/code_trans_t5_base_code_documentation_generation_python_multitask"),
    tokenizer=AutoTokenizer.from_pretrained("SEBIS/code_trans_t5_base_code_documentation_generation_python_multitask", skip_special_tokens=True),
    device=0
)

tokenized_code = "def e ( message , exit_code = None ) : print_log ( message , YELLOW , BOLD ) if exit_code is not None : sys . exit ( exit_code )"
pipeline([tokenized_code])
```
Run this example in [colab notebook](https://github.com/agemagician/CodeTrans/blob/main/prediction/multitask/pre-training/function%20documentation%20generation/python/base_model.ipynb).
## Training data

The supervised training tasks datasets can be downloaded on [Link](https://www.dropbox.com/sh/488bq2of10r4wvw/AACs5CGIQuwtsD7j_Ls_JAORa/finetuning_dataset?dl=0&subfolder_nav_tracking=1)

## Training procedure

### Multi-task Pretraining

The model was trained on a single TPU Pod V3-8 for 420,000 steps in total, using sequence length 512 (batch size 4096).
It has a total of approximately 220M parameters and was trained using the encoder-decoder architecture.
The optimizer used is AdaFactor with inverse square root learning rate schedule for pre-training.


## Evaluation results

For the code documentation tasks, different models achieves the following results on different programming languages (in BLEU score):

Test results :

|   Language / Model   |     Python     |      Java      |       Go       |      Php       |      Ruby      |   JavaScript   |
| -------------------- | :------------: | :------------: | :------------: | :------------: | :------------: | :------------: |
|   CodeTrans-ST-Small    |      17.31     |     16.65      |     16.89      |     23.05      |      9.19      |      13.7      |
|   CodeTrans-ST-Base     |      16.86     |     17.17      |     17.16      |     22.98      |      8.23      |      13.17     |   
|   CodeTrans-TF-Small    |      19.93     |     19.48      |     18.88      |     25.35      |     13.15      |      17.23     |
|   CodeTrans-TF-Base     |      20.26     |     20.19      |     19.50      |     25.84      |     14.07      |      18.25     |
|   CodeTrans-TF-Large    |      20.35     |     20.06      |   **19.54**    |     26.18      |     14.94      |    **18.98**   |
|   CodeTrans-MT-Small    |      19.64     |     19.00      |     19.15      |     24.68      |     14.91      |      15.26     |
|   CodeTrans-MT-Base     |    **20.39**   |     21.22      |     19.43      |   **26.23**    |   **15.26**    |      16.11     |
|   CodeTrans-MT-Large    |      20.18     |   **21.87**    |     19.38      |     26.08      |     15.00      |      16.23     |
|   CodeTrans-MT-TF-Small |      19.77     |     20.04      |     19.36      |     25.55      |     13.70      |      17.24     |
|   CodeTrans-MT-TF-Base  |      19.77     |     21.12      |     18.86      |     25.79      |     14.24      |      18.62     |
|   CodeTrans-MT-TF-Large |      18.94     |     21.42      |     18.77      |     26.20      |     14.19      |      18.83     |
|   State of the art   |      19.06     |     17.65      |     18.07      |     25.16      |     12.16      |      14.90     |


> Created by [Ahmed Elnaggar](https://twitter.com/Elnaggar_AI) | [LinkedIn](https://www.linkedin.com/in/prof-ahmed-elnaggar/) and Wei Ding | [LinkedIn](https://www.linkedin.com/in/wei-ding-92561270/)

