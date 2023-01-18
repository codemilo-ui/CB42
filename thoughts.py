import random, randfacts, json, requests, string
def get_shower(f):
	data = requests.get('https://www.reddit.com/r/showerthoughts/top.json?sort=top&t=week&limit=100')

	data = json.loads(data.text)
	while True:
		data = requests.get('https://www.reddit.com/r/showerthoughts/top.json?sort=top&t=week&limit=100')

		data = json.loads(data.text)
		try:
			if data["message"] == "Too Many Requests":
				print("Too Many Requests")
		except KeyError:
			break
	data = data["data"]["children"][f]["data"]

	title = "\n\"" + data["title"] + "\""
	author = "    -" + data["author"] + "\n"
	return [title, author]

with open("thoughts.json", "r") as f:
	data = json.load(f)
ts = data["thoughts"]
for i in range(100):
	ts.append(get_shower(i))
	print(f"{i} completed")

ts = list(set(ts))
data["thoughts"] = ts
with open("data.json", "w") as f:
	json.dump(data, f)
print(ts)