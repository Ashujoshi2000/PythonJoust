#Joust by S Paget

import pygame, random
pygame.mixer.pre_init(44100,-16,2,512) 
pygame.init() 


def load_sliced_sprites(w, h, filename):
     #returns a list of image frames sliced from file
     images = []
     master_image = pygame.image.load( filename )
     master_image = master_image.convert_alpha()
     master_width, master_height = master_image.get_size()
     for i in range(int(master_width/w)):
          images.append(master_image.subsurface((i*w,0,w,h)))
     return images


def loadBirds():
     birdimages = load_sliced_sprites(60,60,"playerMounted.png")
     return birdimages

def loadEnemies():
     enemyimages = load_sliced_sprites(60,58,"enemies2.png")
     return enemyimages

def loadSpawns():
    spawnimages = load_sliced_sprites(60,60,"spawn1.png")
    return spawnimages

def loadPlatforms():
     platformimages = []
     platformimages.append(pygame.image.load("plat1.png"))
     platformimages.append(pygame.image.load("plat2.png"))
     platformimages.append(pygame.image.load("plat3.png"))
     platformimages.append(pygame.image.load("plat4.png"))
     platformimages.append(pygame.image.load("plat5.png"))
     platformimages.append(pygame.image.load("plat6.png"))
     platformimages.append(pygame.image.load("plat7.png"))
     platformimages.append(pygame.image.load("plat8.png"))
     return platformimages

class platformClass(pygame.sprite.Sprite):
     def __init__(self,image,x,y):
          pygame.sprite.Sprite.__init__(self) #call Sprite initializer
          self.image = image
          self.rect = self.image.get_rect()
          self.x = x
          self.y = y
          self.rect.topleft = (x,y)
          self.right = self.rect.right
          self.top = self.rect.top


class enemyClass(pygame.sprite.Sprite):
     def __init__(self,enemyimages, spawnimages, startPos,enemyType):
          pygame.sprite.Sprite.__init__(self) #call Sprite initializer
          self.images = enemyimages
          self.spawnimages=spawnimages
          self.frameNum = 0
          self.enemyType = enemyType
          self.image = self.spawnimages[0]
          self.rect = self.image.get_rect()
          self.next_update_time = 0
          self.next_anim_time = 0
          self.x = startPos[0]
          self.y = startPos[1]
          self.flap=0
          self.facingRight = True
          self.xspeed = random.randint(3,10)
          self.targetXSpeed = 10
          self.yspeed = 0
          self.walking = True
          self.flapCount = 0
          self.spawning=True
         

     def update(self, current_time,keys,platforms,god):
          if self.next_update_time<current_time:  # only update every 30 millis
                    self.next_update_time = current_time+50
                    if self.spawning:
                           self.frameNum +=1
                           self.image = self.spawnimages[self.frameNum]
                           self.next_update_time += 100
                           self.rect.topleft = (self.x,self.y)
                           if self.frameNum==5:
                               self.spawning=False
                    else:
                            #see if we need to accelerate
                            if abs(self.xspeed) < self.targetXSpeed:
                                    self.xspeed += self.xspeed/abs(self.xspeed)/2
                            #work out if flapping...
                            if random.randint(0,10)>8 and (not keys[pygame.K_1] or not god.on):
                                    if self.flap < 1:
                                            if self.yspeed > -250:
                                                    self.yspeed -=3
                                            self.flap = 3
                            else:
                                    self.flap -=1

                            self.x = self.x + self.xspeed
                            self.y = self.y + self.yspeed
                            if not self.walking:
                                    self.yspeed += 0.4
                            if self.yspeed > 10:        #this is all handling the
                                    self.yspeed = 10        #screen edges, looping between screens
                            if self.yspeed < -10:       #etc...
                                    self.yspeed = -10
                            if self.y < 0:
                                 self.y=0
                                 self.yspeed = 2
                            if self.y > 550:
                                    self.y = 550
                                    self.yspeed=0
                            if self.x < -48:
                                    self.x = 900
                            if self.x >900:
                                    self.x = -48
                            self.rect.topleft = (self.x,self.y)
                            #check for platform collision
                            collidedPlatforms = pygame.sprite.spritecollide(self,platforms,False,collided=pygame.sprite.collide_mask)
                            self.walking = False
                            if (((self.y >40 and self.y < 45) or (self.y >220 and self.y < 225)) and (self.x < 0 or self.x > 860)):  #catch when it is walking between screens
                                    self.walking = True
                                    self.yspeed = 0
                            else:
                                    for collidedPlatform in collidedPlatforms:
                                         self.bounce(collidedPlatform)
                            self.rect.topleft = (self.x,self.y)
                            if self.walking:
                                    if self.next_anim_time < current_time:
                                            if self.xspeed != 0:
                                                    self.next_anim_time = current_time + 100/abs(self.xspeed)
                                                    self.frameNum +=1
                                                    if self.frameNum > 3:
                                                            self.frameNum = 0
                                            else:
                                                    self.frameNum = 3
                            else:
                                    if self.flap>0:
                                            self.frameNum = 6
                                    else:
                                            self.frameNum = 5                                           
                            self.image = self.images[((self.enemyType*7)+self.frameNum)]
                            if self.xspeed <0 or (self.xspeed == 0 and self.facingRight == False):
                                    self.image = pygame.transform.flip(self.image, True, False)
                                    self.facingRight = False
                            else:
                                    self.facingRight = True


     def bounce(self,collidedThing):
          collided=False
          if self.y < (collidedThing.y-20) and ((self.x > (collidedThing.x - 40) and self.x < (collidedThing.rect.right-10))):
               #coming in from the top?
               self.walking = True
               self.yspeed = 0
               self.y = collidedThing.y - self.rect.height+3
          elif self.x < collidedThing.x:
               #colliding from left side
               collided = True
               self.x = self.x -10
               self.xspeed = -2
          elif self.x > collidedThing.rect.right-50:
               #colliding from right side
               collided = True
               self.x = self.x +10
               self.xspeed = 2
          elif self.y > collidedThing.y:
               #colliding from bottom
               collided = True
               self.y = self.y + 10
               self.yspeed = 0     
          return collided
     
