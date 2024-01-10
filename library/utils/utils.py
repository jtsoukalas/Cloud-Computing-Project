import bs4
import requests
import os
import psutil
import time

class Utils:
    positive_words_path = "../assets/positive_words.txt"
    negative_words_path = "../assets/negative_words.txt"
    script_dir = os.path.dirname(__file__)  #
    abs_positive_file_path = os.path.join(script_dir, positive_words_path)
    abs_negative_file_path = os.path.join(script_dir, negative_words_path)

    cashed_urls = []
    cashed_urls_num = 20

    @staticmethod
    def article_scraper(url):
        textual_data = ""
        response = requests.get(url)
        if response is not None:
            html = bs4.BeautifulSoup(response.text, 'html.parser')
            title = html.select("#firstHeading")[0].text
            paragraphs = html.select("p")
            textual_data = " ".join([para.text for para in paragraphs[0:5]])
        return textual_data.split(" ")

    @staticmethod
    def pos_neg_words(path_pos, path_neg):
        file_pos = open(path_pos, "r")
        file_pos_content = file_pos.read()
        found_positive_words = file_pos_content.split('\n')
        file_neg = open(path_neg, "r")
        file_neg_content = file_neg.read()
        found_negative_words = file_neg_content.split('\n')
        return found_positive_words, found_negative_words

    @staticmethod
    def article_sentiment_analysis(url):
        found_pos_words, found_neg_words = Utils.pos_neg_words(Utils.abs_positive_file_path, Utils.abs_negative_file_path)
        article_words = Utils.article_scraper(url)
        spos_words, sneg_words, sarticle_words = set(found_pos_words), set(found_neg_words), set(article_words)
        num_pos_words = len(spos_words.intersection(sarticle_words))
        num_neg_words = len(sneg_words.intersection(sarticle_words))

        mem_used, cpu_percent = Utils.monitor_cpu_ram()
        cpu_percent = sum(cpu_percent) / len(cpu_percent)
        if num_pos_words == num_neg_words or num_pos_words + 1 == num_neg_words or num_pos_words == num_neg_words + 1:
            return url.split("/")[-1], "neutral", mem_used, cpu_percent
        if num_pos_words > num_neg_words:
            return url.split("/")[-1], "positive", mem_used, cpu_percent

        return url.split("/")[-1], "negative", mem_used, cpu_percent

    @staticmethod
    def article_sentiment_analysis_thread(url, response, index):
        response[index] = Utils.article_sentiment_analysis(url)

    @staticmethod
    def monitor_cpu_ram():
        mem = psutil.virtual_memory()
        return mem.percent, psutil.cpu_percent(interval=None, percpu=True)

    @staticmethod
    def mem_stats():
        mem = psutil.virtual_memory()
        return time.time(), psutil.cpu_count(), mem.total / 1024 ** 2

    @staticmethod
    def cashing_urls():
        for i in range(Utils.cashed_urls_num):
            url = requests.get("https://en.wikipedia.org/wiki/Special:Random")
            Utils.cashed_urls.append(url.url)

        print(Utils.cashed_urls_num, 'urls cashed')

    @staticmethod
    def get_num_cashed_urls(num):
        if num > Utils.cashed_urls_num:
            return None
        return Utils.cashed_urls[0:num]

    @staticmethod
    def return_result(cpu_count, num, response, start_time, total_mem):
        while None in response:
            pass
        total_mem_used = 0
        total_cpu = 0
        for i in range(len(response)):
            total_mem_used += response[i][2]
            total_cpu += response[i][3]
            response[i] = response[i][:2]
        execution_time = str((time.time() - start_time))
        return {"response": response, "time": execution_time, "cpu_count": cpu_count, "total_mem": total_mem,
                "average_mem": total_mem_used / int(num), "average_cpu_percentage": total_cpu / int(num)}
