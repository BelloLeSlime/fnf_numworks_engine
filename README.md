# Friday Night Funkin: Numworks Engine *(python)*



### What is the project? 

The goal of the python version of **Numworks Engine** is simple: **being able to make little FNF mods with only your Numworks Calculator in the Python IDE**. This engine itself and all the other tools are even made in the calculator (because I was bored in math class).



### What's included?

There is:
- customizable menu
- multiple songs support
- script feature (to code mechanics or visual effect)
- full controll on the stage
- an image and chart editor
- moving camera system
- optimization so the game can run at 12 FPS



### What's NOT included?

There is not:
- options and credits
- native zooming
- comments because of the memory (good luck understanding that LMAO)
- the score, misses, combos, rankings and rate
- the end of the song (win or loose, you are immortal)
- spaces and blank lines (memory optimization and everything)
- actual animations: the animations that I will talk about are just one single frame.
- event: to mimic them, just use song scripts and check `game.current_ms` to trigger stuff.



### How can I play already made FNF mods? 

All you need to do is downloading `fnf.py`, `input\_manager.py`, `drawer.py` and the `files.py` and `fnf\_data.py` aviable in the release section relative to the mod you wanna install. Then, all you need to do is putting them on your calculator and running `fnf.py`.



### What are `rect_edit.py` and `chart_editor.py`? 

`rect_edit.py` is an image editor. You can make images for your mods with a few rectangles. To make a rectangle, press **OK** and release it somewhere else. You can then move it with **POWER**, resize it with **SQUARE**, paint it with the selected color with **COMMA**, select the color of it with **SQRT**, move it to the front or the back with **PLUS** and **MINUS**, and to the very front and very back with **MULTIPLICATION** and **DIVISION**, and delete it with **BACKSPACE**. To select a color, press **ANS** (you will then enter the RGB color). With **SHIFT** + **ARROWS**, you can move the cursor one pixel at a time, and with **ALPHA** + **ARROWS** you can move it 5 times faster. You can import an image in your files with **XNT**, access the options with **TOOLBOX** and finally export the image with **EXE**. You can also shift all the rectangles with **LN**, **SINE**, **COSINE** and **TANGEANT**. When you export an image, it prints all the data one line at a time (because of the 144-character limit of the copy and paste function of the calculator), and you will have to copy the lines and paste them in `files.py` like this : `image = RectImage(<...data...>)`. The program can't save anything from itself because of the restrictions of the calculator. That's fastidious and risky, but it's the only way to save data.
It needs `input_manager.py`, `files.py` and `drawer.py`.
-# note that you will need to make a rectangle that covers all of your image and put it in the very back: it will not be displayed and is for scaling

`chart_editor.py` is, well, a chart editor. You can put notes with the **ARROWS**, and going down or up using **SHIFT** and **EXP**. To change the selected character, press **ALPHA**. **XNT** imports, **EXE** exports and **SQUARE** changes the BPM (don't change it when there are notes already, it may break). To add sustain, press **TOOLBOX**, **IMAGINARY**, **COMMA** or **POWER**. Same as the image editor, you must copy the lines and paste them in `files.py` when you export. However, don't make the full chart, make little parts (like 1000c at max) and make them individual charts (`chart1=Chart(...)`	`chart2=Chart(...)`	`chart3=Chart(...)`) and then fuse them (`chart = chart1.fuse(chart2).fuse(chart3)`). Remember to put the BPM and the speed (`chart=Chart([...], 96, 0.1)`).
It needs `input_manager.py`, `files.py` with left, down, up and right arrows images and `drawer.py`.



### How can I make a mod?

Creating a mod requires:
- creating assets for the mod (the characters (idle, left, down, up and right, and icon), the main menu and menu background (can be remplaced with a simple rectangle if not necessary), and the assets for your stages)
- creating charts (with the chart editor)
- basic knowledge of coding with python (even if you can do things without actually coding)

Tips before starting:
- Use as few space as you can: the calculator have very few memory, so use your characters smart
- The three limits here are the memory limit (what's in your scripts), the RAM limit (how much you create (a dictionnary with hundreds of lists isn't a great idea)) and the speed limit (if your script takes a lot of calculations). Optimize the memory first, then the speed, and finally the RAM if you can.

