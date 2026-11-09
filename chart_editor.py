from kandinsky import *
from ion import *
from time import *
from files import *
from input_manager import *
from drawer import *

class ChartEdit:
  def __init__(self,bpm):
    self.chart=[[],[],[],[],[],[],[],[],0,0,[],[],[],[],[],[],[],[]]
    self.bpm=bpm
    self.char_count=len(str(self.chart))
  def change_bpm(self,wanted_bpm):
    old_bpm=self.bpm
    self.bpm=wanted_bpm
    coef=wanted_bpm/old_bpm
    for note in self.chart:
      if note==0:
        continue
      for i,ms in enumerate(note):
        note[i]=ms/coef
  def get_mspb(self):
    return (1/self.bpm)*60000
  def add_note(self, ms, note):
    self.chart[note].append(int(ms))
    self.char_count+=len(str(int(ms)))+1
  def rm_note(self,ms,note):
    self.chart[note].remove(int(ms))
    self.char_count-=len(str(int(ms)))+1
  def get_line(self, ms):
    notes=[]
    for i in range(17):
      if i in [8,9]:
        continue
      if int(ms) in self.chart[i]:
        notes.append(i)
    return notes
  def toggle_note(self,ms,note):
    if int(ms) in self.chart[note]:
      self.rm_note(ms,note)
    else:
      self.add_note(ms,note)
  def export(self):
    data_str=str(self.chart)
    line=""
    for i,c in enumerate(data_str):
      if not c in " ":
        line+=c
      if len(line)==144:
        print(line)
        line=""
    print(line)

running=True
drawer=Drawer()
in_m=Input()
chart_edit=ChartEdit(120)
delta=0
max_fps=20
selected_ms=0
selected_char=0
def draw_arrow(y,note):
  images=[left_arrow,down_arrow,up_arrow,right_arrow]
  if note in [0,1,2,3]:
    image=images[note]
    drawer.display_image(image,32*note,y,32)
  elif note in [4,5,6,7]:
    image=images[note-4]
    drawer.display_image(image,130+32*(note-4),y,32)
  elif note in [10,11,12,13]:
    image=images[note-10]
    col=(min(image.image[11]+50,255),min(image.image[12]+50,255),min(image.image[13]+50,255))
    drawer.fill_rect(8+32*(note-10),y-20,16,52,col)
  elif note in [14,15,16,17]:
    image=images[note-14]
    col=(min(image.image[11]+50,255),min(image.image[12]+50,255),min(image.image[13]+50,255))
    drawer.fill_rect(138+32*(note-14),y-20,16,52,col)

def refresh():
  drawer.fill_rect(0,0,320,222,color(225,225,225))
  drawer.fill_rect(0+129*selected_char,0,128,40,color(255,255,0))
  drawer.draw_string("Opponent",25,10)
  drawer.draw_string("Player",160,10)
  drawer.fill_rect(0,38,257,2,"black")
  drawer.fill_rect(127,0,3,222,"black")
  drawer.fill_rect(257,0,3,222,"black")
  drawer.fill_rect(0,108+16,257,1,"red")
  mspb=chart_edit.get_mspb()
  ms=selected_ms-mspb/4*2
  y=40
  for i in range(6):
    drawer.fill_rect(0,40+i*34,257,2 if ms%mspb<=2 else 1,"black")
    chart_data=chart_edit.get_line(ms)
    for note in chart_data:
      draw_arrow(y,note)
    ms+=mspb/4
    y+=34
  drawer.draw_string(str(int(selected_ms))+"ms",260,0)
  drawer.draw_string(str(chart_edit.bpm)+"BPM",260,20)
  drawer.draw_string(str(chart_edit.char_count)+"c"+("!"if chart_edit.char_count>144*7 else ""),260,40)

refresh()
while running:
  t=monotonic()  
  in_m.process()
  if in_m.ikjp(KEY_LEFT):
    chart_edit.toggle_note(selected_ms,0+4*selected_char)
    refresh()
  if in_m.ikjp(KEY_DOWN):
    chart_edit.toggle_note(selected_ms,1+4*selected_char)
    refresh()
  if in_m.ikjp(KEY_UP):
    chart_edit.toggle_note(selected_ms,2+4*selected_char)
    refresh()
  if in_m.ikjp(KEY_RIGHT):
    chart_edit.toggle_note(selected_ms,3+4*selected_char)
    refresh()
  if in_m.ikjp(KEY_ALPHA):
    selected_char=1 if selected_char==0 else 0
    refresh()
  if in_m.ikjp(KEY_SHIFT):
    selected_ms=max(0,selected_ms-chart_edit.get_mspb()/4)
    refresh()
  if in_m.ikjp(KEY_EXP):
    selected_ms+=chart_edit.get_mspb()/4
    refresh()
  if in_m.ikjp(KEY_EXE):
    chart_edit.export()
    running = False
  if in_m.ikjp(KEY_XNT):
    print("0. Cancel")
    i=0
    charts=[]
    for var in globals():
      if isinstance(globals()[var],Chart):
        i+=1
        print(str(i)+". "+var)
        charts.append(var)
    imprt=int(input("> "))
    if imprt!=0:
      chrt=globals()[charts[imprt-1]]
      chart_edit.chart=chrt.chart
      chart_edit.bpm=chrt.bpm
    refresh()
  if in_m.ikjp(KEY_IMAGINARY):
    chart_edit.toggle_note(selected_ms,10+4*selected_char)
    refresh()
  if in_m.ikjp(KEY_COMMA):
    chart_edit.toggle_note(selected_ms,11+4*selected_char)
    refresh()
  if in_m.ikjp(KEY_TOOLBOX):
    chart_edit.toggle_note(selected_ms,12+4*selected_char)
    refresh()
  if in_m.ikjp(KEY_POWER):
    chart_edit.toggle_note(selected_ms,13+4*selected_char)
    refresh()
  if in_m.ikjp(KEY_SQUARE):
    chart_edit.change_bpm(int(input("BPM: > ")))
    refresh()
  drawer.draw()
  delta=monotonic()-t
  if delta<1/max_fps:
    sleep(1/max_fps-delta)