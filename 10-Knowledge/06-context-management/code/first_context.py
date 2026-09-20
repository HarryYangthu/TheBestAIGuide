from context import ROOT, initial_messages, measure, read_fixture, save_json

messages = initial_messages(read_fixture("task.json"))
save_json(ROOT / "runs/first/messages.json", messages)
print("messages=" + str(len(messages)))
print("serialized_input_tokens=" + str(measure(messages)))
print("artifacts=runs/first/messages.json")
