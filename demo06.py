'''
更新日志：
1.优化键盘监听器逻辑,支持多事件监听
2.修复足球在边界卡住的问题
3.修复足球减速方法除数为零异常
4.暂时使用手动操作代替敌人AI

test2
'''

import sys
import pygame
from math import sqrt, pow
from copy import copy

'''足球类,继承自Sprite类'''
class Ball(pygame.sprite.Sprite):
    def __init__(self, image, position):
        #初始化动画精灵
        pygame.sprite.Sprite.__init__(self)
        self.image=image        #加载图片素材
        self.rect=self.image.get_rect()
        self.last_updated=0
        self.rect.left ,self.rect.top =position[0],position[1]  # 放置在指定位置
        self.width, self.hight, self.radius=25, 25, 25/2        # 碰撞体积（长，宽，半径）
        self.speed=[0, 0]           # 速度
        self.have=False             # 球是否被球员获得
        self.have_people=None       # 球被哪个球员获得

    '''移动'''
    def update(self):
        # 球没有被球员获得，自由移动
        if self.have==False:
            now = pygame.time.get_ticks()
            #减速
            if now - self.last_updated > 500:
                self.last_updated=now
                self.slow()
            self.rect=self.rect.move(self.speed)
            #print(self.speed)
        # 球被球员获得
        else:
            self.rect=self.have_people.rect
            self.rect=self.rect.move([13, 25])  #先把球移到角色中心
            self.move_direction()
            self.border()

    '''根据角色朝向设置偏移'''
    def move_direction(self):
        offset=15
        if self.have_people.direction==0:
            self.rect=self.rect.move([0, -offset])
        elif self.have_people.direction==1:
            self.rect=self.rect.move([offset, -offset])
        elif self.have_people.direction==2:
            self.rect=self.rect.move([offset, 0])
        elif self.have_people.direction==3:
            self.rect=self.rect.move([offset, offset])
        elif self.have_people.direction==4:
            self.rect=self.rect.move([0, offset])
        elif self.have_people.direction==5:
            self.rect=self.rect.move([-offset, offset])
        elif self.have_people.direction==6:
            self.rect=self.rect.move([-offset, 0])
        elif self.have_people.direction==7:
            self.rect=self.rect.move([-offset, -offset])

    '''减速'''
    def slow(self):
        if (self.speed[0]!=0 or self.speed[1]!=0):
            before=copy(self.speed)
            self.speed[0]-=1.5*self.speed[0]/(sqrt(pow(self.speed[0], 2)+pow(self.speed[1], 2)) +0.01)
            self.speed[1]-=1.5*self.speed[1]/(sqrt(pow(self.speed[0], 2)+pow(self.speed[1], 2)) +0.01)
            if before[0]*self.speed[0]<0:   #防止减速后反向加速
                self.speed[0]=0
            if before[1]*self.speed[1]<0:
                self.speed[1]=0
    
    '''边界,防止出界'''
    def border(self):
        if self.rect.left<=0:
            self.rect.left=0
        elif self.rect.left>=WIDTH-25:
            self.rect.left=WIDTH-25
        if self.rect.top<=0:
            self.rect.top=0
        elif self.rect.top>=HINGT-25:
            self.rect.top=HINGT-25

'''球门类,继承自Sprite类'''
class Goal(pygame.sprite.Sprite):
    def __init__(self, image, position):
        #初始化动画精灵
        pygame.sprite.Sprite.__init__(self)
        self.image=image        #加载图片素材
        self.rect=self.image.get_rect()
        self.rect.left ,self.rect.top =position[0],position[1]  # 放置在指定位置
        self.goal_img=pygame.transform.rotozoom( pygame.image.load("img\goal.png").convert_alpha(),0 ,0.5 )#进球动画
        self.if_goal=False    #是否进球

    '''碰撞检测，进球'''
    def goalCheck(self, object):
        #两个精灵之间的像素蒙版检测，更为精准的一种检测方式
        if pygame.sprite.collide_mask(self, object):
            self.if_goal= True
        
