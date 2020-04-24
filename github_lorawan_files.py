import threading
import time
import subprocess
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
import datetime
from datetime import datetime
from datetime import timedelta
import os.path
# Import thte SSD1306 module.
import adafruit_ssd1306
# Import Adafruit TinyLoRa
from adafruit_tinylora.adafruit_tinylora import TTN, TinyLoRa

# Button A
btnA = DigitalInOut(board.D5)
btnA.direction = Direction.INPUT
btnA.pull = Pull.UP

# Button B
btnB = DigitalInOut(board.D6)
btnB.direction = Direction.INPUT
btnB.pull = Pull.UP

# Button C
btnC = DigitalInOut(board.D12)
btnC.direction = Direction.INPUT
btnC.pull = Pull.UP

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# 128x32 OLED Display
reset_pin = DigitalInOut(board.D4)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)
# Clear the display.
display.fill(0)
display.show()
width = display.width
height = display.height

# TinyLoRa Configuration
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = DigitalInOut(board.CE1)
irq = DigitalInOut(board.D22)
rst = DigitalInOut(board.D25)

# TTN Device Address, 4 Bytes, MSB
devaddr = bytearray([0x26, 0x02, 0x17, 0x50])
#devaddr = bytearray([0x26, 0x02, 0x1A, 0x60])
# TTN Network Key, 16 Bytes, MSB
nwkey = bytearray([0xA2, 0xB6, 0x4D, 0xD0, 0xCa, 0xC1, 0xE9, 0x6B, 0xB9, 0x38, 0x27, 0x11, 0x19, 0xE6, 0x17, 0xA4])
#nwkey = bytearray([0x1F, 0xBA, 0xB0, 0xB9, 0x26, 0xE4, 0x19, 0x5E,
#                   0xC5, 0x33, 0xFE, 0x67, 0x84, 0x42, 0x3C, 0x57])
# TTN Application Key, 16 Bytes, MSB
app = bytearray([0x02, 0xF7, 0x83, 0x74, 0xAB, 0xDA, 0x8F, 0xE3, 0xF0, 0x73, 0xB0, 0xB5, 0x1E, 0x7E, 0x49, 0x09])
#app = bytearray([0x5E, 0xD7, 0xC1, 0x35, 0xA0, 0x5E, 0x65, 0xA8,
#                 0x59, 0x9A, 0x2C, 0xB1, 0xF5, 0xDB, 0xB6, 0x98])
# Initialize ThingsNetwork configuration
ttn_config = TTN(devaddr, nwkey, app, country='US')
# Initialize lora object
lora = TinyLoRa(spi, cs, irq, rst, ttn_config)
# 2b array to store sensor data
data_pkt = bytearray(2)
# time to delay periodic packet sends (in seconds)
data_pkt_delay = 5.0


def send_pi_data_periodic():
    threading.Timer(data_pkt_delay, send_pi_data_periodic).start()
    print("Sending periodic data...")
    send_pi_data(CPU)
    print('CPU:', CPU)

def send_pi_data(data):
    # Encode float as int
    data = int(data * 100)
    # Encode payload as bytes
    data_pkt[0] = (data >> 8) & 0xff
    data_pkt[1] = data & 0xff
    # Send data packet
    lora.send_data(data_pkt, len(data_pkt), lora.frame_counter)
    lora.frame_counter += 1
    display.fill(0)
    display.text('Sent Data to TTN!', 15, 15, 1)
    print('Data sent!')
    display.show()
    time.sleep(0.5)

def send_default_data(num_pedestrians, num_bicyclists):
    #bytearray of length
    # Encode float as int

    payload = bytearray([0x07, 0x65, 0xFF, 0xFF, 0x08, 0x65, 0xFF, 0xFF])
    #num_pedestrians=100*num_pedestrians
    low_num_pedestrian=num_pedestrians & 0xFF
    payload[3]=low_num_pedestrian
    high_num_pedestrian=(num_pedestrians >> 8) & 0xFF
    payload[2]=high_num_pedestrian
    #num_bicyclists=100*num_bicyclists
    low_num_bicyclists=num_bicyclists & 0xFF
    payload[7]=low_num_bicyclists
    high_num_bicyclists=(num_bicyclists >> 8) & 0xFF
    payload[6]=high_num_bicyclists
    # Send data packet
    lora.send_data(payload, len(payload), lora.frame_counter)
    lora.frame_counter += 1
    display.fill(0)
    display.text('Sent Data to CAY!', 15, 15, 1)
    print('Data sent!')
    display.show()
    time.sleep(0.5)


