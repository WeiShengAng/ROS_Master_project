
import serial
from time import sleep

s=serial.Serial("COM8",9600)
s.timeout = 1 #timeout means wait for 1 second, if no new data coming in then quit readline
try:
    while True:
        s.write('T'.encode()) # because what send is str, use encode to transform str to bytes
        sleep(0.1)
        #   read msg from arduino   # if execute this then fail to run 'D' cmd
        # msg = s.readline().decode() # because what receive is bytes, use decode to transform bytes to str
        # print(msg)
        # if msg == 'H':
        #     print("Done")
        # else:
        #     pass

except KeyboardInterrupt:
    exit()