'''球员角色类,继承自Sprite类'''
class Athlete(pygame.sprite.Sprite):
    def __init__(self, images, position, max_speed, direction):
        #初始化动画精灵
        pygame.sprite.Sprite.__init__(self)
        #加载图片素材库
        self.all_frames=images
        #当前角色状态图片库，当前角色状态图片
        self.current_frames=self.all_frames[direction]
        self.current_frame_index=0             #当前帧序号
        self.image=self.all_frames[direction][self.current_frame_index]
        self.rect=self.image.get_rect()

        self.last_updated=0         # 上次刷新时刻
        self.width, self.hight, self.radius=40, 40, 40/2        #角色碰撞体积（长，宽，半径）
        self.rect.left ,self.rect.top =position[0],position[1]  # 将角色放置在指定位置
        self.direction=direction    # 当前角色朝向
        self.max_speed=max_speed    # 设置最大速度
        self.current_speed=0        # 当前速度
        self.speed=[self.current_speed, self.current_speed]     # 速度
        self.run=False              # 移动标记
        self.haveBall=False         # 是否有球标记
        self.last_HitBall=0         # 上次踢球时刻
        self.hit_speed=6            # 踢球力度
    
    '''移动角色'''
    def update(self): 
        self.rect=self.rect.move(self.speed)
        self.border()
        self.animate()
    
    '''依次播放运动帧'''
    def animate(self):
        now = pygame.time.get_ticks()
        # 不移动，不播放移动帧
        if self.run==False:
            self.image = self.current_frames[self.current_frame_index]
         # 移动，播放移动帧
        elif now - self.last_updated > 100: # 定时更新移动帧
            self.last_updated=now
            self.current_frame_index += 1
            if self.current_frame_index>len(self.current_frames)-1:
                self.current_frame_index=1
            self.current_frame_index = (self.current_frame_index)
            self.image = self.current_frames[self.current_frame_index]
    
    '''踢球方法'''
    def hit(self, ball):
        # 检查是否得到球
        if self.haveBall==True:
            self.last_HitBall = pygame.time.get_ticks()
            self.haveBall=False
            ball.have_people=None 
            ball.have=False
            self.current_speed=self.max_speed      # 恢复角色速度
            if self.direction==0:
                ball.speed=add(self.speed, [0, -self.hit_speed])
            elif self.direction==1:
                ball.speed=add(self.speed, [self.hit_speed, -self.hit_speed])
            elif self.direction==2:
                ball.speed=add(self.speed, [self.hit_speed, 0])
            elif self.direction==3:
                ball.speed=add(self.speed, [self.hit_speed, self.hit_speed])
            elif self.direction==4:
                ball.speed=add(self.speed, [0, self.hit_speed])
            elif self.direction==5:
                ball.speed=add(self.speed, [-self.hit_speed, self.hit_speed])
            elif self.direction==6:
                ball.speed=add(self.speed, [-self.hit_speed, 0])
            elif self.direction==7:
                ball.speed=add(self.speed, [-self.hit_speed, -self.hit_speed])

    '''碰撞检测,得球'''
    def collideCheck(self, object):
        now = pygame.time.get_ticks()
        if now - self.last_HitBall > 200:                  #达到冷却时间
            #两个精灵之间的像素蒙版检测，更为精准的一种检测方式
            if pygame.sprite.collide_mask(self, object): 
                if object.have==True and object.have_people!=self:    #抢球
                    object.have_people.haveBall=False
                    object.have_people.last_HitBall=now
                    object.have_people=self
                    #print("++++抢球")

                self.current_speed=self.max_speed*0.8      #限制角色速度
                self.haveBall=True
                object.speed=[0, 0]
                object.have=True
                object.have_people=self

    '''边界,防止角色出界'''
    def border(self):
        if self.rect.left<=0:
            self.rect.left=0
        elif self.rect.left>=WIDTH-50:
            self.rect.left=WIDTH-50
        if self.rect.top<=0:
            self.rect.top=0
        elif self.rect.top>=HINGT-50:
            self.rect.top=HINGT-50
    
    '''管它是干啥的,写上就对了！'''
    def __setitem__(self, k, v):
        self.k = v

