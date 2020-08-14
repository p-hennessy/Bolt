import socket

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from pygments.lexers.python import Python3Lexer


class Shell():
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = (host, port)

        self.history = FileHistory("/tmp/bolt-shell-history")
        self.prompt_session = PromptSession(
            history=self.history,
            enable_history_search=True,
            lexer=PygmentsLexer(Python3Lexer)
        )

    def connect(self):
        self.sock.connect(self.address)
        self.sock.sendall("".encode())
        self.recv()

    def disconnect(self):
        self.sock.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def prompt(self):
        style = Style.from_dict({'': '#ffffff', 'prompt': 'ansigreen'})
        prompt = [('class:prompt', 'bolt'), ('class:dollar', '$ ')]

        return self.prompt_session.prompt(prompt, style=style, auto_suggest=AutoSuggestFromHistory())

    def send(self, message):
        self.history.append_string(message)
        self.sock.sendall(f"{message}\n".encode())

    def recv(self):
        BUFF_SIZE = 4096
        data = b''
        while True:
            part = self.sock.recv(BUFF_SIZE)
            data += part
            if len(part) < BUFF_SIZE:
                break
            
        return data.decode()[:-5]
