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

class test_script(Script):
    some_field=0
    def awake(self,game):
        print("Hi :)")
    def post_update(self,game,delta):
        print("delta: ", delta)
        print("current ms: ", game.current_ms)

mod = Mod(
    "Mod",
    [],
    Menu(
        f.RectImage([0,0,320,222,0,0,0,0,0,320,222,245,245,245])
        (140,180), (50,20),
        f.RectImage([0,0,320,222,0,0,0,0,0,320,222,225,225,225])
    )
)