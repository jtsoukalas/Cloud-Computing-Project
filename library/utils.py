import urllib.request
import bs4
import concurrent.futures
import requests
import threading
import _thread
import multiprocessing
import os
import psutil
import time

positive_words_path = "./assets/positive_words.txt"
negative_words_path = "./assets/negative_words.txt"
script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
abs_positive_file_path = os.path.join(script_dir, positive_words_path)
abs_negative_file_path = os.path.join(script_dir, negative_words_path)

def article_scraper(url):
    response = requests.get(url)
    if response is not None:
        html = bs4.BeautifulSoup(response.text, 'html.parser')
        title = html.select("#firstHeading")[0].text
        paragraphs = html.select("p")
        textual_data = " ".join([para.text for para in paragraphs[0:5]])
    return textual_data.split(" ")


def pos_neg_words(path_pos, path_neg):
    file_pos = open(path_pos, "r")
    file_pos_content = file_pos.read()
    lpositive_words = file_pos_content.split('\n')
    file_neg = open(path_neg, "r")
    file_neg_content = file_neg.read()
    lnegative_words = file_neg_content.split('\n')
    return lpositive_words, lnegative_words


def article_sentiment_analysis(url):
    lpos_words, lneg_words = pos_neg_words(abs_positive_file_path, abs_negative_file_path)
    article_words = article_scraper(url)
    spos_words, sneg_words, sarticle_words = set(lpos_words), set(lneg_words), set(article_words)
    num_pos_words = len(spos_words.intersection(sarticle_words))
    num_neg_words = len(sneg_words.intersection(sarticle_words))
    # print(num_pos_words,num_neg_words, end=" ")
    if num_pos_words == num_neg_words or num_pos_words + 1 == num_neg_words or num_pos_words == num_neg_words + 1:
        return url.split("/")[-1], "neutral"
    if num_pos_words > num_neg_words:
        return url.split("/")[-1], "positive"

    return url.split("/")[-1], "negative"

def monitor_CPU_Ram():
    mem = psutil.virtual_memory()
    print("{}: Memory: {} CPU: {}".format(time.ctime(time.time()), mem.percent,
                                          psutil.cpu_percent(interval=1.0, percpu=True)))

def mem_stats():
    mem = psutil.virtual_memory()
    print("Nuber of CPUs: ", psutil.cpu_count(), " Total physical memory", str(int(mem.total / 1024 ** 2)), "MB")
    return time.time()