'''玩家类,继承Aathlete类'''
class Player(Athlete):
    def __init__(self, images, position, speed, direction):
        super(Player, self).__init__(images, position, speed, direction)
        #用集合存储键盘的双键移动
        self.key_list = set()
                
    '''重写移动方法'''
    def update(self, *args):
        # 按下方向键时进行判断
        if self.key_list & {pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT} != set():
            self.run=True
            if self.haveBall==True:        #得球时限制最大速度
                self.current_speed=self.max_speed*0.8
            else:
                self.current_speed=self.max_speed
        	# 同时按下两个键时进行判断
            if self.key_list >= {pygame.K_UP, pygame.K_LEFT}:
                self.direction=7
                self.speed=[-self.current_speed, -self.current_speed]
            elif self.key_list >= {pygame.K_UP, pygame.K_RIGHT}:
                self.direction=1
                self.speed=[self.current_speed, -self.current_speed]
            elif self.key_list >= {pygame.K_DOWN, pygame.K_RIGHT}:
                self.direction=3
                self.speed=[self.current_speed, self.current_speed]
            elif self.key_list >= {pygame.K_DOWN, pygame.K_LEFT}:
                self.direction=5
                self.speed=[-self.current_speed, self.current_speed]
            # 按下一个键时进行判断
            elif pygame.K_LEFT in self.key_list:
                self.direction=6
                self.speed=[-self.current_speed, 0]
            elif pygame.K_RIGHT in self.key_list:
                self.direction=2
                self.speed=[self.current_speed, 0]
            elif pygame.K_UP in self.key_list:
                self.direction=0
                self.speed=[0, -self.current_speed]
            elif pygame.K_DOWN in self.key_list:
                self.direction=4
                self.speed=[0, self.current_speed]
            self.current_frames=self.all_frames[self.direction]                      #切换当前角色状态图片库
            self.image=self.current_frames[self.current_frame_index]    #更新当前角色状态图片
        # 没有按下，停止移动
        else:
            self.run=False
            self.current_frame_index=0
            self.current_speed=0
            self.speed=[self.current_speed, self.current_speed]
        if pygame.K_SPACE in self.key_list:     # 按下空格，踢球
            self.hit(ball)
        self.rect=self.rect.move(self.speed)
        self.border()
        self.animate()

    '''按键按下时将监听到的键值加入列表'''
    def key_down(self, key):
        self.key_list.add(key)
            
    '''按键松开时将监听到的键值从列表中删除'''
    def key_up(self, key):
        self.key_list.remove(key)

'''敌人类,继承Athlete类'''
class Enemy(Athlete):
    def __init__(self, images, position, speed, direction):
        super(Enemy, self).__init__(images, position, speed, direction)
        #用集合存储键盘的双键移动
        self.key_list = set()

    '''重写移动方法'''
    def update(self, *args):
        # 按下方向键时进行判断
        if self.key_list & {pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d} != set():
            self.run=True
            if self.haveBall==True:        #得球时限制最大速度
                self.current_speed=self.max_speed*0.8
            else:
                self.current_speed=self.max_speed
            # 同时按下两个键时进行判断
            if self.key_list >= {pygame.K_w, pygame.K_a}:
                self.direction=7
                self.speed=[-self.current_speed, -self.current_speed]
            elif self.key_list >= {pygame.K_w, pygame.K_d}:
                self.direction=1
                self.speed=[self.current_speed, -self.current_speed]
            elif self.key_list >= {pygame.K_s, pygame.K_d}:
                self.direction=3
                self.speed=[self.current_speed, self.current_speed]
            elif self.key_list >= {pygame.K_s, pygame.K_a}:
                self.direction=5
                self.speed=[-self.current_speed, self.current_speed]
            # 按下一个键时进行判断
            elif pygame.K_a in self.key_list:
                self.direction=6
                self.speed=[-self.current_speed, 0]
            elif pygame.K_d in self.key_list:
                self.direction=2
                self.speed=[self.current_speed, 0]
            elif pygame.K_w in self.key_list:
                self.direction=0
                self.speed=[0, -self.current_speed]
            elif pygame.K_s in self.key_list:
                self.direction=4
                self.speed=[0, self.current_speed]
            self.current_frames=self.all_frames[self.direction]                      #切换当前角色状态图片库
            self.image=self.current_frames[self.current_frame_index]    #更新当前角色状态图片
        # 没有按下，停止移动
        else:
            self.run=False
            self.current_frame_index=0
            self.current_speed=0
            self.speed=[self.current_speed, self.current_speed]
        if pygame.K_LSHIFT in self.key_list:     # 按下空格，踢球
            self.hit(ball)
        self.rect=self.rect.move(self.speed)
        self.border()
        self.animate()

    '''按键按下时将监听到的键值加入列表'''
    def key_down(self, key):
            self.key_list.add(key)
                
    '''按键松开时将监听到的键值从列表中删除'''
    def key_up(self, key):
            self.key_list.remove(key)

'''物体碰到边界反弹'''
def borderBounce(object):
    if(object.rect.left<=0 or object.rect.left+object.width>=WIDTH):
        object.speed[0]*=-1
    if(object.rect.top<=0 or object.rect.top+object.hight>=HINGT):
        object.speed[1]*=-1

'''图片加载,返回一个二维图片列表,8组方向,每组5张'''
def imgload(id):
    playerImgs=[]
    for i in range(8):
        playerImgs.append([])
        for j in range(5):
            #print("loading----------img/player/player{}{}{}.png".format(id, i, j) )
            playerImgs[-1].append(pygame.image.load("img/player/player{}{}{}.png".format(id ,i, j)) )
    return playerImgs

# 向量相加
def add(a, b):
    after=[]
    if len(a)!=len(b):
        print("----向量维数不同!")
    for i in range(len(a)):
        after.append(a[i]+b[i])
    return after