class playerClass(pygame.sprite.Sprite):
     def __init__(self,birdimages,spawnimages):
          pygame.sprite.Sprite.__init__(self) #call Sprite initializer
          self.images = birdimages
          self.frameNum = 0
          self.image = self.images[self.frameNum]
          self.rect = self.image.get_rect()
          self.next_update_time = 0
          self.next_anim_time = 0
          self.x = 300
          self.y = 440
          self.facingRight = True
          self.xspeed = 0
          self.yspeed = 0
          self.flap = False
          self.walking = True
          self.playerChannel= pygame.mixer.Channel(0)
          self.flapsound = pygame.mixer.Sound("joustflaedit.wav")
          self.skidsound = pygame.mixer.Sound("joustski.wav")
          self.bumpsound = pygame.mixer.Sound("joustthu.wav")



     def update(self, current_time,keys,platforms,enemies,god):
          # Update every 30 milliseconds
          if self.next_update_time < current_time:
               self.next_update_time = current_time + 30
               if keys[pygame.K_LEFT]:
                    if self.xspeed >-10:
                         self.xspeed -=0.5
               elif keys[pygame.K_RIGHT]:
                    if self.xspeed <10:
                         self.xspeed +=0.5
               if keys[pygame.K_SPACE]:
                    if self.flap == False:
                         self.playerChannel.stop()
                         self.flapsound.play(0)
                         if self.yspeed > -250:
                              self.yspeed -=3
                         self.flap = True
               else:
                    self.flap = False
               self.x = self.x + self.xspeed
               self.y = self.y + self.yspeed
               if not self.walking:
                    self.yspeed += 0.4
               if self.yspeed > 10:
                    self.yspeed = 10
               if self.yspeed < -10:
                    self.yspeed = -10
               if self.y < 0:
                    self.y = 0
                    self.yspeed=2
               if self.y > 550:
                    self.y = 550
                    self.yspeed=0
               if self.x < -48:
                    self.x = 900
               if self.x >900:
                    self.x = -48
               self.rect.topleft = (self.x,self.y)
               #check for enemy collision
               collidedBirds = pygame.sprite.spritecollide(self,enemies,False,collided=pygame.sprite.collide_mask)
               for bird in collidedBirds:
                    #check each bird to see if above or below
                    if bird.y > self.y:
                         self.bounce(bird)
                         bird.kill()
     
                    elif bird.y < self.y-5 and not god.on:
                         self.kill()
                    else:
                         self.bounce(bird)
                         bird.bounce(self)
               #check for platform collision
               collidedPlatforms = pygame.sprite.spritecollide(self,platforms,False,collided=pygame.sprite.collide_mask)
               self.walking = False
               if (((self.y >40 and self.y < 45) or (self.y >250 and self.y < 255)) and (self.x < 0 or self.x > 860)):  #catch when it is walking between screens
                    self.walking = True
                    self.yspeed = 0
               else:
                    collided=False
                    for collidedPlatform in collidedPlatforms:   
                         collided = self.bounce(collidedPlatform)
                    if collided:
                         #play a bump sound
                         self.playerChannel.play(self.bumpsound)
               self.rect.topleft = (self.x,self.y)
               if self.walking:
                    #if walking
                    if self.next_anim_time < current_time:
                         if self.xspeed != 0:
                              if (self.xspeed>5 and keys[pygame.K_LEFT]) or (self.xspeed<-5 and keys[pygame.K_RIGHT]):

                                   if  self.frameNum != 4:
                                        self.playerChannel.play(self.skidsound)
                                   self.frameNum=4
                              else:
                                   self.next_anim_time = current_time + 200/abs(self.xspeed)
                                   self.frameNum +=1
                                   if self.frameNum > 3:
                                        self.frameNum = 0
                         elif self.frameNum == 4:
                              self.frameNum = 3
                              self.playerChannel.stop()

                    self.image = self.images[self.frameNum]    
               else:
                    if self.flap:
                         self.image = self.images[6]
     
                    else:
                         self.image = self.images[5]
               if self.xspeed <0 or (self.xspeed == 0 and self.facingRight == False):
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.facingRight = False
               else:
                    self.facingRight = True
                    
     def bounce(self,collidedThing):
          collided=False
          if self.y < (collidedThing.y-20) and ((self.x > (collidedThing.x - 40) and self.x < (collidedThing.rect.right-10))):
               #coming in from the top?
               self.walking = True
               self.yspeed = 0
               self.y = collidedThing.y - self.rect.height +1
          elif self.x < collidedThing.x:
               #colliding from left side
               collided = True
               self.x = self.x -10
               self.xspeed = -2
          elif self.x > collidedThing.rect.right-50:
               #colliding from right side
               collided = True
               self.x = self.x +10
               self.xspeed = 2
          elif self.y > collidedThing.y:
               #colliding from bottom
               collided = True
               self.y = self.y + 10
               self.yspeed = 0     
          return collided

