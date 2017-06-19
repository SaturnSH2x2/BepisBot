import json

def load_js(path):
	try:
		with open(path, "r") as js:
			data = json.load(js)
			js.close()
	except FileNotFoundError:
		data = {}

	return data

def save_js(path, data):
	js = open(path, "w+")
	json.dump(data, js)
	js.close()
	
	return
