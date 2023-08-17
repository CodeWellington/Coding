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
        desc = f"Router Model:          {self.model}\n" \
               f"Software:              {self.software}\n" \
               f"IP:                    {self.ip}"
        return desc

class Switch(Router): #Inheriting from previous class
    def get_des(self):
        desc = f"Switch Model:          {self.model}\n" \
               f"Software:              {self.software}\n" \
               f"IP:                    {self.ip}"
        return desc


rtr1 = Router("2021", "16.7.4", "10.10.10.10", "48")
sw1 = Switch("9300", "10.2.2", "20.20.20.20", "36")
print(rtr1.get_des())
print(sw1.get_des())
