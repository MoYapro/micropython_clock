import machine
import network
import neopixel
import time
import ntptime


brightness = 8
pixels = 60
dataPin = 5
hourColor = (0,0,brightness)
minuteColor = (0,brightness,0)
secondColor = (brightness,0,0)
ssid = 'Heimnetz'
wifipassword = 'Superteam1700'

YEAR = 0
MONTH = 1
DAY = 2
HOUR = 3
MINUTE = 4
SECOND = 5


def initClock():
    ntptime.settime()
    print("Set local time to: %s" %str(time.localtime()))


def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        sta_if.active(True)
        sta_if.connect(ssid, wifipassword)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
    print('Connected to network: ' + str(sta_if.isconnected()))
    
def reset(leds):
    for i in range(pixels):
        leds[i] = (0,0,0)
    
def clear(leds):
  reset(leds)
  leds.write()
  print('clear')

def initLedStrip():
    leds = neopixel.NeoPixel(machine.Pin(dataPin), pixels)
    clear(leds)
    return leds

def printTime(t):
    print(str(t[DAY]) + '.' + str(t[MONTH]) + '.' + str(t[YEAR]))
    print(str(t[HOUR]) + ':' + str(t[MINUTE]) + ':' + str(t[SECOND]))
                   
def minutePos(minute):
    return minute - 1
                   
def secondPos(second):
    return second - 1
                   
def hourPos(hour, minute):
    hour = hour + 2 #due to timezone
    if hour > 12:
        hour = hour - 12
        hourPart = hour * 5
        minutePart = (minute//15)
    return round(hourPart + minutePart)

def plus(s1, s2):
    r = s1[0] + s2[0]
    g = s1[1] + s2[1]
    b = s1[2] + s2[2]
    return (r,g,b)
        

def showTimeOnLed(now):
    now = time.localtime()
    reset(leds)
    hourpos = hourPos(now[HOUR], now[MINUTE])
    minutepos = minutePos(now[MINUTE])
    secondpos = secondPos(now[SECOND])
    leds[hourpos] = plus(leds[hourpos], hourColor)
    leds[minutepos] = plus(leds[minutepos], minuteColor)
    leds[secondpos] = plus(leds[secondpos], secondColor)
    leds.write()
    
def runClock():
    last = 0
    while(True):
        now = time.localtime()
        if(last == now):
            continue
        #printTime(now)
        showTimeOnLed(now)
        last = now
        time.sleep_ms(10)
        



print('Starting...')
do_connect()
initClock()
leds = initLedStrip()
runClock()

clear()
print('end')