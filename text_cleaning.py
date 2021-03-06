import urllib
import pandas as pd
import requests
import io
import time
import bs4
import re
import nltk
from nltk import download
from string import punctuation as pnc
from nltk.corpus import stopwords


def as_list_soup(text):
    paragraphs = text.encode("utf-8")

    # defining a nested function to remove punctuations from the corpus
    def strip_punctuation(s):
        s = str(s)
        return "".join(c for c in s if c not in pnc)
        # output = paragraphs

    punctuation_striped = strip_punctuation(paragraphs)

    processed_article9 = punctuation_striped.lower()
    processed_article9 = re.sub("[^a-zA-Z]", " ", processed_article9)
    processed_article9 = re.sub(r"\s+", " ", processed_article9)
    ## stop word removal
    stop_words = set(stopwords.words("english"))
    words = processed_article9.split()
    stopword_removed_text = [
        i for i in processed_article9.lower().split() if i not in stop_words
    ]
    cleaned_txt_2 = stopword_removed_text
    return stopword_removed_text
