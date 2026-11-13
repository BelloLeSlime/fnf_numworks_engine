#v0.2
from time import *
from drawer import *
from input_manager import *
from fnf_data import *
class Game:
  r=True
  drawer=Drawer()
  in_m=Input()
  max_fps=12
  song_id=0
  stage={}
  delta=1/max_fps
  current_ms=0
  hit_notes={}
  p_pose=None
  opp_pose=None
  rel_score=0
  sel=0
  state=0
  og_t=0

  def refresh(self):
    if mod.script:
      mod.script.pre_refresh(self,self.delta)
    if self.state==0:
      self.drawer.display_image(mod.menu.main_bg,0,0,320)
      self.drawer.draw_string("Press OK",mod.menu.ok_pos[0],mod.menu.ok_pos[1])
      self.drawer.draw_string(mod.name,mod.menu.title_pos[0],mod.menu.title_pos[1])
    elif self.state==1:
      self.drawer.display_image(mod.menu.bg,0,0,320)
      self.drawer.draw_string((">" if self.sel == 0 else "")+"Freeplay",20,110+25+(-self.sel)*25)
      self.drawer.draw_string((">" if self.sel == 1 else "")+"Options",20,110+50+(-self.sel)*25)
      self.drawer.draw_string((">" if self.sel == 2 else "")+"Credits",20,110+75+(-self.sel)*25)
    elif self.state==2:
      self.drawer.display_image(mod.menu.bg,0,0,320)
      for i,song in enumerate(mod.songs):
        self.drawer.draw_string((">" if self.sel == i else "")+song.name,20,110+i*25+(-self.sel)*25)
        self.drawer.display_image(song.opp.icon,250,(110+i*25+(-self.sel)*25)-5,25)
    elif self.state==5:
      song = mod.songs[self.song_id]
      if song.script:
        song.script.pre_refresh(self,self.delta)
      for el in self.stage.elmts:
        if el[0]=="bg":
          self.drawer.display_image(el[1],el[2][0],el[2][1],el[2][2])
        elif el[0]=="player":
          if not self.p_pose:
            self.drawer.display_image(el[1].anim["idle"], el[2][0], el[2][1], el[2][2])
          else:
            pose = "left" if self.p_pose[0] == 4 else "down" if self.p_pose[0] == 5 else "up" if self.p_pose[0] == 6 else "right"
            self.drawer.display_image(el[1].anim[pose], el[2][0], el[2][1], el[2][2])
            if self.p_pose[1] > self.delta:
              self.p_pose = (self.p_pose[0], self.p_pose[1] - self.delta)
            else:
              self.p_pose = None
        elif el[0]=="opp":
          if not self.opp_pose:
            self.drawer.display_image(el[1].anim["idle"],el[2][0],el[2][1],el[2][2])
          else:
            pose="left" if self.opp_pose[0]==0 else "down" if self.opp_pose[0]==1 else "up" if self.opp_pose[0]==2 else "right"
            self.drawer.display_image(el[1].anim[pose],el[2][0],el[2][1],el[2][2])
            if self.opp_pose[1]>self.delta:
              self.opp_pose=(self.opp_pose[0],self.opp_pose[1]-self.delta)
            else:
              self.opp_pose=None
        elif el[0]=="anim":
          self.drawer.display_image(el[1][el[3]],el[2][0],el[2][1],el[2][2])
        elif el[0]=="sprite":
          self.drawer.display_image(el[1],el[2][0],el[2][1],el[2][2])
      for i in range(4):
        self.drawer.display_image(song.arrows[i].grey_scale(),200+25*i,25,24,camera=False)
      for i in range(4):
        self.drawer.display_image(song.arrows[i].grey_scale(),25*(i+1),25,24,camera=False)
      self.drawer.fill_rect(58,198,204,14,(0,0,0),camera=False)
      self.drawer.fill_rect(60,200,100+self.rel_score if song.rvrs else 100-self.rel_score,10,song.player.color if song.rvrs else song.opp.color,camera=False)
      self.drawer.display_image(song.player.icon if song.rvrs else song.opp.icon,118+self.rel_score if song.rvrs else 118-self.rel_score,180,40)
      self.drawer.fill_rect(160+self.rel_score if song.rvrs else 160-self.rel_score,200,100-self.rel_score if song.rvrs else 100+self.rel_score,10,song.opp.color if song.rvrs else song.player.color,camera=False)
      self.drawer.display_image(song.opp.icon if song.rvrs else song.player.icon,162+self.rel_score if song.rvrs else 162-self.rel_score,180,40)
      for note,note_mss in enumerate(song.chart.chart):
        if note_mss==0:
          continue
        for ms in note_mss:
          if self.current_ms-500<float(ms)<self.current_ms+2000:
            if str(ms) in self.hit_notes:
              if note in self.hit_notes[str(ms)]:
                continue
            dt=float(ms)-self.current_ms
            d=dt*song.chart.speed
            y=25+d
            if y<-24 or y>320:
              continue
            if note<4:
              self.drawer.display_image(song.arrows[note],(25 if not song.rvrs else 200)+note*25,y,24,camera=False)
            elif note<8:
              self.drawer.display_image(song.arrows[note-4],(25 if song.rvrs else 200)+25*(note-4),y,24,camera=False)
            elif note<14:
              self.drawer.fill_rect((25 if not song.rvrs else 200)+25*(note-10)+8,y-16,24-16,24+16,(min(song.arrows[note-10].image[11]+50,255),min(song.arrows[note-10].image[12]+50,255),min(song.arrows[note-10].image[13]+50,255)),camera=False)
            elif note<18:
              self.drawer.fill_rect((25 if song.rvrs else 200)+25*(note-14)+8,y-16,24-16,24+16,(min(song.arrows[note-14].image[11]+50,255),min(song.arrows[note-14].image[12]+50,255),min(song.arrows[note-14].image[13]+50,255)),camera=False)
      self.drawer.draw_string(str(int(1/self.delta))+"FPS",0,0)
      if song.script:
        song.script.post_refresh(self,self.delta)
    if mod.script:
      mod.script.post_refresh(self,self.delta)
  
  def __init__(self):
    if mod.script:
      mod.script.awake(self)
    self.refresh()
    while self.r:
      t=monotonic()
      self.in_m.process()
      if mod.script:
        mod.script.pre_update(self,self.delta)
      if self.state==0:
        if self.in_m.ikjp(KEY_OK):
          self.state=1
          self.refresh()
      elif self.state==1:
        if self.in_m.ikjp(KEY_BACKSPACE):
          self.state=0
          self.refresh()
        if self.in_m.ikjp(KEY_DOWN):
          self.sel=min(self.sel+1,2)
          self.refresh()
        if self.in_m.ikjp(KEY_UP):
          self.sel=max(self.sel-1,0)
          self.refresh()
        if self.in_m.ikjp(KEY_OK):
          self.state=self.sel+2
          self.sel=0
          self.refresh()
      elif self.state==2:
        if self.in_m.ikjp(KEY_BACKSPACE):
          self.state=1
          self.sel=0
          self.refresh()
        if self.in_m.ikjp(KEY_OK):
          self.state=5
          self.song_id=self.sel
          song=mod.songs[self.sel]
          self.rel_score=0
          self.stage=song.stage.copy()
          self.og_t=monotonic()
          if song.script:
            song.script.awake(self)
          self.refresh()
        if self.in_m.ikjp(KEY_DOWN):
          self.sel = min(self.sel+1,len(mod.songs)-1)
          self.refresh()
        if self.in_m.ikjp(KEY_UP):
          self.sel = max(self.sel-1,0)
          self.refresh()
      elif self.state==3:
        if self.in_m.ikjp(KEY_BACKSPACE):
          self.state=1
          self.sel=1
          self.refresh()
      elif self.state==4:
        if self.in_m.ikjp(KEY_BACKSPACE):
          self.state=1
          self.sel=2
          self.refresh()
      elif self.state==5:
        song=mod.songs[self.song_id]
        if song.script:
          song.script.pre_update(self,self.delta)
        for note,note_mss in enumerate(song.chart.chart):
          if note_mss==0:
            continue
          for ms in note_mss:
            if str(ms) in self.hit_notes and ms<self.current_ms-1000:
              del self.hit_notes[str(ms)]
            if self.current_ms-500<ms<self.current_ms+500:
              if str(ms) in self.hit_notes:
                if note in self.hit_notes[str(ms)]:
                  continue
              if ((note == 4 and self.in_m.ikjp(KEY_LEFT)) or (note == 5 and self.in_m.ikjp(KEY_DOWN)) or (note == 6 and self.in_m.ikjp(KEY_UP)) or (note == 7 and self.in_m.ikjp(KEY_RIGHT))) and (self.current_ms-200 <= float(ms) <= self.current_ms+200):
                self.rel_score = min(self.rel_score+5,100)
                if str(ms) in self.hit_notes:
                  self.hit_notes[str(ms)].append(note)
                else:
                  self.hit_notes[str(ms)] = [note]
                self.p_pose=(note,1)
              elif ((note == 14 and self.in_m.ikp(KEY_LEFT)) or (note == 15 and self.in_m.ikp(KEY_DOWN)) or (note == 16 and self.in_m.ikp(KEY_UP)) or (note == 17 and self.in_m.ikp(KEY_RIGHT))) and (self.current_ms-100 <= float(ms) <= self.current_ms+100):
                self.rel_score = min(self.rel_score+2,100)
                if str(ms) in self.hit_notes:
                  self.hit_notes[str(ms)].append(note)
                else:
                  self.hit_notes[str(ms)] = [note]
                self.p_pose = (note-10, 1)
              elif note in [4,5,6,7] and float(ms) < self.current_ms-200:
                self.rel_score = max(self.rel_score-6,-100)
                if str(ms) in self.hit_notes:
                  self.hit_notes[str(ms)].append(note)
                else:
                  self.hit_notes[str(ms)] = [note]
              elif note in [0,1,2,3,10,11,12,13] and (self.current_ms-100 <= float(ms) <= self.current_ms+100):
                self.rel_score = max(self.rel_score-3,-100) if note in [0,1,2,3] else max(self.rel_score-1,-100)
                if str(ms) in self.hit_notes:
                  self.hit_notes[str(ms)].append(note)
                else:
                  self.hit_notes[str(ms)] = [note]
                self.opp_pose=(note if note in [0,1,2,3] else note-10,1)
        self.current_ms=(monotonic()-self.og_t)*1000
        if song.script:
          song.script.post_update(self,self.delta)
        self.refresh()
      self.drawer.update(self.delta)
      self.drawer.draw()
      if mod.script:
        mod.script.post_update(self,self.delta)
      self.delta = monotonic()-t
      if self.delta < 1/self.max_fps:
        sleep(1/self.max_fps-self.delta)
        self.delta = 1 / self.max_fps

try:
  g=Game()
except KeyboardInterrupt:
  pass