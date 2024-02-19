import requests
import re
import os
import urllib.request
import pandas as pd
import threading
import time
from tqdm import tqdm

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}

def getPaperPdf(doi):
    # 下载文献
    sci_Hub_Url = "https://www.sci-hub.ee/"
    paper_url = sci_Hub_Url + doi
    pattern = '/.*?\.pdf'
    content = requests.get(paper_url, headers=headers)
    download_url = re.findall(pattern, content.text)
    download_url[1] = "https:" + download_url[1]
    path = r"paper"
    if not os.path.exists(path):
        os.makedirs(path)

    req = urllib.request.Request(download_url[1], headers=headers)
    u = urllib.request.urlopen(req, timeout=5)

    # 获取文献名称
    title_base_url = "https://api.crossref.org/works/"
    url = title_base_url + doi
    response = requests.get(url)
    title = ""
    if response.status_code == 200:
        data = response.json()
        title = data["message"]["title"][0]
        title = title.replace(':', '')
    else:
        print("Failed to fetch title for DOI:", doi)

    # 写入
    file_name = title + ".pdf"
    f = open(os.path.join(path, file_name), 'wb')
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
        f.write(buffer)
    f.close()
    print("Successful to download" + " " + file_name)

# 开启多线程
def download_papers(df):
    threads = []
    for doi in df['doi']:
        thread = threading.Thread(target=getPaperPdf, args=(doi,))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

if __name__ == '__main__':
    print("下载中......................................")
    start_time = time.time()  # 记录开始下载的时间戳
    df = pd.read_csv('doi.csv')
    download_papers(df)
    end_time = time.time()  # 记录结束下载的时间戳
    download_time = end_time - start_time  # 计算下载所花费的时间
    print("总下载时间：",download_time)
    print("下载完成")