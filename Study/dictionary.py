Dic_name.get("key")  #It will return None if the key doesn't exist

Dic_name.get("key", "another value")  #Another value will replace the None return if the key doesn't exist

New_dic = dic_name.copy #It will copy the dic_name -
# Note that if you just assign the value it will point to the same memory value and caution must be taken if the traditional method is used.

Dic_name.update(new_dic) # It will overwrite the values that have the same key

for k in network_dict:   # It will return only the key
    print(k)
for v in network_dict.values():  # It will return only the values
    print(v)
for k, v in network_dict.items():  # It will return both
    print(k,v)


#The second argument allows to specify which value should correspond to key
model = london.setdefault('model', 'Cisco3580')

d_keys = ['hostname', 'location', 'vendor', 'model', 'ios', 'ip']

r1 = dict.fromkeys(d_keys)




