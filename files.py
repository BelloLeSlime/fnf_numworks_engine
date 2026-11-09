class RectImage:
  def __init__(self,image):
    self.image=image
  def grey_scale(self):
    grey=[]
    for i in range(len(self.image)/7):
      color = min(((self.image[i*7+4]+self.image[i*7+5]+self.image[i*7+6])/3)+50,255)
      grey+=[self.image[i*7],self.image[i*7+1],self.image[i*7+2],self.image[i*7+3],color,color,color]
    return RectImage(grey)
class Chart:
  def __init__(self,chart,bpm=120,speed=0.2):
    self.chart=chart
    self.bpm=bpm
    self.speed=speed
  def fuse(self,chart):
    for i in range(18):
      self.chart[i]+=chart.chart[i]
    return self

left_arrow=RectImage([0,0,80,80,255,255,255,0,27,80,28,255,0,148,16,11,20,57,255,0,148,])
down_arrow=RectImage([0,0,80,80,255,255,255,27,0,30,80,0,150,255,12,45,59,21,0,150,255,])
up_arrow=RectImage([0,0,80,80,255,255,255,27,0,30,80,0,255,0,9,13,64,18,0,255,0])
right_arrow=RectImage([0,0,80,80,255,255,255,0,27,80,28,255,24,24,43,11,20,57,255,24,24])
