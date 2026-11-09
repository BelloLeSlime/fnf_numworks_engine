from kandinsky import *
class Vector2:
  def __init__(self,x,y):
    self.x=x
    self.y=y
class Drawer:
  def __init__(self):
    self.buffer=[]
    self.camera=Vector2(0,0)
    self.mc=None
  def fill_rect(self, x, y, w, h, color, camera=True):
    self.buffer.append(["rect",x,y,w,h,color,1 if camera else 0])
  def set_pixel(self, x, y, color, camera=True):
    self.buffer.append(["pixel",x,y,color,1 if camera else 0])
  def display_image(self,img,x,y,w,camera=True):
    self.buffer.append(["image",img,x,y,w,1 if camera else 0])
  def draw_string(self,text,x,y,camera=True):
    self.buffer.append(["text",text,x,y,1 if camera else 0])
  def move_camera(self,x,y,time):
    self.mc = [self.camera,Vector2(x,y),time,0]
  def update(self, delta):
    if self.mc:
      self.mc[3]+=delta
      if self.mc[3]>=self.mc[2]:
        self.mc[3]=self.mc[2]
      p=self.mc[3]/self.mc[2]
      e=p*p*(3-2*p)
      x1=self.mc[0].x
      self.camera.x=x1+(self.mc[1].x-x1)*e
      y1=self.mc[0].y
      self.camera.y=y1+(self.mc[1].y-y1)*e
      if self.mc[3]>=self.mc[2]:
        self.mc = None
  def draw(self):
    for el in self.buffer:
      if el[0]=="pixel":
        set_pixel(el[1]+self.camera.x*el[4],el[2]+self.camera.y*el[4],el[3])
      elif el[0]=="rect":
        fill_rect(int(el[1]+self.camera.x*el[6]),int(el[2]+self.camera.y*el[6]),int(el[3]),int(el[4]),el[5])
      elif el[0]=="text":
        draw_string(el[1],int(el[2]+self.camera.x*el[4]),int(el[3]+self.camera.y*el[4]))
      elif el[0]=="image":
        rects=el[1].image
        og_w=rects[2]
        coef_w=og_w/el[4]
        for i in range(int(len(rects)/7)):
          if i==0:
            continue
          fill_rect(int((rects[i*7]/coef_w)+el[2]-self.camera.x*el[5]),int((rects[i*7+1]/coef_w)+el[3]-self.camera.y*el[5]),int(max(rects[i*7+2]/coef_w,1)),int(max(rects[i*7+3]/coef_w,1)),color(rects[i*7+4],rects[i*7+5],rects[i*7+6]))
    self.buffer=[]