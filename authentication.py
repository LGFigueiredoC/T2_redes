import json

class Authenticator ():
    def __init__(self, directory):
        self.n_users = 0
        self.data_file = "client_info.json"
        with open (self.data_file, 'w') as file:
            data =  {"login": "logTeste", "senha": "senhateste"}
            json.dump(data, file)
            data =  {"login": "logTeste2", "senha": "senhateste2"}
            json.dump(data,file)
            pass


    def create_login (self, login: str, passw: str):
        with open(self.data_file) as file:
            data = json.load(file)
            print(data)

a = Authenticator("test.json")