#窗口尺寸
WIDTH=980
HINGT=700
#初始化
pygame.init()
pygame.mixer.init()
#设置窗口
screen=pygame.display.set_mode((WIDTH, HINGT))
pygame.display.set_caption("趣味足球1.0.6")
#加载背景音乐、音效
pygame.mixer.music.load("music\Desastre.ogg")
pygame.mixer.music.play(-1)
laughSound=pygame.mixer.Sound("music\laugh.wav")
#加载图片
playerImgs=imgload(0)#  队友0，敌人1
enemyImgs=imgload(1)
goal0Img=pygame.image.load("img\goal0.png").convert_alpha()
goal0Img=pygame.transform.rotozoom(goal0Img, 90, 0.7)
goal1Img=pygame.image.load("img\goal1.png").convert_alpha()
goal1Img=pygame.transform.rotozoom(goal1Img, 90, 0.7)
ballImg=pygame.image.load("img/ball.png").convert_alpha()
background=pygame.image.load("img\pitch.png").convert_alpha()
background=pygame.transform.rotozoom(background, 90, 0.7)
#添加背景图片
screen.blit(background, (0,0))
#添加进动作精灵组
groupAthlete=pygame.sprite.Group()
groupGoal=pygame.sprite.Group()
groupBall=pygame.sprite.Group()
#创建玩家
player=Player(playerImgs, [WIDTH/2+100,HINGT/2], 4, 6)
groupAthlete.add(player)
#创建敌人
enemy=Enemy(enemyImgs, [WIDTH/2-100,HINGT/2], 4, 6)
groupAthlete.add(enemy)
#创建球门
goal0=Goal(goal0Img, (-59, 280))
groupGoal.add(goal0)
goal1=Goal(goal1Img, (925, 280))
groupGoal.add(goal1)
#创建球
ball=Ball(ballImg, (WIDTH/2-12,HINGT/2-12))
groupBall.add(ball)
 


clock=pygame.time.Clock()
'''主循环'''
while True:
    #检查球员得球
    player.collideCheck(ball)
    enemy.collideCheck(ball)
    #检查进球
    for each in groupGoal:
        each.goalCheck(ball)
    #更新
    groupAthlete.update()
    groupBall.update()
    #边界反弹
    borderBounce(ball)
    #更新图像
    screen.blit(background, (0,0))
    groupBall.draw(screen)
    groupAthlete.draw(screen)
    groupGoal.draw(screen)
    for each in groupGoal:# 球进了
        if each.if_goal:
            laughSound.play(1)
            screen.blit(each.goal_img, [WIDTH/2-150, HINGT/2-150])

    for event in pygame.event.get():
        #键盘按下，控制玩家移动，踢球
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player.key_down(pygame.K_UP)# 向集合中加入键值
            elif event.key == pygame.K_DOWN:
                player.key_down(pygame.K_DOWN)
            elif event.key == pygame.K_RIGHT:
                player.key_down(pygame.K_RIGHT)
            elif event.key == pygame.K_LEFT:
                player.key_down(pygame.K_LEFT)
            elif event.key == pygame.K_SPACE:
                player.key_down(pygame.K_SPACE)

            if event.key == pygame.K_w:
                enemy.key_down(pygame.K_w)# 向集合中加入键值
            elif event.key == pygame.K_s:
                enemy.key_down(pygame.K_s)
            elif event.key == pygame.K_d:
                enemy.key_down(pygame.K_d)
            elif event.key == pygame.K_a:
                enemy.key_down(pygame.K_a)
            elif event.key == pygame.K_LSHIFT:
                enemy.key_down(pygame.K_LSHIFT)
        # 松开键盘,在列表中删除按键值
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                player.key_up(pygame.K_UP)
            elif event.key == pygame.K_DOWN:
                player.key_up(pygame.K_DOWN)
            elif event.key == pygame.K_RIGHT:
                player.key_up(pygame.K_RIGHT)
            elif event.key == pygame.K_LEFT:
                player.key_up(pygame.K_LEFT)
            elif event.key == pygame.K_SPACE:
                player.key_up(pygame.K_SPACE)

            if event.key == pygame.K_w:
                enemy.key_up(pygame.K_w)
            elif event.key == pygame.K_s:
                enemy.key_up(pygame.K_s)
            elif event.key == pygame.K_d:
                enemy.key_up(pygame.K_d)
            elif event.key == pygame.K_a:
                enemy.key_up(pygame.K_a)
            elif event.key == pygame.K_LSHIFT:
                enemy.key_up(pygame.K_LSHIFT)
        
        #点击退出，关闭窗口
        if event.type==pygame.QUIT:
            sys.exit()

    #刷新屏幕,固定帧率
    pygame.display.flip()
    clock.tick(30)