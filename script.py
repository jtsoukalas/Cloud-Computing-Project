import requests
import time

batches = 0

# request from localhost:5000/get_cashed to get the cashed urls
response = requests.get("http://localhost:5000/get_cashed")

# get the urls from the response
urls = response.json()["urls"]

# keep only the first 800 urls
urls = urls[:800]

# split the urls into batches
if batches == 0:
    batched_urls = urls
else:
    batched_urls = [urls[i:i + batches] for i in range(0, len(urls), batches)]

start_time = time.time()

# for each batch, send a request to localhost:5000/scrape_list with a body containing the batch
for batch in batched_urls:
    response = requests.get("http://localhost:5000/scrape_list", json={"urls": batch})

print("Total time: ", time.time() - start_time)