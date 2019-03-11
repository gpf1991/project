#coding=utf-8
'''
AID httpserver v3.0
'''

from socket import *
import sys
from threading import Thread
from settings import *

def connect_frame(request):
    s = socket()
    try:
        s.connect(frame_address) #连接webframe
    except Exception as e:
        print('Connect error:', e)
        return
    s.send(request.encode())
    response = s.recv(4096*10).decode()
    s.close()
    return response


#将httpserver功能封装为类
class HTTPServer(object):
    def __init__(self, address):
        self.address = address
        self.create_socket()
        self.bind(address)

    #创建套接字
    def create_socket(self):
        self.sockfd = socket()
        self.sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    #绑定地址
    def bind(self, address):
        self.ip = address[0]
        self.port = address[1]
        self.sockfd.bind(address)

    #启动服务器
    def serve_forever(self):
        self.sockfd.listen(10)
        print('Listen to the port %d...' %self.port)
        while True:
            connfd, addr = self.sockfd.accept()
            print('Connect from:', addr)
            handle_client = Thread(target=self.handle, args=(connfd,))
            handle_client.setDaemon(True)
            handle_client.start()

    #处理客户端请求
    def handle(self, connfd):
        #接收请求
        request = connfd.recv(1024)
        # print(request)
        if not request:
            connfd.close()
            return
        request_lines = request.splitlines()
        #获取请求行
        request_line = request_lines[0].decode('utf-8')
        print('请求:', request_line)

        #向webframe发送
        response_body = connect_frame(request_line)

        if response_body == '404':
            response_headers = 'HTTP/1.1 404 Not Found\r\n'
            response_body = '<h1>Not Found</h1>'
        else:
            response_headers = 'HTTP/1.1 200 OK\r\n'
        response_headers += '\r\n'
        response = response_headers + response_body
        connfd.send(response.encode())
        connfd.close()


if __name__ == '__main__':
    httpd = HTTPServer(ADDR)
    httpd.serve_forever()  #启动http服务

