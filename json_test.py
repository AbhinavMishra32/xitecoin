import json

a = json.dumps({"A":"a", "B":"b"})
print(type(a))

b = {"x":2133/12, "b":"a", "c":4 }

print(type(b.get("x")))