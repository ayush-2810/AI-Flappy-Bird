import pygame 
import neat
import time
import random
import os
pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 50)
#Window and images
GEN = 0
win_width = 575
win_height = 800
bird_imgs = [pygame.transform.scale2x(pygame.image.load(r"C:\Users\DELL\bird1.png")), 
             pygame.transform.scale2x(pygame.image.load(r"C:\Users\DELL\bird2.png")), 
             pygame.transform.scale2x(pygame.image.load(r"C:\Users\DELL\bird3.png"))]  #Transform func inc the size of the image
pipe_img = pygame.transform.scale2x(pygame.image.load(r"C:\Users\DELL\pipe.png"))
base_img = pygame.transform.scale2x(pygame.image.load(r"C:\Users\DELL\base.png"))
back_img = pygame.transform.scale2x(pygame.image.load(r"C:\Users\DELL\bg.png"))
font = pygame.font.SysFont("comicsans", 50)

#Bird class

class Bird:
    imgs = bird_imgs
    animation_time = 5
    rot_velocity = 20
    max_rotation = 25
    def __init__(self, x, y):     #Starting position of our bird
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.img_count = 0
        self.height = self.y
        self.img = self.imgs[0]
        
    def jump(self):
        self.vel = -10.5 #Moving up should be -ve vel
        self.tick_count = 0
        self.height = self.y
        
    def move(self):
        self.tick_count += 1
        d = self.vel*self.tick_count + 1.5*self.tick_count**2
        if(d>=16):    #Terminal vel
            d = (d/abs(d)) * 16
        if(d<0):
            d-=2
        self.y += d
        if d<0 or self.y < self.height + 50:
            if self.tilt < self.max_rotation:
                self.tilt = self.max_rotation
        else:
            if self.tilt > -90:
                self.tilt -= self.rot_velocity
    def draw(self, win):
        self.img_count +=1
        if self.img_count <= self.animation_time:
            self.img = self.imgs[0]
        elif self.img_count <= self.animation_time*2:
            self.img = self.imgs[1]
        elif self.img_count <= self.animation_time*3:
            self.img = self.imgs[2]
        elif self.img_count <= self.animation_time*4:
            self.img = self.imgs[1]
        elif self.img_count == self.animation_time*4 + 1:
            self.img = self.imgs[0]
            self.img_count = 0
        if self.tilt <= -80:
            self.img = self.imgs[1]
            self.img_count = self.animation_time*2
        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_img, new_rect.topleft)
    def get_mask(self):
        return pygame.mask.from_surface(self.img)  #Gives 2d list


class Pipe:
    gap = 200
    vel = 5
    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.pipe_top = pygame.transform.flip(pipe_img, False, True)
        self.pipe_bottom = pipe_img
        self.passed = False
        self.set_height()
    def set_height(self):
        self.height = random.randrange(14,450)
        self.top = self.height - self.pipe_top.get_height()
        self.bottom = self.height + self.gap
    def move(self):
        self.x -= self.vel
    def draw(self,win):
        win.blit(self.pipe_top, (self.x, self.top))
        win.blit(self.pipe_bottom, (self.x, self.bottom))
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.pipe_top)
        bottom_mask = pygame.mask.from_surface(self.pipe_bottom)
        
        #offset is dist b/w 2 objects
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)   # returns none if don't collide
        t_point = bird_mask.overlap(top_mask, top_offset)
        if(t_point or b_point):
            return True
        return False

def draw_window(win, birds, pipes, base, score,gen):
    win.blit(back_img, (0,0))  #Blit draws
    for pipe in pipes:
        pipe.draw(win)
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (win_width -10 - text.get_width(), 10))
    text = STAT_FONT.render("GEN: " + str(gen), 1, (255, 255, 255))
    win.blit(text, (10, 10))
    for bird in birds:
        bird.draw(win)
    pygame.display.update()

class Base:
    vel = 5
    width = base_img.get_width()
    img = base_img
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.width
    def move(self):
        self.x1 -= self.vel
        self.x2 -= self.vel
        if(self.x1 + self.width < 0):
            self.x1 = self.x2 + self.width
        if(self.x2 + self.width < 0):
            self.x2 = self.x1 + self.width
    def draw(self, win):
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))
        

def main(genomes, config):
    global GEN
    score  = 0
    GEN += 1
    nets = []
    gem = []
    birds = []
    for _,g in genomes:  #genomes is tupple
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        gem.append(g)
    base = Base(730)
    pipes = [Pipe(700)]
    run = True
    win = pygame.display.set_mode((win_width, win_height))
    clock = pygame.time.Clock()
    score = 0
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        pipe_see = 0
        if(len(birds) > 0):  # to check wether we want to see at the 2nd pipe or not when there 2 pipes at a time
            if (len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].pipe_top.get_width()):
                pipe_see = 1
        else:
            run = False
            break
        for x,bird in enumerate(birds):
            bird.move()
            gem[x].fitness += 0.1
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_see].height), abs(bird.y - pipes[pipe_see].height)))
            if output[0] > 0.5:   # o/p is a list
                bird.jump()
        add_pipe = False
        rem = []
        for pipe in pipes:
            for x,bird in enumerate(birds):  #new loop
                if(pipe.collide(bird)):
                    gem[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    gem.pop(x)
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            if(pipe.x + pipe.pipe_top.get_width() < 0):
                rem.append(pipe)
            pipe.move()
        if(add_pipe):
            score += 1
            for g in gem:
                g.fitness += 5
            pipes.append(Pipe(600))
        for r in rem:
            pipes.remove(r)
        for x,bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                gem.pop(x)
        base.move()
        draw_window(win, birds, pipes, base, score,GEN)
def run(config_path):
    #Loading file
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
        neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    #population
    p = neat.Population(config)
    #o/p we will see
    p.add_reporter(neat.StdOutReporter(True)) # gives report of each gen
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,50)  #using main as our fitness function


if __name__=='__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neatflappy.txt")
    run(config_path)

''' Basic neat-:
-> i/p - bird, top, and bottom pip
-> o/p - jump?
-> activtion function - tanh -1 to 1 if >0.5 jump
-> no. of population in each gen - 200 (100 random neural network will be for 100 then they will mutate them till perfect)
-> fitness function - the far you go, you get better(distance as a factor)(most imp how we are gonna get better evaluate how good our birds are)
-> max gen - here 30
'''

