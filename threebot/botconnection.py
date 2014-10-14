import zmq


class BotConnection:
    """
    A generic BotConnection class.
    Usage: Create a new BotConnection before sending messages make sure you
    run the connect() method.
    """
    def __init__(self, endpoint, secret_key):
        self.endpoint = endpoint
        self.secret_key = str(secret_key)
        self.context = zmq.Context(1)

    def connect(self):
        self.client = self.context.socket(zmq.REQ)
        self.client.connect(self.endpoint)

        self.poll = zmq.Poller()
        self.poll.register(self.client, zmq.POLLIN)

    def disconnect(self):
        self.client.setsockopt(zmq.LINGER, 0)
        self.client.close()
        self.poll.unregister(self.client)

    def reconnect(self):
        self.disconnect()
        self.connect()

    def close(self):
        self.disconnect()
        self.context.term()
