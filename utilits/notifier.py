class Observer:

    def update(self, subject):
        pass

    def update_user(self, subject):
        pass


class Subject:

    def __init__(self):
        self.observers = []

    def notify(self):
        for item in self.observers:
            item.update(self)

    def notify_users(self):
        for item in self.observers:
            item.update_user(self)


class SmsNotifier(Observer):

    def update(self, subject):
        print('SMS->', 'к нам присоединился', subject.users[-1].name)


class EmailNotifier(Observer):

    def update(self, subject):
        print(('EMAIL->', 'к нам присоединился', subject.users[-1].name))


class SmsNotifierUsers(Observer):

    def update_user(self, subject):
        print('SMS->', 'переименовался товар')


class EmailNotifierUsers(Observer):

    def update_user(self, subject):
        print('EMAIL->', 'переименовался товар')
