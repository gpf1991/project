#coding=utf-8
'''
模拟网站后端处理程序
'''
from socket import *
import sys
from select import select
from views import *

frame_ip = '176.136.4.48'
frame_port = 8080

if len(sys.argv) < 3:
    pass
else:
    frame_ip = sys.argv[1]
    frame_port = sys.argv[2]
frame_address = (frame_ip, frame_port)

#静态网页位置
STATIC_DIR = './static'

#url列表，决定我们可以处理什么样的数据请求
urls = [
        ('/time', show_time), 
        ('/hello', say_hello),
        ('/bye', say_bye)
]

#应用类，将功能封装
class Application(object):
    def __init__(self):
        self.sockfd = socket()
        self.sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sockfd.bind(frame_address)
        self.rlist = [self.sockfd]
        self.wlist = []
        self.xlist = []

    def runserver(self):
        self.sockfd.listen(5)
        print('Listen to the port %d...' %frame_port)
        while True:
            rs,ws,xs = select(self.rlist, self.wlist, self.xlist)
            for r in rs:
                if r is self.sockfd:
                    connfd, addr = r.accept()
                    self.rlist.append(connfd)
                else:
                    request = r.recv(1024).decode()
                    self.handle(r, request)

    def handle(self, connfd, request):
        method = request.split(' ')[0]
        path_info = request.split(' ')[1]

        if method == 'GET':
            if path_info == '/' or path_info[-5:] == '.html':
                response = self.get_html(path_info)
            else:
                response = self.get_data(path_info)
        elif method == 'POST':
            pass
        connfd.send(response.encode())
        connfd.close()
        self.rlist.remove(connfd)

    def get_html(self, path_info):
        if path_info == '/':
            get_file = STATIC_DIR + '/index.html'
        else:
            get_file = STATIC_DIR + path_info
        try:
            fd = open(get_file)
        except IOError:
            response = '404'
        else:
            response = fd.read()
        finally:
            return response

    def get_data(self, path_info):
        for url, func in urls:
            if path_info == url:
                response = func()
                break
        else:
            response = '404'
        return response


if __name__ == '__main__':
    app = Application()
    app.runserver()  #启动应用框架服务
