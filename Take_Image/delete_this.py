import time

def capture_image(ct, cs, user_input, bl=False):
    count_t = ct
    count_s = cs
        
    if bl==False:
        if user_input=="t":
            print(count_t)

        elif user_input=="s":
            print(count_s)
    else:
        if user_input=="t":
            print(count_t)
            count_t += 1

        elif user_input=="s":
            print(count_s)
            count_s += 1

    return count_t, count_s


# ***
prev_user_input = "t"

count_t = 0
count_s = 0

try:
    while (True): 
        user_input = input("Take Image?")

        if user_input == "n":
            break
        elif user_input=="":
            user_input = prev_user_input
        
        print("Lighting Call")
        _, _= capture_image(count_t,count_s,user_input=user_input)

        print("BL Call")
        count_t, count_s  = capture_image(count_t, count_s, user_input=user_input,bl=True)
        
        prev_user_input = user_input

except Exception as e:
    print("{} \nCapture Ended With Raised Exception".format(e))
# https://www.geeksforgeeks.org/finally-keyword-in-python/