def send_test_data():
    #bytearray of length
    # Encode float as int
    payload = bytearray([0x03, 0x67, 0x01, 0x10, 0x05, 0x67, 0x00, 0xFF])
    # Send data packet
    lora.send_data(payload, len(payload), lora.frame_counter)
    lora.frame_counter += 1
    display.fill(0)
    display.text('Sent Data to CAY!', 15, 15, 1)
    print('Data sent!')
    display.show()
    time.sleep(0.5)

#send_default_data(100,213)
#if you're running the LoRa separately comment out the next two lines of code
datapedestriantest=(subprocess.check_output("grep 'person' results.txt | cut -f1 -d'.'", shell=True)).splitlines()
databicyclisttest=(subprocess.check_output("grep 'bicycle' results.txt | cut -f1 -d'.'", shell=True)).splitlines()
#datapedestriantest=int(subprocess.check_output("grep 'person' results.txt | wc -l", shell=True))
#databicyclisttest=int(subprocess.check_output("grep 'bicycle' results.txt | wc -l", shell=True))
grepdata=datetime.min
while True:
    packet = None
    # draw a box to clear the image
    display.fill(0)
    display.text('RasPi LoRaWAN', 35, 0, 1)
    
    # read the raspberry pi cpu load
    cmd = "top -bn1 | grep load | awk '{printf \"%.1f\", $(NF-2)}'"
    CPU = subprocess.check_output(cmd, shell = True )
    CPU = float(CPU)
    currenttime=datetime.now() - grepdata
    if currenttime.total_seconds() >= (60*54.2):
        #if you're running the LoRa separately comment out the next line of code
        #calls the OpenCV function
        opencvupload=os.system("LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1 python3 main2.py --images images")
        if os.path.isfile("results.txt"):
            #if you're demoing the LoRa separately comment out this next line of code and uncomment the line below it
            #searches for the word person in the text file, cuts to the digit number  
            datapedestriantest=(subprocess.check_output("grep 'person' results.txt | cut -f1 -d'.'", shell=True)).splitlines()
            #datapedestriantest=(subprocess.check_output("grep 'person' results.txt | wc -l", shell=True))
            #if you're demoing the LoRa separately -- comment this section out 
            pedestriantotal=0
            for numpedestriancount in datapedestriantest:
                print(numpedestriancount)
                #turn numpedestriancount from a string to an integer      
                pedestriancountarray=int(numpedestriancount)
                #increments pedestriantotal 
                pedestriantotal=pedestriancountarray+pedestriantotal
            #prints out the total number of pedestrians counted in that text file
            print(pedestriantotal)
            #if you're demoing the LoRa separately comment out this next line of code and uncomment the line below it
            #searches for the word bicycle in the text file, cuts to the digit number
            databicyclisttest=(subprocess.check_output("grep 'bicycle' results.txt | cut -f1 -d'.'", shell=True)).splitlines()
            #databicyclisttest=(subprocess.check_output("grep 'bicycle' results.txt | wc -l", shell=True))
            #if you're demo the LoRa separately -- comment this section out
            bicyclisttotal=0
            for numbicyclisttotal in databicyclisttest:
                #turn numbicyclisttotal from a string to an integer
                bicyclistcountarray=int(numbicyclisttotal)
                #increments bicyclisttotal
                bicyclisttotal=bicyclistcountarray+bicyclisttotal
            #prints out the total number of bicyclists counted in that text file 
            print(bicyclisttotal)
            #if you're demoing the LoRa separately -- comment this next line out and uncomment the code below it
            #sends the data of total number of pedestrians and bicyclist counted from the results.txt text file 
            send_default_data(pedestriantotal,bicyclisttotal)
            #send_default_data(datapedestriantest,databicyclisttest)
        else: 
            pedestriantotal=0
            bicyclisttotal=0
            send_default_data(pedestriantotal,bicyclisttotal)
           #if you're demoing the LoRa separately uncomment this set of code
           #datapedestriantest=0
           #databicyclisttest=0
           #send_default_data(datapedestriantest,databicyclisttest)
        deletefile=os.system("rm -f results.txt")
        if deletefile != 0:
            print ("File removal failed")
        grepdata=datetime.now()


#send the data 
#delete the file
    if not btnA.value:
        # Send Packet
        send_default_data(datapedestriantest,databicyclisttest) #send_pi_data(CPU)
    #if not btnB.value:
        # Display CPU Load
    #    display.fill(0)
     #   display.text('CPU Load %', 45, 0, 1)
      #  display.text(str(CPU), 60, 15, 1)
       # display.show()
       # time.sleep(0.1)
   # if not btnC.value:
    #    display.fill(0)
    #    display.text('* Periodic Mode *', 15, 0, 1)
    #    display.show()
    #    time.sleep(0.5)
    #    send_pi_data_periodic()


    display.show()
    time.sleep(.1)

