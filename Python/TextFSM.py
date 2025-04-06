import textfsm
import json

raw_output = '''Interface    Status    Protocol
Gig0/1       up        up
Gig0/2       down      down
Gig0/3       up        up'''

template_file = open('basic.textfsm')

textfsm_parser = textfsm.TextFSM(template_file)
parsed_data = textfsm_parser.ParseText(raw_output)

parsed_output = [dict(zip(textfsm_parser.header, row)) for row in parsed_data]
print(json.dumps(parsed_output, indent=4))

template_file.close()
