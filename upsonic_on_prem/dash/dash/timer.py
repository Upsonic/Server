import threading


def timer(value=None, interval=60):
    def decorate(value):
        def task():
            value()
            timer = threading.Timer(interval, task)
            timer.start()

        timer = threading.Timer(interval, task)
        timer.start()

    if value == None:
        return decorate
    else:
        decorate(value)
        return value
