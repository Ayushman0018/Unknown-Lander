import pygame
import os
import random
import sys
pygame.init()
pygame.joystick.init()
pygame.mixer.init()

gscreen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Nuclear - The Game")
screen_width, screen_height = gscreen.get_rect().size
red_overlay = pygame.Surface((screen_width, screen_height))
red_overlay.fill((255,0,0))
if pygame.joystick.get_count() > 0:
    remote = pygame.joystick.Joystick(0)
    remote.init()
def im(image_name, sx, sy):
    img = pygame.image.load(image_name).convert_alpha()
    img = pygame.transform.scale(img, (sx, sy))
    return img

animation_disk = {
    'lava_animation' : [[200,200]],
    'laser':[[150, 800]],
    'ufo':[[200,150]],
    'flames':[[1000, 500]],
    "blast":[[230, 170]]
}

def text_plot(text, color, size, x, y, position=""):
    font = pygame.font.SysFont(None, size)
    blz = font.render(text, True, color)
    if position == "screencenter":
        bx, by = blz.get_rect().size
        x = align(screen_width, bx)
        y = align(screen_height, by)
    gscreen.blit(blz, [x, y])

def align(field, length, pad=0):
    return ((field-length)//2)+pad

def gameover():
    white = (255,255,255)
    red = (255,0,0)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                gameloop()
        text_plot("Game Over! Click anywhere to play again.", red, 60, 0, 0, "screencenter")
        pygame.display.update()

def gameloop():
    animations = []
    clock = pygame.time.Clock()
    counter = 0
    risk_counter = 0
    fps = 32
    towers = []
    black = (0,0,0)
    score = 0
    victory_trigger = 100
    vel_counter = 0
    alpha_vel = 10
    victory = False
    alpha_value = 1
    risk = False
    fire_cooldown = 0
    loading_screen = im("loading_screen.webp", screen_width, screen_height)
    gscreen.blit(loading_screen, [0, 0])
    pygame.display.update()
    last_vel_x = 5
    vel_x = 5
    pygame.mixer.music.load("audio/ufo.mp3")
    blast = pygame.mixer.Sound("audio/explosion.mp3")
    explosion = pygame.mixer.Sound("audio/big_explosion.mp3")
    red = (255,0,0)
    beep = pygame.mixer.Sound("audio/beep.mp3")
    beep.set_volume(0.5)
    recharge = pygame.mixer.Sound("audio/recharge.mp3")
    victory_sound = pygame.mixer.Sound("audio/victory.mp3")
    defeat = pygame.mixer.Sound("audio/defeat.mp3")
    a = os.listdir("lava_animation/")
    for i in a:
        if i[-3:] == "png":
            animation_disk['lava_animation'].append(im(f"lava_animation/{i}", 200, 200))

    a = os.listdir("ufo/")
    for i in a:
        if i[-3:] == "png":
            animation_disk['ufo'].append(im(f"ufo/{i}", 200, 150))
    a = os.listdir("laserbeam/")
    for i in a:
        if i[-3:] == "png":
            animation_disk['laser'].append(im(f"laserbeam/{i}", 550, 800))
    a = os.listdir("flames/")
    for i in a:
        if i[-3:] == "png":
            animation_disk['flames'].append(im(f"flames/{i}", 1000, 500))
    a = os.listdir("blast/")
    for i in a:
        if i[-3:] == "png":
            animation_disk['blast'].append(im(f"blast/{i}", 230, 170))
    class user:
        def __init__(self):
            self.x = 150
            self.y = 50
            self.over = False
            self.victory = False
    player = user()
    class tower:
        def __init__(self, x, y, imagename):
            self.x = x
            self.y = y
            self.imagename = imagename
            self.health = 400
            self.image = im(self.imagename, 100, self.health)
            towers.append(self)
        def destruct(self):
            self.health -= 50
            if self.health <= 0:
                del towers[towers.index(self)]
            else:
                self.image = pygame.transform.scale(self.image, (100, self.health))
                self.y = screen_height-self.health
        def animate(self):
            gscreen.blit(self.image, [self.x, self.y])
    class animation:
        def __init__(self, sequence_name, sx, sy, x, y, obj, extension='jpg', animation_type="one_time", position="dynamic", retract = 20):
            self.sequence_name = sequence_name
            a = os.listdir(self.sequence_name)
            self.frames = []
            self.counter = 0
            self.obj = obj
            self.x = x
            self.first_x = obj.x
            self.first_y = obj.y
            self.position = position
            self.animation_type = animation_type
            self.y = y
            self.frame_velocity = 1
            self.retract = retract
            self.sx, self.sy = animation_disk[self.sequence_name][0]
            self.frames = list(animation_disk[self.sequence_name][1:])
            self.counter_limit = len(self.frames)
            #print(self.counter_limit)
            animations.append(self)
        def animate(self):
            if self.position == "dynamic":
                position = [self.obj.x + self.x, self.obj.y + self.y]
            else:
                position = [self.first_x+self.x, self.first_y+self.y]
            if self.sequence_name == "ufo":
                if self.obj.over == True:
                    del animations[animations.index(self)]
            if self.sequence_name in ['flames', 'lava_animation'] and self.obj.health <= 0:
                del animations[animations.index(self)]
            if self.animation_type == "one_time_delete":
                gscreen.blit(self.frames[self.counter], position)
                if self.counter >= self.counter_limit-1:
                    del animations[animations.index(self)]
                else:
                    self.counter += 1
            if self.animation_type == "one_time":
                gscreen.blit(self.frames[self.counter], position)
                if self.counter >= self.counter_limit-1:
                    pass
                else:
                    self.counter += 1
            elif self.animation_type == "reverse_loop":
                gscreen.blit(self.frames[self.counter], position)
                self.counter += self.frame_velocity
                if self.counter >= self.counter_limit-1:
                    self.frame_velocity = -1
                elif self.counter <= 0:
                    self.frame_velocity = 1
            elif self.animation_type == "loop":
                gscreen.blit(self.frames[self.counter], position)
                self.counter += 1
                if self.counter >= self.counter_limit-1:
                    self.counter = 0
            elif self.animation_type == "no_end":
                gscreen.blit(self.frames[self.counter], position)
                self.counter += 1
                # #print(self.counter, self.counter_limit)
                if self.counter >= self.counter_limit-1:
                    self.counter -= self.retract
    # animation("lava_animation", 200, 200, 0, 0, animation_type="one_time")
    background = im("background.png", screen_width, screen_height)
    animation("ufo", 200, 150, 0, 0, player, animation_type="loop", extension="png")
    for i in range(200, screen_width-200, 300):
        tower(i, screen_height-400, "pole1.png")
    # tower(300, screen_height-400, "pole1.png")
    pygame.mixer.music.play(loops=-1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.JOYBUTTONDOWN:
                if victory == "VERDICT":
                    gameloop()
                if fire_cooldown == 0:
                    fire_cooldown = 130
                    # print("JOYBUTTON")
                    explosion.play()
                    score += 5
                    animation('laser', 150, 800, -170, 70, player, extension="png", position="static", animation_type="one_time_delete")
                    last_vel_x = vel_x
                    vel_x = 0
                    vel_counter = 0
                    for tow in towers:
                        if abs((player.x+100) - (tow.x+50)) < 50:
                            animation("lava_animation", 200, 200, -50, 0, tow, extension="png", animation_type="one_time")
                            if tow.health == 400:
                                animation('flames', 1000, 500, -390, -450, tow, extension="png", animation_type="no_end", retract=50)
                            tow.destruct()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE and victory == "VERDICT":
                    gameloop()
                if event.key == pygame.K_SPACE and fire_cooldown == 0:
                    fire_cooldown = 130
                    explosion.play()
                    score += 5
                    animation('laser', 150, 800, -170, 70, player, extension="png", position="static", animation_type="one_time_delete")
                    last_vel_x = vel_x
                    vel_x = 0
                    vel_counter = 0
                    for tow in towers:
                        if abs((player.x+100) - (tow.x+50)) < 50:
                            animation("lava_animation", 200, 200, -50, 0, tow, extension="png", animation_type="one_time")
                            if tow.health == 400:
                                animation('flames', 1000, 500, -390, -450, tow, extension="png", animation_type="no_end", retract=50)
                            tow.destruct()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                #print(f"X: {mx}  Y: {my}")
        gscreen.blit(background, [0, 0])
        if victory == True:
            if abs(player.x - screen_width//2) > 100:
                player.x += ((screen_width//2 - player.x)/100)*10
            elif player.y < screen_height-200:
                player.y += 10
                vel_x = 0
            else:
                player.victory = True
                victory = "VERDICT"
        if player.over == False and not victory in [True, 'VERDICT'] :
            player.x += vel_x
        for i in towers:
            if abs((player.x+100) - (i.x+50)) < 50 and abs(player.y-i.y) < 100 and player.over == False:
                animation("blast", 230, 170, 0, 0, player, extension="png", animation_type="one_time_delete")
                #print("I played explosion")
                beep.stop()
                blast.set_volume(1)
                blast.play()
                player.over = True
            elif abs(player.y-i.y) < 200 and player.over == False and abs(player.y-i.y) > 100 and risk_counter == 0 and victory != True and victory != "VERDICT":
                beep.play()
                risk_counter = 50
                risk = True
        if player.over == True:
            counter += 1
        if counter > 100:
            defeat.play()
            gameover()
        leftgame = 0
        for i in towers:
            leftgame += i.health
        if leftgame <= 0 and not victory in [True, 'VERDICT']:
            victory_trigger -= 1
            if victory_trigger <= 0:
                victory = True
                pygame.mixer.music.stop()
                victory_sound.play()
        if fire_cooldown > 0:
            fire_cooldown -= 1
        if fire_cooldown == 70 and leftgame > 0:
            recharge.play()
        if vel_x == 0:
            vel_counter += 1
            if vel_counter >= 100:
                vel_x = last_vel_x
        if player.x > screen_width-200 or player.x <= 50:
            if abs(vel_x) > 10:
                if vel_x < 0:
                    vel_x -= 2
                else:
                    vel_x += 2
            vel_x *= -1
            player.y += 50
        for i in towers:
            i.animate()
            # pygame.draw.rect(gscreen, black, [i.x+50, 0, 2, screen_height])
        for i in animations:
            i.animate()
        if victory == "VERDICT":
            risk = False
            text_plot(f"Congratulations, You Won! Score: {score}, Press SPACE to restart.", red, 90, 0, 0, position="screencenter")
        if risk == True:
            risk_counter -= 1
            alpha_value += alpha_vel
            if alpha_value < 1:
                alpha_vel = 10
                alpha_value = 1
            elif alpha_value > 149:
                alpha_vel = -10
                alpha_value = 149
            red_overlay.set_alpha(alpha_value)
            gscreen.blit(red_overlay, [0, 0])
        pygame.draw.rect(gscreen, black, [8, 38, 132*2, 24])
        pygame.draw.rect(gscreen, (255,0,0), [10, 40, fire_cooldown*2, 20])
        text_plot(f"Score: {score}", red, 40, 10,10)
        pygame.display.update()
        clock.tick(fps)
gameloop()