class godmode(pygame.sprite.Sprite):
     def __init__(self):
          pygame.sprite.Sprite.__init__(self) #call Sprite initializer
          self.pic = pygame.image.load("god.png")
          self.image = self.pic
          self.on = False
          self.rect = self.image.get_rect()
          self.rect.topleft = (850,0)
          self.timer = pygame.time.get_ticks()
          
     def toggle(self,current_time):
          if current_time>self.timer:
               self.on = not self.on
               self.timer = current_time+1000
          
          
def generateEnemies(enemyimages, spawnimages, enemyList,spawnPoints, enemiesToSpawn):
     for count in range(2):
          enemyList.add(enemyClass(enemyimages, spawnimages, spawnPoints[count],0))
          enemiesToSpawn -=1
          
     return enemyList, enemiesToSpawn

def main():
     window = pygame.display.set_mode((900, 650))
     pygame.display.set_caption('Joust')
     screen = pygame.display.get_surface()
     clearSurface = screen.copy()
     player =  pygame.sprite.RenderUpdates()
     enemyList =  pygame.sprite.RenderUpdates()
     platforms =  pygame.sprite.RenderUpdates()
     godSprite = pygame.sprite.RenderUpdates()
     birdimages = loadBirds()
     enemyimages = loadEnemies()
     spawnimages = loadSpawns()
     platformImages = loadPlatforms()
     playerbird = playerClass(birdimages,spawnimages)
     god = godmode()
     godSprite.add(godmode())
     spawnPoints = [[420,80],[50,255]]
     plat1 = platformClass(platformImages[0],200,550)  #we create each platform by sending it the relevant platform image, the x position of the platform and the y position
     plat2 = platformClass(platformImages[1],350,395)
     plat3 = platformClass(platformImages[2],350,130)
     plat4 = platformClass(platformImages[3],0,100)
     plat5 = platformClass(platformImages[4],759,100)
     plat6 = platformClass(platformImages[5],0,310)
     plat7 = platformClass(platformImages[6],759,310)
     plat8 = platformClass(platformImages[7],600,290)
     player.add(playerbird)
     platforms.add(plat1,plat2,plat3,plat4,plat5,plat6,plat7,plat8)
     pygame.display.update()
     nextSpawnTime = pygame.time.get_ticks() + 2000
     enemiesToSpawn = 6
     running = True
     while running:
          current_time = pygame.time.get_ticks()
          if current_time>nextSpawnTime and enemiesToSpawn>0:
                   enemyList, enemiesToSpawn = generateEnemies(enemyimages,spawnimages, enemyList,spawnPoints,enemiesToSpawn)
                   nextSpawnTime = current_time+5000
          keys = pygame.key.get_pressed()
          pygame.event.clear()
          #If they have pressed Escape, close down Pygame
          if keys[pygame.K_ESCAPE]:
               running=False
          if keys[pygame.K_g]:
               god.toggle(current_time)
          player.update(current_time,keys,platforms,enemyList,god)
          platforms.update()
          enemyList.update(current_time,keys,platforms,god)
          enemiesRects = enemyList.draw(screen)
          if god.on:
               godrect = godSprite.draw(screen)
          else:
               godrect = pygame.Rect(850,0,50,50)
          playerRect = player.draw(screen)
          platRects = platforms.draw(screen)
          pygame.display.update(playerRect)
          pygame.display.update(platRects)
          pygame.display.update(enemiesRects)
          pygame.display.update(godrect)
          player.clear(screen,clearSurface)
          enemyList.clear(screen,clearSurface)
          godSprite.clear(screen,clearSurface)



main()
pygame.quit()