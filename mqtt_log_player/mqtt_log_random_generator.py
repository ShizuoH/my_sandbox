import json
import random
import time

log = {
    "messages": []
}

for i in range(10):
    topic = "topic-name{}".format(i)
    timestamp = time.time()
    if i % 2 == 0:
        data = "data-content{}".format(i)
    else:
        data = {
            "type": random.randint(0, 1),
            "value": random.randint(0, 100),
            "message": "message-{}".format(i)
        }
    log["messages"].append({
        "name": topic,
        "timestamp": timestamp,
        "data": data
    })

with open("mqtt_log.json", "w") as f:
    json.dump(log, f)
