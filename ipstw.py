from micropython import const
from machine import ADC,Pin,SoftI2C,PWM
from time import sleep
import neopixel
import sys
import struct
import neopixel
import framebuf
# MicroPython SSD1306 OLED driver, I2C and SPI interfaces
import time
currentBoard=""
if(sys.platform=="esp8266"):
  currentBoard="esp8266"
elif(sys.platform=="esp32"):
  currentBoard="esp32"
# register definitions
SET_CONTRAST        = const(0x81)
SET_ENTIRE_ON       = const(0xa4)
SET_NORM_INV        = const(0xa6)
SET_DISP            = const(0xae)
SET_MEM_ADDR        = const(0x20)
SET_COL_ADDR        = const(0x21)
SET_PAGE_ADDR       = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP       = const(0xa0)
SET_MUX_RATIO       = const(0xa8)
SET_COM_OUT_DIR     = const(0xc0)
SET_DISP_OFFSET     = const(0xd3)
SET_COM_PIN_CFG     = const(0xda)
SET_DISP_CLK_DIV    = const(0xd5)
SET_PRECHARGE       = const(0xd9)
SET_VCOM_DESEL      = const(0xdb)
SET_CHARGE_PUMP     = const(0x8d)
 
class SSD1306:
  def __init__(self, width, height, external_vcc):
    self.width = width
    self.height = height
    self.external_vcc = external_vcc
    self.pages = self.height // 8
    self.buffer = bytearray(self.pages * self.width)
    self.framebuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MVLSB)
    self.poweron()
    self.init_display()
  def init_display(self):
    for cmd in (
      SET_DISP | 0x00, # off
      # address setting
      SET_MEM_ADDR, 0x00, # horizontal
      # resolution and layout
      SET_DISP_START_LINE | 0x00,
      SET_SEG_REMAP | 0x01, # column addr 127 mapped to SEG0
      SET_MUX_RATIO, self.height - 1,
      SET_COM_OUT_DIR | 0x08, # scan from COM[N] to COM0
      SET_DISP_OFFSET, 0x00,
      SET_COM_PIN_CFG, 0x02 if self.height == 32 else 0x12,
      # timing and driving scheme
      SET_DISP_CLK_DIV, 0x80,
      SET_PRECHARGE, 0x22 if self.external_vcc else 0xf1,
      SET_VCOM_DESEL, 0x30, # 0.83*Vcc
      # display
      SET_CONTRAST, 0xff, # maximum
      SET_ENTIRE_ON, # output follows RAM contents
      SET_NORM_INV, # not inverted
      # charge pump
      SET_CHARGE_PUMP, 0x10 if self.external_vcc else 0x14,
      SET_DISP | 0x01): # on
      self.write_cmd(cmd)
    self.fill(0)
    self.show()
  def poweroff(self):
    self.write_cmd(SET_DISP | 0x00)
  def contrast(self, contrast):
    self.write_cmd(SET_CONTRAST)
    self.write_cmd(contrast)
  def invert(self, invert):
    self.write_cmd(SET_NORM_INV | (invert & 1))
  def show(self):
    x0 = 0
    x1 = self.width - 1
    if self.width == 64:
      # displays with width of 64 pixels are shifted by 32
      x0 += 32
      x1 += 32
    self.write_cmd(SET_COL_ADDR)
    self.write_cmd(x0)
    self.write_cmd(x1)
    self.write_cmd(SET_PAGE_ADDR)
    self.write_cmd(0)
    self.write_cmd(self.pages - 1)
    self.write_data(self.buffer)
  def fill(self, col):
    self.framebuf.fill(col)
  def pixel(self, x, y, col):
    self.framebuf.pixel(x, y, col)
  def scroll(self, dx, dy):
    self.framebuf.scroll(dx, dy)
  def text(self, string, x, y, col=1):
    self.framebuf.text(string, x, y, col)
  def hline(self, x, y, w, col):
    self.framebuf.hline(x, y, w, col)
  def vline(self, x, y, h, col):
    self.framebuf.vline(x, y, h, col)
  def line(self, x1, y1, x2, y2, col):
    self.framebuf.line(x1, y1, x2, y2, col)
  def rect(self, x, y, w, h, col):
    self.framebuf.rect(x, y, w, h, col)
  def fill_rect(self, x, y, w, h, col):
    self.framebuf.fill_rect(x, y, w, h, col)
  def blit(self, fbuf, x, y):
    self.framebuf.blit(fbuf, x, y)
    
