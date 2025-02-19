import re

def config_block(file, regex):
  ##Find the block of code based on regex - Ex. ap profile <name> [ap\sprofile\s.*]
 output = {}
 temp = ""

 for line in file:
  if temp and line.startswith(" "): #Config block starts with space
   output[temp].append(line)
  elif temp and not line.startswith(" "):
   temp = "" #When the block finishes

  try:
   temp = re.search(regex, line).group(0)
   output[temp] = []
  except:
   continue
 return output

if __name__ == "__main__":

 ##Read a config file##
 with open('config.txt', 'r', newline='') as file:
  lines = file.readlines()
  lines = [line.rstrip('\n\r') for line in lines]
 
 ##Example
 profi_regex = 'ap\sprofile\s.*'
 profi = config_block(lines, profi_regex)

 # Test
