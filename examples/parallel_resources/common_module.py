from multiprocessing import Queue

queue = Queue()
print ("Loaded queue")
queue.put("first")
queue.put("second")

# eof
