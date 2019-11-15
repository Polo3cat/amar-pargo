import abc


class NothingError(Exception):
	def __init__(self, message):
		self.message = message


class Tool(abc.ABC):
	def __init__(self):
		pass

	@abc.abstractmethod
	def evaluate(self, screenshot):
		...

	@abc.abstractmethod
	def act(self, screenshot):
		...
