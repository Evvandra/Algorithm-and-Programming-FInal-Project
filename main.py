import pygame
import time
import math
from utils import scale_image, blit_rotate_center, blit_text_center                         #to import function from another file(utils)
pygame.font.init()                                                                          # load the font n order to write text in pygame

GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)                               #to load the grass image and scale the image
TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.9)                               #load the track image and scale

TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)                 #load the track border and scale
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER) #use track border as a mask for colliding situation

FINISH = pygame.image.load("imgs/finish.png")                                               #load the finish line imahe
FINISH_MASK = pygame.mask.from_surface(FINISH) #create a finish mask
FINISH_POSITION = (130, 250)                                                                #indicate the position of the finist line

RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)                          #load the car(red) image
GREEN_CAR = scale_image(pygame.image.load("imgs/green-car.png"), 0.55)                      #load the car(green) image

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))                                              #the window/the screen size of the game is equal to the size of the track size
pygame.display.set_caption("Racing Game!")                                                  #set the title of the window

MAIN_FONT = pygame.font.SysFont("comicsans", 44)                                            #set the font of the text and the size of the font

FPS = 60
PATH = [(175, 119), (110, 70), (56, 133), (70, 481), (318, 731), (404, 680), (418, 521), (507, 475), (600, 551), (613, 715), (736, 713),
        (734, 399), (611, 357), (409, 343), (433, 257), (697, 258), (738, 123), (581, 71), (303, 78), (275, 377), (176, 388), (178, 260)]               # the computer car have to move based on this coordinates


class GameInfo:                                             # information about the game
    LEVELS = 10                                             # there will be 10 levels available in this game

    def __init__(self, level=1):                            #indicating the level starts from 1
        self.level = level
        self.started = False                                # indicating the current level has started  
        self.level_start_time = 0                           # to know how much time has elapsed in the level

    def next_level(self):                                   # to go to the next level
        self.level += 1                                     # add the level by 1, if the user win in the first level
        self.started = False                                # wait for the user to go to the next level

    def reset(self):                                        # to reset the position of the car for certain level 
        self.level = 1
        self.started = False
        self.level_start_time = 0

    def game_finished(self):                                # to know whether the user finish the game or no
        return self.level > self.LEVELS                     # if the current level is greater than the max level, then the user has win the game

    def start_level(self):                                  # to start the leve;
        self.started = True                                 # indicate that the level has started
        self.level_start_time = time.time()                 # keep in track when the level has started

    def get_level_time(self):
        if not self.started:
            return 0                                        # the time is still 0 if the level 
        return round(time.time() - self.level_start_time)   # calculate how much time has elapsed


class AbstractCar:                                          # class to move the car as we want                          
    def __init__(self, max_vel, rotation_vel):              # define the maximum velocity and rotation
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0                                        # initial speed/ the car is not moving from the start positiono
        self.rotation_vel = rotation_vel
        self.angle = 0                                      # the car is start from the angle of 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1                             # everytime the user pressed the W key, the velocity will be increase by 0.1

    def rotate(self, left=False, right=False):              # initialize the position of the angle of the car
        if left:
            self.angle += self.rotation_vel                 # if the car moving the left the angle is increasing
        elif right:
            self.angle -= self.rotation_vel                 # if the car rotate to the right, the angle is decreasing

    def draw(self, win): 
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):                                                             # increase the velocty of the car based on the acceleration
        self.vel = min(self.vel + self.acceleration, self.max_vel)                      # makesure the velocity won't exceed the maximum velocity
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)                   # to ensure that the max velocity when backwards is the half of the max velocity when going forward
        self.move()

    def move(self):                                                                     # function to move the car based on how we want
        radians = math.radians(self.angle)                                              # convert the angle into radians
        vertical = math.cos(radians) * self.vel 
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):                          # function when the car is colliding with the track or to the computer car
        car_mask = pygame.mask.from_surface(self.img)           
        offset = (int(self.x - x), int(self.y - y))             # substract the current x and y position with the x and y of the other mask which will give us the displacement
        poi = mask.overlap(car_mask, offset)                    # return the POI between two mask if there is one (poi = point of intersection)
        return poi

    def reset(self):                                            # reset the car prepairing for the next level
        self.x, self.y = self.START_POS                         # initialize the positin of the car before the race start
        self.angle = 0                                          # set the angle of the car
        self.vel = self.max_vel                                 # the car initially is not moving
        self.current_point = 0


