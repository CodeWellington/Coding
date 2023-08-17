class Router:
    '''This is a class for router'''
    #Functions in class are named as methods
    def __init__(self, model, software, ip, ports):
        self.model = model
        self.software = software
        self.ip = ip
        self.ports = ports
    def get_des(self):
        '''Return the device information'''
        desc = f"Model:          {self.model}\n" \
               f"Software:       {self.software}\n" \
               f"IP:             {self.ip}"
        return desc


rtr1 = Router("9300", "16.7.4", "10.10.10.10", "48")
print(rtr1.get_des())
