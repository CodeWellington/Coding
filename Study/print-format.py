#You can print with .format, f"" or with %s

#Here are some examples:

name = wellington maciel de oliveira

print("My name is {}".format(name))
>My name is wellington maciel de oliveira

print(f"My name is {name}")
>My name is wellington maciel de oliveira

print("My name is %s" %name)
>My name is wellington maciel de oliveira

#Print with spaces on left, right or middle

print(f"start{name:50}end")
>startwellington maciel de oliveira                      end

print(f"start{name:>50}end")
>start                     wellington maciel de oliveira end

print(f"start{name:^50}end")
>start          wellington maciel de oliveira            end


#Tip - use end="" to print loop in the same line

my_list = ["wellington ", "maciel ", "de ", "oliveira"]
for obj in my_list:
    print(obj, end="")