#### 1. The structure
- Go to `fnf_data.py` (the mod itself) and create a mod structure
```python
mod = Mod(
    "Mod", #The name of your mod
    [], #The list of the songs there is in your mod
    Menu( #The menu
        f.RectImage([0,0,320,222,0,0,0,0,0,320,222,245,245,245]) #A plain gray image for the main menu
        (140,180), #The position of the "Press OK" label (put it out of bounds if unneessary)
        (50,20), #The position of the name label
        f.RectImage([0,0,320,222,0,0,0,0,0,320,222,225,225,225]) #Another plain gray image for the menu
    ),
    None #
)
```
- To add a song, you must first define the characters, the stage and the arrow set of this song
```python
bf=Char(
  { #The animations
    "idle":f.bf_idle, #The images (that you will need to draw, but just use placeholder by now)
    "left":f.bf_left,
    "down":f.bf_down,
    "up":f.bf_up,
    "right":f.bf_right,
  },
  (0,200,255), #The color, used for the bottom bar
  f.bf_icon #The icon
)
```
```python
test_stage=Stage(
  [
    [
        "bg", #The type (here, "bg" for background. There is also "player" for the player, "opp" for the opponent, "anim" for an animatable and "sprite" for just an image)
        f.bg_stage, #In case of the bg, sprite and anim, the image
        (0,0,320) #The position and scale of the image (here, 0, 0 for the origin and 320 to take all the screen)
    ], #note that the background is buggy, and I'm too lazy to fix it
    [
        "player",
        bf, #In case of the player and opp, the character
        (200,100,65) #The position and scale. Note that the screen is 320px by 222px.
    ],
    [
        "opp",
        dad,
        (50,100,65)
    ],
  ]
)
```
```
arrow_set=[f.left_arrow, f.down_arrow, f.up_arrow, f.right_arrow]
```
Then you can make your song:
```python
test_song = Song(
    "Test Song", #The name of the song
    test_stage, #The stage
    f.chart, #The chart from your files.py
    bf, #The player
    dad, #The opponent
    arrow_set, #The arrow set
    None, #The song script
    False #If True, you will have to press the notes on the left instead of right
)
```
Don't forget to add your song to the song list
```python
mod = Mod(
    "Mod",
    [test_song],
    Menu(
        f.RectImage([0,0,320,222,0,0,0,0,0,320,222,245,245,245])
        (140,180),
        (50,20),
        f.RectImage([0,0,320,222,0,0,0,0,0,320,222,225,225,225])
    ),
    None
)
```

#### 2. The images
There isn't much to say about this part, just draw, but with rectangles. Use only a few of them, not to lose all of your works because the console just said "No there are too many lines". You can make the images black and white in the code just by putting `.grey_scale()` by the way.

#### 3. The charts
Same as before, do the charts, and don't make them big, make them small and then use the `fuse()` function.

#### 4. Spooky Scary Scripting
It's OK to me because I made the thing, but if you want more than just two characters and a stage, you must code things yourself via scripting. There are two types of scripts:
- Mod script: the script that controls the entire game
- Song scripts: scripts that are active only when a song is played

Scripts are given 5 functions in order to communicate with the game:
- `awake(self, game)`: when the mod/song starts. game here is the engine itself, so you can access every property or method of basically anything
- `pre_update(self, game, delta)`: called at the beginning of each frame. delta is the time elapsed since the last frame
- `post_update(self, game, delta)`: called at the end of each frame
- `pre_refresh(self, game, delta)`: called at the beginning of the screen refresh (each frame if in the game and not in the menu). Note that the refresh is between pre_update and post_update
- `post_refresh(self, game, delta)`: called at the end of the screen refresh

Between you do anything, I strongly recommend you to **read the code of the egine, drawer and input_manager** and understand it (not easy with no space, blank line, comment and with approximative variable names, but *memory optimization*).
I will maybe make a commented version, but for now I'm too lazy to do that. Just consider you happy that I make a full tutorial on that.

