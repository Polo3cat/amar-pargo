from .tool import Tool

class DebugTool(Tool):
	def __init__(self):
		pass

	def evaluate(self, screenshot):
		return 1


	def act(self, screenshot):
		return 'wait', 0
