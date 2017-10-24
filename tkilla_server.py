import socket
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bd import User, users

class MainServer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.client = object()
        self.addr = str()
        self.data = str()
        self.json_data = str()
        self.string = str()
        self.sock = str()
        self.clients = list()
        self.chat = Chat()
        self.user = User
        self.tokin_dict = dict()
        self.users_list = list()
        self.accounts_dict = dict()

    def connect(self):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(15)
        self.run()

    def run(self):
        while True:
            self.client, self.addr = self.sock.accept()
            self.clients.append(self.client)

            try:
                #print(self.client)
                self.data = self.client.recv(1024)
                self.json_data = json.loads(self.data.decode('utf-8'))
                self.respons_generator()
            except IndentationError:
                print('Error 400. Wrong JSON-object.')
                self.run()
            except json.decoder.JSONDecodeError:
                print('Error 400. Wrong JSON-object. 2')
                self.run()

    def respons_generator(self):
        if 'tokin' in self.json_data.keys():
            self.presence()
        elif self.json_data['action'] == "authenticate":
            self.authenticate()
        elif self.json_data['action'] == "msg":
            self.conversation()
        elif self.json_data['action'] == "presence":
            self.presence()
        else:
            error_response = {
                "response": 400,
                "error": "Bad request"
                }
            self.string = json.dumps(error_response)
            self.client.send(self.string)
            self.client.close()

    def authenticate(self):
        #if self.json_data['user']['account_name'] in users.keys():
        if session.query(User).filter_by(login = self.json_data['user']['account_name']).first():
            bd_user = session.query(User).filter_by(login = self.json_data['user']['account_name']).first()
            #if self.json_data['user']['password'] == users[self.json_data['user']['account_name']]:
            if self.json_data['user']['password'] == bd_user.password:
                print("Пользователь с ником %s прошел аунтентификацию %s" % (self.json_data['user']['account_name'], self.json_data['time']) )
                #self.user = User(self.json_data['user']['account_name'], self.json_data['user']['password'])
                if self.json_data['user']['account_name'] in [user.login for user in self.users_list]:
                    respons = {
                        "response": 200,
                        "alert": "Authentication is successful",
                        "tokin": self.accounts_dict[self.json_data['user']['account_name']].tokin
                    }
                else:
                    #self.user = User(self.json_data['user']['account_name'], self.json_data['user']['password'])
                #Создание токина
                    #self.user.create_tokin()
                    bd_user.create_tokin()
                    session.commit()
                    #self.users_list.append(self.user)
                    self.users_list.append(bd_user)
                    #self.accounts_dict[self.json_data['user']['account_name']] = self.user
                    self.accounts_dict[self.json_data['user']['account_name']] = bd_user
                    #self.tokin_dict[self.user.tokin] = self.user
                    self.tokin_dict[self.user.tokin] = bd_user
                    respons = {
                        "response": 200,
                        "alert": "Authentication is successful",
                        "tokin": bd_user.tokin
                    }
                print(self.users_list)
                self.string = json.dumps(respons)
                self.client.send(self.string.encode('utf-8'))
                self.client.close()
            else:
                error_response = {
                    "response": 402,
                    "error": "Wrong password or no account with that name"
                    }
                print("Ошибка 402, \"Wrong password\"")
                self.string = json.dumps(error_response)
                self.client.send(self.string.encode('utf-8'))
                self.client.close()

        else:
            error_response = {
                "response": 402,
                "error": "No account with that name"
            }
            print("Ошибка 402, \"Wrong password or no account with that name\"")
            self.string = json.dumps(error_response)
            self.client.send(self.string.encode('utf-8'))
            self.client.close()

    def conversation(self):
        #Здесь будет реализовано общение между пользователями, однажды...
        print('Здесь будет реализовано общение между пользователями, однажды...')
        #self.chat = Chat()
        try:
            if self.json_data['mode'] == 'w':
                self.chat.add_writing_client(self.client)
                return

            elif self.json_data['mode'] == 'r':
                self.chat.add_reading_client(self.client)
                print(self.chat.reading_clients)
                return

            else:
                print('Неверный режим запуска {}. Режим запуска должен быть r - чтение или w - запись'.format(self.json_data['mode']))
        except KeyError:
            pass
            #print('Без модуля')

        #print(self.json_data['message'])
        self.chat.chat_history.append(self.json_data)
        #self.chat.read_requests()  # Получаем входные сообщения
        print(self.chat.chat_history)
        self.chat.write_requests() # Выполним отправку входящих сообщений

    def presence(self):
        #if self.json_data['tokin'] in self.tokin_dict.keys():
        if session.query(User).filter_by(tokin = self.json_data['tokin']).first():
            u = session.query(User).filter_by(tokin = self.json_data['tokin']).first()
            #print('Вот все мои токины\n', self.tokin_dict.keys())
            #u = self.tokin_dict[self.json_data['tokin']]
            respons = {
                "response": 400,
                "alert": u.login,
                "tokin": u.tokin
            }
            self.string = json.dumps(respons)
            self.client.send(self.string.encode('utf-8'))
            self.client.close()
        else:
            print('Неверный токин клиента.')
            respons = {
                "response": 403,
                "alert": "Неверный токин. Пройди аунтентификацию.",
            }
            self.string = json.dumps(respons)
            self.client.send(self.string.encode('utf-8'))
            self.client.close()

class Chat:
    def __init__(self):
        self.chat_history = list()
        self.instant_messages = list()
        self.clients = list()
        self.writing_clients = list()
        self.reading_clients = list()

    def add_writing_client(self, client):
        self.writing_clients.append(client)

    def add_reading_client(self, client):
        self.reading_clients.append(client)

    def read_requests(self):
        """
        Чтение сообщений, которые будут посылать клиенты
        """
        self.instant_messages = list()
        for sock in self.writing_clients:
            try:
                self.data = sock.recv(1024).decode('utf-8')
                self.chat_history.append(self.data)
                self.instant_messages.append(self.data)
            except:
                print('Какие-то проблемы при чтении сообщений отправленных в чат')
                #Реализовать отключение клиента TODO

    def write_requests(self):
        """
        Отправка сообщений тем клиентам, которые их ждут
        """
        for sock in self.reading_clients:
        #    for message in self.chat_history:
            message = self.chat_history[-1]
            try:
                message = json.dumps(message)
                resp = message.encode('utf-8')
                sock.send(resp)

            except ConnectionResetError:
                print('Удаленный хост принудительно разорвал существующее подключение')

                #    print('Какие-то проблемы при записи сообщений отправленных в чат')
                    # Реализовать отключение клиента

if __name__ == '__main__':

    engine = create_engine('sqlite:///tkilla_database.db', echo=False)
    pool_recycle = 7200  # переустановление соединения с бд через каждые 2 часа

    Session = sessionmaker(bind=engine)
    session = Session()

    server = MainServer('', 8888)
    server.connect()