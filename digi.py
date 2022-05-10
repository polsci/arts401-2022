from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import os
import time
import re
import glob
_RE_COMBINE_WHITESPACE = re.compile(r"\s+")

message = ' - you are a coder!'
message_debug = 'You debugged some code - you are a officially a'

# load the corpus
def load_texts(corpus_dir, file_mask = "*.txt"):
    texts = []
    files = [f for f in glob.glob(corpus_dir + '/' + file_mask)]
    for file in files:
        with open(file, 'rb') as f:
            text = _RE_COMBINE_WHITESPACE.sub(' ', f.read().decode('utf8')).strip()
            texts.append(text)
    return texts


def url_to_filename(url):
    url = url.replace('https://', '').replace('http://', '')
    safe = []
    for x in url:
        if x.isalnum():
            safe.append(x)
        else:
            safe.append('-')
    filename = "".join(safe)

    if len(filename) > 200: #prevent filenames over 200 - note this could create a conflict of filenames so check        
        filename = filename[:100] + '___' + filename[-100:]
    
    return filename

def preview_html(url):
    # make the request and assign the result to a variable 'response'
    response = requests.get(url)

    if response.text:
        print(response.text)

def preview_text(url):
    # make the request and assign the result to a variable 'response'
    response = requests.get(url)

    if response.text:
        # create a BeautifulSoup object using the html.parser
        soup = BeautifulSoup(response.text.replace('>','>\n'), "html.parser") 
        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.decompose()    # rip it out
            
        # get text
        text = soup.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        #chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        #text = '\n'.join(chunk for chunk in chunks if chunk)
        text = '\n'.join(line for line in lines if line)
        
        print(text)
        
def preview_links(start, url_must_contain):
    # make the request and assign the result to a variable 'response'
    response = requests.get(start)

    # create a BeautifulSoup object using the html.parser
    soup = BeautifulSoup(response.text, "html.parser") 

    links = soup.select('a') # this is elegant and flexible!

    queue = []

    for link in links:
        if 'href' in link.attrs:
            url = urljoin(start, link['href'])
            if url_must_contain in url:
                if url not in queue:
                    queue.append(url)
                    print(url)
                    
def crawl_links(start, url_must_contain, corpus_dir, rough_clean=True):
    # make the request and assign the result to a variable 'response'
    response = requests.get(start)

    # create a BeautifulSoup object using the html.parser
    soup = BeautifulSoup(response.text, "html.parser") 

    links = soup.select('a') # this is elegant and flexible!

    if not os.path.exists(corpus_dir):
        os.makedirs(corpus_dir)
    print('Files will be saved in',corpus_dir)

    queue = []
    
    first_page_text = False
    second_page_text = False
    
    texts = {}
    remove_lines = []

    for link in links:
        if 'href' in link.attrs:
            url = urljoin(start, link['href'])
            if url_must_contain in url:
                if url not in queue:
                    queue.append(url)
                    print('Retrieving',url)
                    crawled = requests.get(url)

                    soup = BeautifulSoup(crawled.text.replace('>','>\n'), "html.parser") 
                    # kill all script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()    # rip it out

                    # get text
                    text = soup.get_text()

                    # break into lines and remove leading and trailing space on each
                    lines = (line.strip() for line in text.splitlines())
                    # break multi-headlines into a line each
                    #chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    # drop blank lines
                    #text = '\n'.join(chunk for chunk in chunks if chunk)
                    text = '\n'.join(line for line in lines if line)
                    texts[url] = text
                    
                    time.sleep(5)
    
    if rough_clean and len(text) > 1:
        first_page_lines = list(line.strip() for line in texts[list(texts.keys())[0]].splitlines())
        second_page_lines = list(line.strip() for line in texts[list(texts.keys())[1]].splitlines())

        for line in first_page_lines:
            if line in second_page_lines:
                remove_lines.append(line)
                
    for url in texts:
        text = texts[url]
        lines = list(line.strip() for line in text.splitlines())
        text = ''
        for line in lines:
            if line not in remove_lines:
                text += line + '\n'
        
        with open(corpus_dir + '/' + url_to_filename(url) + '.txt', 'w', encoding='utf-8') as f:
            f.write(text)


def black_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return("hsl(0,100%, 1%)")