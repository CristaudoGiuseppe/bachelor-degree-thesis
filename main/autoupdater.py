import socket, os, sys, subprocess, time, platform, utility

BUFFER_SIZE = 1024
SEPARATOR = "<SEPARATOR>"

def open_file(filename):
    if sys.platform == "win32":
            os.startfile(filename)
    else:
            opener ="open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])


class Client:


      def __init__(self):
            self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.connect_to_server()

      def connect_to_server(self):
            self.target_ip = '95.179.183.203'

            if 'Windows' in platform.system():
                  self.target_port = 5001
            else:
                  self.target_port = 5002

            self.s.connect((self.target_ip,self.target_port))

            self.main()

      def reconnect(self):
            self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.s.connect((self.target_ip,int(self.target_port)))

      def main(self):

            utility.printLogo()
            print(utility.bcolors.WARNING + '   Checking for updates..' + utility.bcolors.ENDC)

            version = utility.getVersion()

            if 'Windows' in platform.system():
                  self.file_name = 'CrissAIO ' + version + '.exe'
            else:
                  self.file_name = 'CrissAIO ' + str(version).replace('.','_' ) + '.zip'

            time.sleep(2)
            
            try:
                  self.s.send(self.file_name.encode('utf-8'))

                  confirmation = self.s.recv(1024).decode('utf-8')
            except:
                  utility.printLogo()
                  print(utility.bcolors.FAIL + '   Something went wrong..' + utility.bcolors.ENDC)
                  self.s.close()
                  time.sleep(100)
                  sys.exit()
            
            if confirmation == "file-exist":
                  utility.printLogo()
                  print(utility.bcolors.OKGREEN + '   Everything is up to date..' + utility.bcolors.ENDC)

                  time.sleep(2)
                  
                  #self.s.shutdown(socket.SHUT_RDWR)
                  self.s.close()

            else:
                  print(confirmation)
                  filename, filesize = confirmation.split(SEPARATOR)
                  filesize = int(filesize)
                  
                  utility.printLogo()
                  print(utility.bcolors.OKGREEN + '   Downloading new version..' + utility.bcolors.ENDC)

                  with open(filename, "wb") as f:

                        while True:
                              
                              bytes_read = self.s.recv(BUFFER_SIZE)
                              if not bytes_read:    
                                    break
      
                              f.write(bytes_read)
                  
                  utility.printLogo()
                  print(utility.bcolors.OKGREEN + '   '+str(filename)+' successfully downloaded.' + utility.bcolors.ENDC+'\n')
                  
                  try:
                        open_file(os.path.abspath(filename))
                  except:
                        pass
                  
                  sys.exit()
                  #self.s.shutdown(socket.SHUT_RDWR)
                  self.s.close()