class IPSTW(SSD1306):
  def __init__(self,i2c=SoftI2C(scl=Pin(22), sda=Pin(21), freq=1000000),address = const(0x48),width=128, height=64,addr=0x3c, external_vcc=False):
    self.addr = addr
    self.temp = bytearray(2)
    self.i2c = i2c
    self.con_ipstw = 0
    self.address = address
    self.np = neopixel.NeoPixel(Pin(12),255,timing=1)
    self.Svn=ADC(Pin(36)) #SVP
    self.Svn.atten(ADC.ATTN_11DB)
    self.valSW = Pin(0,Pin.IN,Pin.PULL_UP)
    self.led=Pin(18,Pin.OUT)
    self.np[0]= (0,0,0)
    self.np[1]= (0,0,0)
    self.np[2]= (0,0,0)
    self.np.write()
    print('IPSTW...Run')
    super().__init__(width, height, external_vcc)
  def map(self,value, istart, istop, ostart, ostop):
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))
  def begin(self):
    self.np[0]= (0,0,0)
    self.np[1]= (0,0,0)
    self.np[2]= (0,0,0)
    self.np.write()
    print('IPSTW...Run')
  def analog(self,port):
    val=ADC(Pin(port))
    val.atten(ADC.ATTN_11DB)
    return val.read()
  def pwm(self,port,duty):
      pwmpin =PWM(Pin(port))
      pwmpin.freq(500)
      pwmpin.duty(duty)
  def exti(self,port,irq_request):
      btn=Pin(port,Pin.IN,Pin.PULL_UP)
      btn.irq(trigger=Pin.IRQ_FALLING,handler=irq_request)
  def output(self,port,logic):
      pin = Pin(port,Pin.OUT)
      pin.value(logic)
  def input(self,port):
      val = Pin(port,Pin.IN,Pin.PULL_UP)
      return val.value()
  def sw1(self):
      return self.valSW.value()
  def OK(self):
    while self.sw1():
      self.fill(0)
      self.text("Press SW1",10,18)
      self.show()
      sleep(0.3)
      self.fill(0)
      self.show()
      sleep(0.3)
  def knob(self,ostart=0,ostop=4095):
    return self.map(self.Svn.read(),0,4095,ostart,ostop)
  def sled(self,n,color):
    self.np[n]= color
    self.np.write()
  def led(self,st):
    self.led.value(st)
  def sound(self,freq,time):
    #global buzzer
    if freq>=3000:
      freq=3000
    elif freq < 0:
      freq=0
    buzzer = PWM(Pin(25))
    buzzer.freq(freq)
    buzzer.duty(512)
    sleep(time)
    buzzer.deinit()

  def write_cmd(self, cmd):
    self.temp[0] = 0x80 # Co=1, D/C#=0
    self.temp[1] = cmd
    #IF SYS  :
    global currentBoard
    if currentBoard=="esp8266" or currentBoard=="esp32":
      self.i2c.writeto(self.addr, self.temp)
    elif currentBoard=="pyboard":
      self.i2c.send(self.temp,self.addr)
    #ELSE:
          
  def write_data(self, buf):
    self.temp[0] = self.addr << 1
    self.temp[1] = 0x40 # Co=0, D/C#=1

    global currentBoard
    if currentBoard=="esp8266" or currentBoard=="esp32":
      self.i2c.start()
      self.i2c.write(self.temp)
      self.i2c.write(buf)
      self.i2c.stop()
    elif currentBoard=="pyboard":
      #self.i2c.send(self.temp,self.addr)
      #self.i2c.send(buf,self.addr)
      self.i2c.mem_write(buf,self.addr,0x40)
  def poweron(self):
    pass
