from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

import torch
from transformers import BertTokenizer, BertForMaskedLM
import string


def load_bert():
    bert_tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    bert_model = BertForMaskedLM.from_pretrained("bert-base-uncased").eval()
    return bert_tokenizer, bert_model


def encode(tokenizer, text, add_special_tokens=True):
    # replace <mask> with it's corresponding representation for the model
    text = text.replace('<mask>', tokenizer.mask_token)

    # if <mask> is the last token, append a "." so that models dont predict punctuation.
    if tokenizer.mask_token == text.split()[-1]:
        text += ' .'

    # create the input vector
    input_ids = torch.tensor(
        [tokenizer.encode(text, add_special_tokens=add_special_tokens)])

    # remember the index of the <mask> character (there is only one)
    mask_idx = torch.where(input_ids == tokenizer.mask_token_id)[1].tolist()[0]

    return input_ids, mask_idx


def decode(tokenizer, pred):
    ignore_tokens = string.punctuation + '[PAD]'

    tokens = []
    for w in pred:
        token = ''.join(tokenizer.decode(w).split())
        if token not in ignore_tokens:
            tokens.append(token.replace("##", ''))

    return tokens


bert_tokenizer, bert_model = load_bert()

# create the app
app = FastAPI()

# mount the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")


# main entry point
@app.get("/")
async def homepage():
    # redirect to index.html
    return RedirectResponse("/static/index.html")


@app.get("/getNext/{text}")
async def date(text: str):
    if len(text) == 0:
        return {"error": {"message": "Can't predict on empty string, enter something"}}

    try:
        # fix the spaces
        text = text.strip().replace("+", " ")

        # mask the area we want the model to predict with <mask>
        text = text + " <mask>"

        # transform input
        input_ids, mask_idx = encode(bert_tokenizer, text)

        # make the prediction
        with torch.no_grad():
            prediction_all = bert_model(input_ids)[0]

        # extract the prediction corresponding to the masked word
        # take the toop 10 prediction and extract their index
        prediction = prediction_all[0, mask_idx, :].topk(
            10, sorted=True).indices.tolist()

        # decode the prediction
        tokens = decode(bert_tokenizer, prediction)

        # if there are no tokens returned (all punctuation and incoherent speech), return empty word
        if len(tokens) == 0:
            tokens = ['']

        # print(tokens)
        nextWord = tokens[0]

        # return 1 of the words
        return {"nextWord": nextWord}

    except Exception as e:
        print(e)
        return {"error": {"message": "Something went wrong, unable to predict"}}
