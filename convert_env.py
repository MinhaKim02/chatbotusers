# convert_env.py
import json

with open(".env", "r") as f:
    line = f.read().strip()
    key, raw_json = line.split("=", 1)
    json_data = json.loads(raw_json)
    json_data["private_key"] = json_data["private_key"].replace("\n", "\\n")
    print(f'{key}={json.dumps(json_data)}')
