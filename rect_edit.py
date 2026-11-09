from kandinsky import *
from ion import *
from time import *
from files import *
from input_manager import *
from drawer import *

cursor = Vector2(160,111)

class Rect:
  def __init__(self,x,y,w,h,color):
    self.x=x
    self.y=y
    self.w=w
    self.h=h
    self.color=color
  def copy(self):
    return Rect(self.x,self.y,self.w,self.h,self.color)

class RectImageEdit:
  def __init__(self):
    self.data = []
  def add_rect(self,rect):
    if rect.w==0 or rect.h==0:
      return
    if rect.w<0:
      rect.w*=-1
      rect.x-=rect.w
    if rect.h<0:
      rect.h*=-1
      rect.y-=rect.h
    self.data.append(rect)
  def rm_rect(self,rect):
    self.data.remove(rect)
  def get_pixel(self,x,y):
    rect=self.get_rect(x,y)
    if rect:
      return rect.color
    else:
      return None
  def get_rect(self,x,y):
    valid_rect=None
    for rect in self.data:
      if (rect.x<=x<rect.x+rect.w) and (rect.y<=y<rect.y+rect.h):
        valid_rect=rect
    return valid_rect
  def get_idx(self,wanted_rect):
    for i,rect in enumerate(self.data):
      if rect==wanted_rect:
        return i
    return None
  def rearange(self,sign,idx):
    try:
      rect1=self.data[idx]
      rect2=self.data[idx+sign]
      self.data[idx]=rect2
      self.data[idx+sign]=rect1
    except IndexError:
      return
  def move_extrem(self,sign,idx):
    if sign==1:
      r=None
      for i,rect in enumerate(self.data):
        if i<idx:
          continue
        elif i==idx:
          r=rect
          try:
            self.data[i]=self.data[i+1]
          except IndexError:
            continue
        else:
          try:
            self.data[i]=self.data[i+1]
          except IndexError:
            self.data[i]=r
    else:
      r=None
      for i,rect in enumerate(self.data):
        if i<=idx:
          if r==None:
            r=rect
            self.data[i]=self.data[idx]
          else:
            self.data[i]=r
            r=rect
  def export(self):
    global running
    data=[]
    for rect in self.data:
      data.append(rect.x)
      data.append(rect.y)
      data.append(rect.w)
      data.append(rect.h)
      data.append(rect.color[0])
      data.append(rect.color[1])
      data.append(rect.color[2])
    data_str=str(data)
    line=""
    for c in data_str:
      if c not in " ":
        line+=c
      if len(line)==144:
        print(line)
        line=""
    print(line)
    running=False
def update_pixel(x,y):
  col=image.get_pixel(x,y)
  drawer.set_pixel(x,y,background_color if not col else col)
def refresh():
  drawer.fill_rect(0,0,320,222,background_color)
  for rect in image.data:
    drawer.fill_rect(rect.x,rect.y,rect.w,rect.h,rect.color)
def settings():
  in_settings=True
  while in_settings:
    print("0. Back")
    print("1. Change Background Color")
    print("2. Change Cursor Color")
    choice=int(input("> "))
    if choice==0:
      in_settings=False
    elif choice==1:
      global background_color
      r = int(input("r: > "))
      g = int(input("g: > "))
      b = int(input("b: > "))
      background_color=(r,g,b)
    elif choice==2:
      global cursor_color
      r = int(input("r: > "))
      g = int(input("g: > "))
      b = int(input("b: > "))
      cursor_color=(r,g,b)

