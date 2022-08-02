import queue
import threading
import urllib.error
import urllib.parse
import urllib.request

threads = 50
target_url = "http://testphp.vulnweb.com"
wordlist_file = "all.txt"  # from SVNDigger
resume = None
user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) " \
             "Gecko/20100101 " \
             "Firefox/19.0"


def build_wordlist(wordlst_file):
    with open(wordlst_file, "r") as fd:
        raw_words = [line.rstrip('\n') for line in fd]
    found_resume = False
    words = queue.Queue()

    for word in raw_words:
        if resume and not found_resume and word == resume:
            found_resume = True
            print(f"Resuming wordlist from: {resume}")
        elif not resume or found_resume:
            words.put(word)
    return words


def dir_bruter(extensions=None):
    while not word_queue.empty():
        attempt = word_queue.get()
        attempt_list = []

        # check if there is a file extension if not
        # it's a directory path we're bruting
        if "." not in attempt:
            attempt_list.append(f"/{attempt}/")
        else:
            attempt_list.append(f"/{attempt}")

        # if we want to bruteforce extensions
        if extensions:
            attempt_list.extend(f"/{attempt}{extension}" for extension in extensions)
        # iterate over our list of attempts
        for brute in attempt_list:
            url = f"{target_url}{urllib.parse.quote(brute)}"
            try:
                headers = {"User-Agent": user_agent}
                r = urllib.request.Request(url, headers=headers)
                response = urllib.request.urlopen(r)
                if len(response.read()):
                    print("[%d] => %s" % (response.code, url))
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    print("!!! %d => %s" % (e.code, url))


word_queue = build_wordlist(wordlist_file)
file_extensions = [".php", ".bak", ".orig", ".inc"]

for _ in range(threads):
    t = threading.Thread(target=dir_bruter, args=(file_extensions,))
    t.start()
