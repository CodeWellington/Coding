class Router:
    '''This is a class for router'''
    #Functions in class are called as methods
    def __init__(self, model, software, ip, ports):
        self.model = model
        self.software = software
        self.ip = ip
        self.ports = ports

rtr1 = Router("9300", "16.7.4", "10.10.10.10", "48")
print(rtr1.ports)
