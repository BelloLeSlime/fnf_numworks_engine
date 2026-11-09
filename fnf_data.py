import files as f
class Mod:
  def __init__(self,name,songs,menu,script=None):
    self.name=name
    self.songs=songs
    self.menu=menu
    self.script=script
class Menu:
  def __init__(self,main_bg,ok_pos,title_pos,bg):
    self.main_bg=main_bg
    self.ok_pos=ok_pos
    self.title_pos=title_pos
    self.bg=bg
class Song:
  def __init__(self,name,stage,chart,player,opp,arrows,script=None,rvrs=False):
    self.name=name
    self.stage=stage
    self.chart=chart
    self.player=player
    self.opp=opp
    self.arrows=arrows
    self.script=script
    self.rvrs=rvrs
class Stage:
  def __init__(self,elmts):
    self.elmts=elmts
  def copy(self):
    return Stage(self.elmts)
class Char:
  def __init__(self,anim,color,icon):
    self.anim=anim
    self.color=color
    self.icon=icon
class Script:
  def awake(self,game):
    pass
  def pre_update(self,game,delta):
    pass
  def post_update(self,game,delta):
    pass
  def pre_refresh(self,game,delta):
    pass
  def post_refresh(self,game,delta):
    pass

gold=Char(
  {
    "idle":f.gold_idle,
    "left":f.gold_left,
    "down":f.gold_down,
    "up":f.gold_up,
    "right":f.gold_right,
  },
  (225,225,225),
  f.gold_icon
)

red=Char(
  {
    "idle":f.red_idle,
    "left":f.red_idle,
    "down":f.red_idle,
    "up":f.red_idle,
    "right":f.red_idle,
  },
  (255,75,75),
  f.red_icon
)

from random import *
from ion import *
class frst_script(Script):
  freeze=0
  uses=0
  typhlo_d=0
  snows=[]
  snow_max=25
  def awake(self,game):
    game.current_ms=-9100
    for i in range(self.snow_max):
      self.snows.append([randint(0,320),randint(0,222),randint(5,10),randint(5,10),randint(3,8),randint(4,9)])
  def post_update(self,game,delta):
    if game.current_ms>0:
      self.freeze+=delta
      if self.freeze>=40:
        self.freeze=40
        game.rel_score=-100
      if game.in_m.ikjp(KEY_OK) and self.uses<10:
        self.uses+=1
        self.freeze=max(self.freeze-18,0)
        self.typhlo_d=1
  def post_refresh(self,game,delta):
    game.drawer.fill_rect(4,44,12,102,(0,200,255))
    game.drawer.fill_rect(5,45,10,100,(0,100,200))
    game.drawer.fill_rect(5,145-self.freeze/40*100,10,self.freeze/40*100,(0,255,255))
    self.typhlo_d-=delta
    typhlo=game.stage.elmts[3]
    if self.typhlo_d>0 or -9100+5000<game.current_ms<-9100+7000:
      typhlo[3]="use"
    else:
      typhlo[3]="idle"
    if self.uses>9:
      typhlo[2]=(typhlo[2][0],min(typhlo[2][1]+delta*70,223),typhlo[2][2])
    while len(self.snows)<self.snow_max:
      if randint(0,1):
        x=randint(0,320)
        y=0
      else:
        x=320
        y=randint(0,222)
      self.snows.append([x,y,randint(5,10),randint(5,10),randint(3,8),randint(4,9)])
    for snow in self.snows:
      snow[0]-=snow[4]
      snow[1]+=snow[5]
      game.drawer.fill_rect(snow[0],snow[1],snow[2],snow[3],(247,247,247))
      if snow[0]+snow[2]<0 or snow[1]>222:
        self.snows.remove(snow)
    if game.current_ms%((1/(f.frostbite.bpm/2))*60000)<=100 and typhlo[3]=="idle":
      typhlo[2]=(randint(19,21),randint(-21,-20),92)
      game.stage.elmts[1][2]=(randint(-2,2),randint(202-75,203-75),80)
    else:
      typhlo[2]=(20,-20,92)
      game.stage.elmts[1][2]=(0,202-75,80)

mt_silver=Stage(
  [
    ["bg",f.mountain,(-100,-100,520)],
    ["player",gold,(0,202-75,80)],
    ["opp",red,(200,50,65)],
    ["anim",
      {"idle": f.typhlosion,"use":f.typhlosion_use},
      (20,-20,92),"idle"],
    ["sprite",
      f.RectImage([0,0,320,222,0,0,0,0,202,320,20,0,0,0,0,0,320,20,0,0,0]),
      (0,0,320)]
  ]
)

arrows_default=[f.left_arrow,f.down_arrow,f.up_arrow,f.right_arrow]

frostbite=Song(
  "Frostbite",
  mt_silver,
  f.frostbite,
  gold, red,
  arrows_default,
  frst_script(), True
)

mod=Mod(
  "Friday Night Funkin'\nHypno's Lullaby",
  [frostbite],
  Menu(
  f.RectImage([0,0,320,222,225,225,225,0,0,320,222,225,225,225]),
  (140,180), (50,20),
  f.RectImage([0,0,320,222,225,225,225,0,0,320,222,225,225,225])
  )
)