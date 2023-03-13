class getApiKeyException(Exception):
    def __init__(self, value):
        self.value = value


class balanceException(Exception):
    def __init__(self, value):
        self.value = value
