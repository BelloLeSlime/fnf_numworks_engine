from ion import *
class Input:
  p=[]
  jp=[]
  jr=[]
  def process(self):
    self.jp=[]
    self.jr=[]
    for k in range(55):
      if keydown(k):
        if not k in self.p:
          self.p+=[k]
          self.jp+=[k]
    for k in self.p:
      if not keydown(k):
        self.p.remove(k)
        self.jr+=[k]
  def ikp(self,k):
    return k in self.p
  def ikjp(self,k):
    return k in self.jp
  def ikjr(self,k):
    return k in self.jr