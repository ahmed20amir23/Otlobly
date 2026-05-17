class Observer:
    def update(self, msg):
        pass

class UserNotifier(Observer):
    def update(self, msg):
        print("User Notification:", msg)

class AdminNotifier(Observer):
    def update(self, msg):
        print("Admin Notification:", msg)

class OrderSubject:
    def __init__(self):
        self.observers = []

    def add(self, observer):
        self.observers.append(observer)

    def notify(self, msg):
        for o in self.observers:
            o.update(msg)