class PlayerCar(AbstractCar):                                                               # this class inherits from AbstractCar
    IMG = RED_CAR                                                                           # define IMG and will be used in the AbstractCar
    START_POS = (180, 200)                                                                  # the position of the car where the user will start from there

    def reduce_speed(self):                                                                 # function to reduce the velocity by half if the user do prese any keys
        self.vel = max(self.vel - self.acceleration / 2, 0)                                 # to ensure if the value is negative, the car wont move backwars insted it will just stop there
        self.move()

    def bounce(self):                                                   # function to bounce when colliding with another object  
        self.vel = -self.vel                                            # reverse the velocity when colliding to another object
        self.move()                                                     # start moving when we reverse the velocti


class ComputerCar(AbstractCar):                                         # this class inherits from AbstractCar 
    IMG = GREEN_CAR                                                     # define the IMG and will be used as BOT to compete with the user
    START_POS = (150, 200)                                              # initialize the start position and makesure it starts at the same position as the user's car

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path                                                # the list of coordinates where the car should move to
        self.current_point = 0                                          # to know the path where the car at
        self.vel = max_vel                                              # the car will move at the maximum velocity all the time even from the start line

    def draw_points(self, win):                                         # to draw all the point of the path
        for point in self.path:    
            pygame.draw.circle(win, (255, 0, 0), point, 5)              # draw a red circle with the radius of 5

    def draw(self, win):
        super().draw(win)                                               # call the functin draw in the AbstractCar 

    def calculate_angle(self):                                          # calculate the angle to certain coordinates
        target_x, target_y = self.path[self.current_point]              # define the target x and y as the next coordinates
        x_diff = target_x - self.x                                      # calcultae the displacement of X
        y_diff = target_y - self.y                                      # calculate the displacement of Y

        if y_diff == 0:                                                 # the displacement of y = 0
            desired_radian_angle = math.pi / 2                          # the angle will be equal to 90
        else:
            desired_radian_angle = math.atan(x_diff / y_diff)           # the anggle will be tan-1(X/Y) which is the angle between the car(computer) and the point

        if target_y > self.y:               
            desired_radian_angle += math.pi                             # to make the car opposite direction since the result of the substraction is always an acute angle

        difference_in_angle = self.angle - math.degrees(desired_radian_angle)   # substract the current angle with the angle between the object and the point and whether its positive and negative it will indicate the object to move left or right
        if difference_in_angle >= 180:                                          # if the difference larger than 180
            difference_in_angle -= 360                                          # substract it with 360 to move to the opposite direction

        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))      # to makesure the car go towards the right angle without skipping it
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))      # to makesure the car go towards the right angle without skipping it

    def update_path_point(self):                                                # makesure the car go to the next point of the path
        target = self.path[self.current_point]                                  # define the target
        rect = pygame.Rect(
            self.x, self.y, self.img.get_width(), self.img.get_height())        # create a rectangle for the car using the x and y of the car
        if rect.collidepoint(*target):                                          # check if the car as passed the targetted point
            self.current_point += 1                                             # if the car already passed the point, set the next point as the target

    def move(self):                                                             # move the car based on the coordinates
        if self.current_point >= len(self.path):                                # to ensure there are no index error when the car dont move to the coordinates that doesn't exist
            return

        self.calculate_angle()                                          # calculate the angle and shift the car into that direction
        self.update_path_point()                                        # update the coordinates where the car have to move to that direction
        super().move()                                                  # call the move method in the AbstractCar's function

    def next_level(self, level):                                        # reset the car to be ready in the next level and increase the velocity
        self.reset()                                                    # reser the car in the start line
        self.vel = self.max_vel + (level - 1) * 0.2                     # define how fast the computer's car go in each levels          
        self.current_point = 0


