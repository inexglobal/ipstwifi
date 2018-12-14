from machine import I2C,Pin
import ipstw
import time
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=1000000)
w=ipstw.IPSTW(i2c)
w.begin()
def map(value, istart, istop, ostart, ostop):
  return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))
while (72 not in i2c.scan()):
  print('check iKB-1')
  time.sleep(0.5)
w.OK()
while 1:
  val=w.analog(0)
  An7=w.analog(7)
  val32=w.analog(32)
  val33=w.analog(33)
  val34=w.analog(34)
  val35=w.analog(35)
  valKnob=w.knob(0,255)
  data=map(val,0,1023,-100,100)
  nondata=map(val,0,1023,100,-100)
  pos=map(An7,0,1023,0,180)
  w.fill(0)
  w.text("adc0=%d " % data,0,0*8)
  w.text("pos=%d " % pos,0,(1*8)+1)
  w.text("val32=%d " % val32,0,(2*8)+1)
  w.text("val33=%d " % val33,0,(3*8)+1)
  w.text("val34=%d " % val34,0,(4*8)+1)
  w.text("val35=%d " % val35,0,(5*8)+1)
  w.show()
  w.output(2,w.input(3))
  w.motor(1,data)
  w.motor(2,nondata) 
  w.servo(10,pos)
  w.servo(11,pos)
  w.servo(12,pos)
  w.servo(13,pos)
  w.servo(14,pos)
  w.servo(15,pos)
  w.led(w.sw1())
  if w.sw1()==0:
    w.sound(1000,0.1)



















