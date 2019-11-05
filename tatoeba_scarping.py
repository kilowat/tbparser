from lib.parser import Parser
import time
import threading

limit = 5  # max download file every word
thread_count = 5  # numbers how match start the threads

# to do get from db
words = [
    "run",
    "help",
    "take"
]

start_time = time.time()


def run():
    p = Parser(limit)
    while len(words) > 0:
        res = p.parse(words.pop())
    #       todo insert in to db
    print("--- %s seconds ---" % (time.time() - start_time))


threads = []

for i in range(thread_count):
    t = threading.Thread(target=run)
    threads.append(t)
    t.start()