Now you understand how the engine works, you can do basically anything. To make a script, just do that:
```python
class test_script(Script):
    some_field=0
    def awake(self,game):
        print("Hi :)")
    def post_update(self,game,delta):
        print("delta: ", delta)
        print("current ms: ", game.current_ms)
```

And then just instantiate your class in the script field of the song/mod
```python
test_song = Song(
    "Test Song",
    test_stage,
    f.chart,
    bf,
    dad,
    arrow_set,
    test_script(),
    False
)
```

For exemple, here is a song script from Frostbite that adds:
- a freezing bar with a warming mechanic
- snow particles
- an animatable that reacts to the mechanic
- elements shaking

```python
from random import * #import stuff
from ion import *
class frst_script(Script):
  freeze=0 #for the freeze mechanic
  uses=0 #how many times you used Typhlosion
  typhlo_d=0 #how long Typhlosion must be on his "use" frame
  snows=[] #the snow particles
  snow_max=25
  def awake(self,game):
    game.current_ms=-9100 #starts the song later so there is an intro
    for i in range(self.snow_max):
      self.snows.append([randint(0,320),randint(0,222),randint(5,10),randint(5,10),randint(3,8),randint(4,9)]) #spawn random snow particles
  def post_update(self,game,delta):
    if game.current_ms>0:
      self.freeze+=delta #the freeze increase with time
      if self.freeze>=40:
        self.freeze=40
        game.rel_score=-100 #instant death
      if game.in_m.ikjp(KEY_OK) and self.uses<10: #the player pressed OK and can use Typhlosion to warm itself
        self.uses+=1 #increase the uses
        self.freeze=max(self.freeze-18,0) #decrease the freeze
        self.typhlo_d=1 #Typhlosion is staying in his "use" frame for 1 second
  def post_refresh(self,game,delta):
    game.drawer.fill_rect(4,44,12,102,(0,200,255)) #draw the freeze bar
    game.drawer.fill_rect(5,45,10,100,(0,100,200))
    game.drawer.fill_rect(5,145-self.freeze/40*100,10,self.freeze/40*100,(0,255,255))
    self.typhlo_d-=delta #update typhlo_d
    typhlo=game.stage.elmts[3] #here, Typhlosion is the 4th element in the stage
    if self.typhlo_d>0 or -9100+5000<game.current_ms<-9100+7000: #if Typhlosion is used OR the intro, we change his current animation ([3])
      typhlo[3]="use"
    else:
      typhlo[3]="idle"
    if self.uses>9: #if Typhlosion is used 10 times
      typhlo[2]=(typhlo[2][0],min(typhlo[2][1]+delta*70,223),typhlo[2][2]) #the Typhlosion element go down: death animation
    while len(self.snows)<self.snow_max: #spawn particles if there isn't enough
      if randint(0,1): #starts from the right
        x=randint(0,320)
        y=0
      else: #or the top
        x=320
        y=randint(0,222)
      self.snows.append([x,y,randint(5,10),randint(5,10),randint(3,8),randint(4,9)]) #create a particle with random x, y, w, h, speed x and speed y
    for snow in self.snows: #update all the particles
      snow[0]-=snow[4] #update the position
      snow[1]+=snow[5]
      game.drawer.fill_rect(snow[0],snow[1],snow[2],snow[3],(247,247,247)) #draw the particle
      if snow[0]+snow[2]<0 or snow[1]>222: #if the particle is out of the screen, delete it
        self.snows.remove(snow)
    if game.current_ms%((1/(f.frostbite.bpm/2))*60000)<=100 and typhlo[3]=="idle": #each beat AND if Typhlosion isn't used
      typhlo[2]=(randint(19,21),randint(-21,-20),92) #Typhlosion shakes from the cold
      game.stage.elmts[1][2]=(randint(-2,2),randint(202-75,203-75),80) #Same for Gold
    else:
      typhlo[2]=(20,-20,92) #Typhlosion back to normal
      game.stage.elmts[1][2]=(0,202-75,80) #Same for Gold
```

Because I'm a very nice guy, I commented this script.

And this is how you create a mod.



### Why not a .nwa app for more memory?

The original challenge was to do all on calculator (and it is the case). However, due to the lack of memory and what external apps are, I will maybe recreate it in C, C++ or Rust on day.