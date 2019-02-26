from machine import I2C,Pin
import network
import ipstw
import time
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=1000000)
print (i2c.scan())

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi = wifi.scan() 

w=ipstw.IPSTW()
w.begin()

w.fill(0)
w.text("WiFi=%d " % len(wifi),0,0*8)
w.show()

if(len(wifi)>3):
  w.sound(1000,0.1)
  w.sound(1000,0.1)
  w.sled(0,(10,0,0))
  w.sled(1,(0,10,0))
  w.sled(2,(0,0,10))
  time.sleep(0.5)
else:
  w.sound(1000,1)
  
w.sled(0,(10,0,0))
w.sled(1,(0,10,0))
w.sled(2,(0,0,10))

def map(value, istart, istop, ostart, ostop):
  return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))
#w.OK()
while 1:
  valKnob=int(w.knob(0,255))
  w.led(w.sw1())
  if w.sw1()==0:
    w.sound(1000,0.1)
  if w.input(34):
    w.sound(1000,0.1)
  if not(w.input(35)):
    w.sound(1000,0.1)
  if not(w.input(33)):
    w.sound(1000,0.1)
  if not(w.input(32)):
    w.sound(1000,0.1)
  if not(w.input(26)):
    w.sound(1000,0.1)
  if not(w.input(5)):
    w.sound(1000,0.1)
  if not(w.input(19)):
    w.sound(1000,0.1)
  if not(w.input(23)):
    w.sound(1000,0.1)
  w.fill(0)
  w.text("KNOB=%d " % w.knob(),0,0*8)
  w.text("IO34=%d " % w.input(34),0,(1*8)+1)
  w.text("IO35=%d " % w.input(35),0,(2*8)+1)
  w.text("IO33=%d " % w.input(33),0,(3*8)+1)
  w.text("IO32=%d " % w.input(32),0,(4*8)+1)
  w.text("IO26=%d " % w.input(26),0,(5*8)+1)
  w.text("IO 5=%d " % w.input(5),0,(6*8)+1)
  w.text("IO19=%d " % w.input(19),0,(7*8)+1)
  w.text("IO23=%d " % w.input(23),60,(7*8)+1)
  w.show()
  w.sled(0,(valKnob,valKnob,valKnob))
  w.sled(1,(valKnob,valKnob,valKnob))
  w.sled(2,(valKnob,valKnob,valKnob))




