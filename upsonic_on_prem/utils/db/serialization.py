import cloudpickle


def serialize(obj):
    return cloudpickle.dumps(obj)

def deserialize(obj):
    return cloudpickle.loads(obj)
