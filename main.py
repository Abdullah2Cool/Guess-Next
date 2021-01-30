from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

import torch
from transformers import BertTokenizer, BertForMaskedLM
import string

from datetime import datetime


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
    # decode and return the prediction
    token = ''.join(tokenizer.decode(pred[0]).split(" "))
    return token


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
    if len(text) == 0 or text == "DODO":
        return {"error": {"message": "Can't predict on empty string, enter something"}}

    try:
        # mask the areas we want the model to predict with <mask>
        text = text.strip() + " <mask>"

        # transform input
        input_ids, mask_idx = encode(bert_tokenizer, text)

        # make the prediction
        with torch.no_grad():
            prediction_all = bert_model(input_ids)[0]

        # extract the prediction corresponding to the masked word
        # take the most likely prediction and extract it's index
        prediction = prediction_all[0, mask_idx, :].topk(1).indices.tolist()

        output = decode(bert_tokenizer, prediction)

        return {"nextWord": output}

    except Exception as e:
        print(e)
        return {"error": {"message": "Something went wrong, unable to predict"}}