running=True
drawer=Drawer()
image=RectImageEdit()
in_m=Input()
fill_rect(0,0,320,222,(225,225,225))
drawing_rect=None
selected_rect=None
cursor_offset=None
cursor_color=color(0,0,0)
selected_corner=0
og_rect=None
og_cursor=None
selected_color=(0,0,0)
background_color=(225,225,225)
while running:
  t=monotonic()
  in_m.process()
  if in_m.ikjp(KEY_POWER):
    rect=image.get_rect(cursor.x,cursor.y)
    if rect:
      selected_rect=rect
      cursor_offset=Vector2(cursor.x-selected_rect.x,cursor.y-selected_rect.y)
  if in_m.ikjr(KEY_POWER):
    selected_rect=None
  if in_m.ikjp(KEY_SQUARE):
    rect=image.get_rect(cursor.x,cursor.y)
    if rect:
      og_rect=rect.copy()
      og_cursor=Vector2(cursor.x,cursor.y)
      selected_rect=rect
      cursor_offset=Vector2(cursor.x-selected_rect.x,cursor.y-selected_rect.y)
      if cursor.x < (2*rect.x+rect.w)/2:
        selected_corner=0 if cursor.y < (2*rect.y+rect.h)/2 else 2
      else:
        selected_corner=1 if cursor.y<(2*rect.y+rect.h)/2 else 3
  if in_m.ikjr(KEY_SQUARE):
    selected_rect=None
  if keydown(KEY_DOWN) or keydown(KEY_UP) or keydown(KEY_LEFT) or keydown(KEY_RIGHT):
    if not in_m.ikp(KEY_SHIFT):
      update_pixel(cursor.x,cursor.y)
      if keydown(KEY_DOWN):
        cursor.y=min(cursor.y+(1 if not keydown(KEY_ALPHA) else 5),222)
      if keydown(KEY_UP):
        cursor.y=max(cursor.y-(1 if not keydown(KEY_ALPHA) else 5),0)
      if keydown(KEY_LEFT):
        cursor.x=max(cursor.x-(1 if not keydown(KEY_ALPHA) else 5),0)
      if keydown(KEY_RIGHT):
        cursor.x=min(cursor.x+(1 if not keydown(KEY_ALPHA) else 5),320)
    else:
      update_pixel(cursor.x,cursor.y)
      if in_m.ikjp(KEY_DOWN):
        cursor.y=min(cursor.y + (1 if not keydown(KEY_ALPHA) else 5),222)
      if in_m.ikjp(KEY_UP):
        cursor.y=max(cursor.y-(1 if not keydown(KEY_ALPHA) else 5),0)
      if in_m.ikjp(KEY_LEFT):
        cursor.x=max(cursor.x-(1 if not keydown(KEY_ALPHA) else 5),0)
      if in_m.ikjp(KEY_RIGHT):
        cursor.x=min(cursor.x+(1 if not keydown(KEY_ALPHA) else 5),320)
    if keydown(KEY_POWER) and selected_rect:
      selected_rect.x=cursor.x-cursor_offset.x
      selected_rect.y=cursor.y-cursor_offset.y
      refresh()
    if keydown(KEY_SQUARE) and selected_rect:
      if selected_corner==0:
        selected_rect.x=cursor.x-cursor_offset.x
        selected_rect.w=og_rect.w+(og_rect.x-selected_rect.x)
        selected_rect.y=cursor.y-cursor_offset.y
        selected_rect.h=og_rect.h+(og_rect.y-selected_rect.y)
      elif selected_corner==1:
        selected_rect.w=og_rect.w+(cursor.x-og_cursor.x)
        selected_rect.y=cursor.y-cursor_offset.y
        selected_rect.h=og_rect.h+(og_rect.y-selected_rect.y)
      elif selected_corner==2:
        selected_rect.x=cursor.x-cursor_offset.x
        selected_rect.w=og_rect.w+(og_rect.x-selected_rect.x)
        selected_rect.h=og_rect.h+(cursor.y-og_cursor.y)
      else:
        selected_rect.w=og_rect.w+(cursor.x-og_cursor.x)
        selected_rect.h=og_rect.h+(cursor.y-og_cursor.y)
      refresh()
  drawer.set_pixel(cursor.x,cursor.y,cursor_color)
  if in_m.ikjp(KEY_OK):
    drawing_rect=Rect(cursor.x,cursor.y,0,0,selected_color)
  elif in_m.ikp(KEY_OK):
    refresh()
    drawing_rect.w=cursor.x - drawing_rect.x
    drawing_rect.h=cursor.y - drawing_rect.y
    drawer.fill_rect(drawing_rect.x,drawing_rect.y,drawing_rect.w,drawing_rect.h,selected_color)
  elif in_m.ikjr(KEY_OK):
    image.add_rect(drawing_rect)
    drawing_rect=None
    refresh()
  if in_m.ikjp(KEY_BACKSPACE):
    rect=image.get_rect(cursor.x,cursor.y)
    if rect:
      image.rm_rect(rect)
      refresh()
  if in_m.ikjp(KEY_COMMA):
    rect=image.get_rect(cursor.x,cursor.y)
    if rect:
      rect.color=selected_color
      refresh()
  if in_m.ikjp(KEY_EXE):
    print("0. Cancel")
    print("1. Export rects")
    choice=int(input("> "))
    if choice==0:
      refresh()
    if choice==1:
      image.export()
  if in_m.ikjp(KEY_ANS):
    r=int(input("r: "))
    g=int(input("g: "))
    b=int(input("b: "))
    selected_color=(r,g,b)
    refresh()
  if in_m.ikjp(KEY_XNT):
    vars=globals()
    images=[]
    i=1
    print("0. Cancel")
    for var in vars:
      if isinstance(vars[var],RectImage):
        print(str(i)+". "+var)
        i+=1
        images.append(vars[var].image)
    idx = int(input(">"))
    if idx!=0:
      img = images[idx-1]
      rects=[]
      for i in range(len(img)/7):
        x=img[i*7]
        y=img[i*7+1]
        w=img[i*7+2]
        h=img[i*7+3]
        r=img[i*7+4]
        g=img[i*7+5]
        b=img[i*7+6]
        rects.append(Rect(x,y,w,h,(r,g,b)))
      image.data=rects
    refresh()
  if in_m.ikjp(KEY_TOOLBOX):
    settings()
    refresh()
  if in_m.ikjp(KEY_SQRT):
    col=image.get_pixel(cursor.x,cursor.y)
    if col:
      selected_color=col
  if in_m.ikjp(KEY_PLUS):
    rect=image.get_rect(cursor.x,cursor.y)
    if rect:
      idx=image.get_idx(rect)
      image.rearange(1,idx)
      refresh()
  if in_m.ikjp(KEY_MINUS):
    rect=image.get_rect(cursor.x,cursor.y)
    if rect:
      idx=image.get_idx(rect)
      image.rearange(-1,idx)
      refresh()
  if in_m.ikjp(KEY_MULTIPLICATION):
    rect=image.get_rect(cursor.x,cursor.y)
    if rect:
      idx=image.get_idx(rect)
      image.move_extrem(1,idx)
      refresh()
  if in_m.ikjp(KEY_DIVISION):
    rect=image.get_rect(cursor.x,cursor.y)
    if rect:
      idx=image.get_idx(rect)
      image.move_extrem(-1,idx)
      refresh()
  if in_m.ikjp(KEY_LN):
    for rect in image.data:
      rect.y-=1
    refresh()
  if in_m.ikjp(KEY_COSINE):
    for rect in image.data:
      rect.y+=1
    refresh()
  if in_m.ikjp(KEY_SINE):
    for rect in image.data:
      rect.x-=1
    refresh()
  if in_m.ikjp(KEY_TANGENT):
    for rect in image.data:
      rect.x+=1
    refresh()
  drawer.draw()
  delta = monotonic()-t
  if delta < 1/15:
    sleep(1/15-delta)