def draw(win, images, player_car, computer_car, game_info):             # function to draw all the images into the window
    for img, pos in images:
        win.blit(img, pos)

    level_text = MAIN_FONT.render(
        f"Level {game_info.level}", 1, (255, 255, 255))                 # to write the level of the game and the color of the text
    win.blit(level_text, (10, HEIGHT - level_text.get_height() - 70))   # render the 'level' text based on the position

    time_text = MAIN_FONT.render(
        f"Time: {game_info.get_level_time()}s", 1, (255, 255, 255))     # to write the how much time has elapsed in the current level
    win.blit(time_text, (10, HEIGHT - time_text.get_height() - 40))     # render it into the window and placed it based on the position 

    vel_text = MAIN_FONT.render(
        f"Vel: {round(player_car.vel, 1)}px/s", 1, (255, 255, 255))     # to write the velocity of the user's car
    win.blit(vel_text, (10, HEIGHT - vel_text.get_height() - 10))       # render the 'velocity' text into the window

    player_car.draw(win)                                                # draw the user's car into the window and state the units which i px/s
    computer_car.draw(win)                                              # draw the computer car into the window
    pygame.display.update()


def move_player(player_car):                                            # function to move the car
    keys = pygame.key.get_pressed()  
    moved = False

    if keys[pygame.K_a]:
        player_car.rotate(left=True)                                    # if the user press [a] it will turn left
    if keys[pygame.K_d]:
        player_car.rotate(right=True)                                   # if the user press [d] it will turn right
    if keys[pygame.K_w]:
        moved = True
        player_car.move_forward()                                       # if the user press [w] it will move forward
    if keys[pygame.K_s]:
        moved = True
        player_car.move_backward()                                      # if the user press [s] it will move backward

    if not moved:
        player_car.reduce_speed()                                       # if the user don't press anything, the velocity will be reduced


def handle_collision(player_car, computer_car, game_info):              # if collision happens and it is for both user's and computer's car
    if player_car.collide(TRACK_BORDER_MASK) != None:                   # if the car collide with the track
        player_car.bounce()                                             # the car will bounce according to their function

    computer_finish_poi_collide = computer_car.collide(
        FINISH_MASK, *FINISH_POSITION)                                  # check if the computer's car passed the finish line
    if computer_finish_poi_collide != None:                             # if it's passed the finish line
        blit_text_center(WIN, MAIN_FONT, "You lost!")                   # display the text if the computer's car wins the game
        pygame.display.update()
        pygame.time.wait(5000)                                          # for delay the time in order to display the text
        game_info.reset()
        player_car.reset()                                              # reset the position of the user's car for the next level
        computer_car.reset()                                            # reset the position of the computer's car for the next level

    player_finish_poi_collide = player_car.collide(
        FINISH_MASK, *FINISH_POSITION)                                  # check if the user's car passed the finish line
    if player_finish_poi_collide != None:  
        if player_finish_poi_collide[1] == 0:                           # not allowing the car drive backwards so no cheating
            player_car.bounce()                                         # if the user try to drive instantly backwards to the finish line, the car will be bounce instead
        else:
            game_info.next_level()                                      # go to the next level
            player_car.reset()                                          # reset the position of the user's car for the next level
            computer_car.next_level(game_info.level)                    # change the speed of the computer's car for the next level


run = True
clock = pygame.time.Clock() 
images = [(GRASS, (0, 0)), (TRACK, (0, 0)),
          (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]                                # to load the images according to their scale
player_car = PlayerCar(4, 4)                                                                # define the velocity and the rotation velocity of the car
computer_car = ComputerCar(2, 4, PATH)                                                      # define the velocity and the rotation of the car and the car have to move based on the coordinates
game_info = GameInfo()                                                                      # define game info as the previous class name game info

while run:
    clock.tick(FPS)                                                                         # makesure that the while loop wont run faster than 60fps

    draw(WIN, images, player_car, computer_car, game_info)                                  # draw the object into the window

    while not game_info.started:
        blit_text_center(
            WIN, MAIN_FONT, f"Press any key to start level {game_info.level}!")             # to display the text that we want using the function from 'utils'
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:                                                   # if the user click the exit(X) button in the screen
                pygame.quit()                                                               # to quit the pygame
                break

            if event.type == pygame.KEYDOWN:                                                # if the user press any key down
                game_info.start_level()                                                     # the level will start eventually

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    move_player(player_car)                                                                 # so we can move the car
    computer_car.move()                                                                     # to make the computer's car move

    handle_collision(player_car, computer_car, game_info)

    if game_info.game_finished():
        blit_text_center(WIN, MAIN_FONT, "You won the game!")                               # display the text if the user has win the game
        pygame.time.wait(5000)                                                              # for time delay in order to display the game
        game_info.reset()                                                                   # restart the game
        player_car.reset()
        computer_car.reset()


pygame.quit()
