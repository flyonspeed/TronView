from collections import deque

class ChangeHistory:
    def __init__(self, max_history=100):
        self.history = deque(maxlen=max_history)

    def add_change(self, change_type, data):
        self.history.append({"type": change_type, "data": data})
        #print(f"history added: {change_type}, {data}")

    def undo(self):
        if self.history:
            return self.history.pop()
        return None
    
    def clear(self):
        self.history.clear()

def undo_last_change(change_history, shared):
    change = change_history.undo()
    if change:
        print(f"undoing change: {change}")
        if change["type"] == "move":
            change["data"]["object"].move(*change["data"]["old_pos"])
        elif change["type"] == "delete":
            shared.CurrentScreen.ScreenObjects.append(change["data"]["object"])
        elif change["type"] == "add":
            shared.CurrentScreen.ScreenObjects.remove(change["data"]["object"])
        elif change["type"] == "option_change":
            setattr(change["data"]["object"].module, change["data"]["option"], change["data"]["old_value"])
            if hasattr(change["data"]["object"].module, 'update_option'):
                change["data"]["object"].module.update_option(change["data"]["option"], change["data"]["old_value"])
        elif change["type"] == "resize":
            change["data"]["object"].resize(*change["data"]["old_size"])
    else:
        print("no change to undo")
