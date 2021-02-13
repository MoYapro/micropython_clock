import machine
import network
import neopixel
import time
import ntptime


brightness = 12
timeBrightness = brightness//12
pixels = 60
dataPin = 5
hourColor = (0,0,brightness)
minuteColor = (0,brightness,0)
secondColor = (brightness,0,0)
timerColor = (timeBrightness,0,timeBrightness)
secondsInYear = 60 * 60 * 24 * 365
secondsInMonth = 60 * 60 * 24 * 30
secondsInDay = 60 * 60 * 24
secondsInHour = 60 * 60
secondsInMinute = 60
ssid = 'Heimnetz'
wifipassword = 'Superteam1700'
timers = []

YEAR = 0
MONTH = 1
DAY = 2
HOUR = 3
MINUTE = 4
SECOND = 5
MILLISECOND = 6


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
        

def updateClockTime(now):
    reset(leds)
    hourpos = hourPos(now[HOUR], now[MINUTE])
    minutepos = minutePos(now[MINUTE])
    secondpos = secondPos(now[SECOND])
    leds[hourpos] = plus(leds[hourpos], hourColor)
    leds[minutepos] = plus(leds[minutepos], minuteColor)
    leds[secondpos] = plus(leds[secondpos], secondColor)
    
    
def plusMinutes(time, addMinutes):
    seconds = time[SECOND]
    minutesSum = (time[MINUTE] + addMinutes)
    minutes = minutesSum % 60
    if minutesSum >= 60:
        hoursSum = time[HOUR] + minutesSum//60    
    else:
        hoursSum = time[HOUR]
    hours = hoursSum % 24
    if hoursSum >= 24:
        daysSum = time[DAY] + hoursSum//24
    else:
        daysSum = time[DAY]
    days = daysSum
    return (time[YEAR], time[MONTH], days, hours, minutes, seconds)

def isBefore(time, referenceTime):
    return time[YEAR] <= referenceTime[YEAR] and time[MONTH] <= referenceTime[MONTH] and time[DAY] <= referenceTime[DAY] and time[HOUR] <= referenceTime[HOUR] and time[MINUTE] <= referenceTime[MINUTE] and time[SECOND] <= referenceTime[SECOND]

def howLongUntilInSeconds(time, referenceTime):
    yearDifference = referenceTime[YEAR] - time[YEAR] 
    monthDifference = referenceTime[MONTH] - time[MONTH]
    dayDifference = referenceTime[DAY] - time[DAY]
    hourDifference = referenceTime[HOUR] - time[HOUR]
    minuteDifference = referenceTime[MINUTE] - time[MINUTE]
    secondDifference = referenceTime[SECOND] - time[SECOND]
    return yearDifference * secondsInYear + monthDifference * secondsInMonth + dayDifference * secondsInDay + hourDifference * secondsInHour + minuteDifference * secondsInMinute + secondDifference
    
def appendMinuteRange(timer, now, activeRanges):
    if timer[HOUR] == now[HOUR]:
            activeRanges.append(range(now[MINUTE], timer[MINUTE]))
    if timer[HOUR] > now[HOUR]:
        activeRanges.append(range(now[MINUTE], 60))
        activeRanges.append(range(0, timer[MINUTE]))

def appendSecondRange(timer, now, activeRanges):
    if timer[MINUTE] == now[MINUTE]:
            activeRanges.append(range(now[SECOND], timer[SECOND]))
    if timer[MINUTE] > now[MINUTE]:
        activeRanges.append(range(now[SECOND], 60))
        activeRanges.append(range(0, timer[SECOND]))
    
def updateTimers(timers, now):
    activeRanges = []
    for timer in timers:
        if isBefore(timer, now):
            print('remove done timer')
            timers.remove(timer)
            continue
        timerDuration = howLongUntilInSeconds(timer, now)
        
        print('update timer: ' + str(timer) + 'Timer will run for another ' + str(timerDuration) + ' seconds')
        if timerDuration <= 60:
            appendSecondRange(timer, now, activeRanges)
        else:
            appendMinuteRange(timer, now, activeRanges)
        
    for activeRange in activeRanges:
        for activePosition in activeRange:
            leds[activePosition] = plus(leds[activePosition], timerColor)
        
            
            
        
    
def setTimer(duration, now):
    timerEnd = plusMinutes(now, duration)
    timers.append(timerEnd)
    print('set timer for ' + str(duration) + ' minutes.')
    print('From '+ str(now))
    print('till ' + str(timerEnd))
    
    
    
def runClock():
    last = 0
    while(True):
        now = time.localtime()
        if(last == now):
            continue
        printTime(now)
        updateClockTime(now)
        updateTimers(timers, now)
        last = now
        leds.write()
        time.sleep_ms(10)
        


print('Starting...')
do_connect()
initClock()
leds = initLedStrip()
setTimer(1, time.localtime()) #for testing
runClock()
clear()
print('end')