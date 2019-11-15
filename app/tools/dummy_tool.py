from .tool import Tool

class DummyTool(Tool):
	def __init__(self):
		pass

	def evaluate(self, screenshot):
		return 0


	def act(self, screenshot):
		return 'wait', 1
