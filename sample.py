'''import time
now = time.time()  ###For calculate seconds of video
future = now + 50
print(future)'''
import time
start_time = time.time()

print("--- %s seconds ---" % (time.time() - start_time))

i = 0

while (i < len(lis)):
    print(lis[i], end=" ")

    # Changing the value of
    # i inside the loop will
    # change it's value at the
    # time of checking condition
    i += 2