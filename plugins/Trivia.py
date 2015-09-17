import threading

def init(bot):
    triviaThread = Trivia(bot)
    triviaThread.start()

    return triviaThread

class Trivia(threading.Thread):
    def __init__(self, bot):
        super(Trivia, self).__init__()
        bot.subscribe("recieve.message", self.onMessage)

    def run(self):
        pass

    def onMessage(self, args):
        print args["msg"]
