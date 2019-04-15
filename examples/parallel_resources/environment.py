from multiprocessing import Queue

queue = Queue()
print ("Loaded queue")
queue.put("first")
queue.put("second")

def before_all(context):
    print("Queue is: %x" % id(queue))


def before_feature(context, feature):
    context.resource = queue.get()
    print("before_feature of {} the element from queue is {}".format(feature.name, context.resource))

def after_feature(context, feature):
    print("after_feature of {} the element to queue is {}".format(feature.name, context.resource))
    queue.put(context.resource)

