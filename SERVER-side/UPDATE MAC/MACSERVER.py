import socket
import threading
import os

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 1024

class Server:
      def __init__(self):
            self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.accept_connections()
    
      def accept_connections(self):

            #os.chdir(os.path.dirname(sys.executable))

            ip = socket.gethostbyname(socket.gethostname())
            port = 5002

            self.s.bind((ip,port))
            self.s.listen(100)

            print('Running on IP: '+ip)
            print('Running on port: '+str(port))

            while 1:
                c, addr = self.s.accept()
                print(c)
            
                threading.Thread(target=self.handle_client,args=(c,addr,)).start()

      def handle_client(self,c,addr):

            #ricevo il nome dell prossimo update
            data = c.recv(1024).decode('utf-8')
            filename = data
            
            if os.path.exists(data):
                  c.send("file-exist".encode('utf-8'))
                  c.shutdown(socket.SHUT_RDWR)
                  c.close()
            else:
                  for f in os.listdir():
                        if 'CrissAIO' in str(f):
                              filename = f
                  filesize = os.path.getsize(filename)
                  #se esiste invio indietro nome e file
                  c.send(f"{filename}{SEPARATOR}{filesize}".encode('utf-8'))

                  with open(filename, 'rb') as f:
                        while True:
                              bytes_read = f.read(BUFFER_SIZE)
                              if not bytes_read:
                                    break
                                    
                              try:
                                    c.sendall(bytes_read)
                              except:
                                    pass

                  c.shutdown(socket.SHUT_RDWR)
                  c.close()
                  """
                  print('Sending',data)
                  if data != '':
                        file = open(data,'rb')
                        data = file.read(1024)
                        while data:
                              c.send(data)
                              data = file.read(1024)

                        c.shutdown(socket.SHUT_RDWR)
                        c.close()
                
                  """
server = Server()
