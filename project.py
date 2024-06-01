from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import os
import math


#constants and initial values
WIDTH, HEIGHT = 600, 800
BACKGROUND_COLOR = 0.0, 0.0, 0.0, 1.0


ship_angle = 0
ship_x = WIDTH / 2
ship_y = HEIGHT / 2
SHIP_SIZE = 20


bullets = []


red_rgb = 1.0, 0.0, 0.0
green_rgb = 0.0, 1.0, 0.0
blue_rgb = 0.0, 0.0, 1.0
yellow_rgb = 1.0, 1.0, 0.0




run = True
gameplay = True
POINT = 0
lifes = 3




#circle_points, draw_points, draw_circle and drawLine algorithms
def draw_points(x, y, size):
    glPointSize(size)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()








def draw_circle(xc, yc, radius, size):
    glPointSize(size)
    glBegin(GL_POINTS)




    x = 0
    y = radius
    d = 1 - radius




    while x < y:
        if d < 0:  # choose east
            d = d + 2 * x + 3
            x = x + 1
        else:  # choose southeast
            d = d + 2 * (x - y) + 5
            x = x + 1
            y = y - 1
        circle_points(xc, yc, x, y)




    glEnd()




def circle_points(xc, yc, x, y):
    glVertex2f(xc + x, yc + y)
    glVertex2f(xc + y, yc + x)
    glVertex2f(xc + y, yc - x)
    glVertex2f(xc + x, yc - y)
    glVertex2f(xc - x, yc - y)
    glVertex2f(xc - y, yc - x)
    glVertex2f(xc - y, yc + x)
    glVertex2f(xc - x, yc + y)








def findZone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx >= 0 and dy >= 0:
        if dx >= dy:
            return 0
        else:
            return 1
    elif dx < 0 and dy >= 0:
        if -dx >= dy:
            return 3
        else:
            return 2
    elif dx < 0 and dy < 0:
        if dx <= dy:
            return 4
        else:
            return 5
    elif dx >= 0 and dy < 0:
        if dx >= -dy:
            return 7
        else:
            return 6




def toZoneZero(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return y, -x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return -y, x
    elif zone == 7:
        return x, -y




def drawLine(x1, y1, x2, y2, size):
    zone = findZone(x1, y1, x2, y2)
    x1, y1 = toZoneZero(x1, y1, zone)
    x2, y2 = toZoneZero(x2, y2, zone)
    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    de = 2 * dy
    dne = 2 * (dy - dx)
    x = x1
    y = y1
    while x <= x2:
        real_x, real_y = toZoneZero(x, y, zone)
        draw_points(real_x, real_y, size)
        if d <= 0:
            d = d + de
            x = x + 1
        else:
            d = d + dne
            x = x + 1
            y = y + 1




def drawLeftArrow(size):
    drawLine(25, 750, 75, 750, size)
    drawLine(25, 750, 50, 775, size)
    drawLine(25, 750, 50, 725, size)




def cross(size):
    drawLine(525, 725, 575, 775, size)
    drawLine(575, 725, 525, 775, size)




def play(size):
    drawLine(280, 725, 280, 775, size)
    drawLine(280, 775, 325, 750, size)
    drawLine(280, 725, 325, 750, size)




def pause(size):
    drawLine(280, 725, 280, 775, size)
    drawLine(320, 725, 320, 775, size)




#Bullets
class Projectile:
    def __init__(self, x, y, radius, speed, size, angle):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.size = size
        self.angle = angle
        self.color = (random.random(), random.random(), random.random())




    def draw(self):
        draw_circle(self.x, self.y, self.radius, self.size)




    def move(self):
        speed = 5
        self.x += speed * math.cos(math.radians(self.angle))
        self.y += speed * math.sin(math.radians(self.angle))




    def checkCollision(self, bubbles):
        distance = math.sqrt((self.x - bubbles.x) ** 2 + (self.y - bubbles.y) ** 2)
        if distance <= self.radius + bubbles.radius:
            return True
        return False




    def update(self):
        self.move()
        glColor3f(*self.color)
        self.draw()




projectile = None
projectile_speed = 5


#bubble object
class Bubble:
    def __init__(self, x, y, w, h, speed, size):
        self.x = x
        self.y = y
        self.radius = w / 2
        self.size = size
        self.speed = speed
        self.color = (random.random(), random.random(), random.random())


        # Determine horizontal direction based on spawn position
        if self.x < WIDTH / 2:  # Spawned on the left side
            self.horizontal_direction = 1  # Move right
        else:  # Spawned on the right side
            self.horizontal_direction = -1  # Move left


        # Determine vertical direction based on spawn position
        if self.y < HEIGHT / 2:  # Spawned on the bottom side
            self.vertical_direction = 1  # Move up
        else:  # Spawned on the top side
            self.vertical_direction = -1  # Move down


    def draw(self):
        draw_circle(self.x, self.y, self.radius, self.size)




    def move(self):
        self.x += self.horizontal_direction * self.speed  # Move horizontally based on direction
        self.y += self.vertical_direction * self.speed
        self.wrap_around()


    def wrap_around(self):
        if self.x < 0:
            self.x = WIDTH
        elif self.x > WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = HEIGHT
        elif self.y > HEIGHT:
            self.y = 0


    def checkCollision(self, bowl):
        distance = math.sqrt((self.x - bowl.x) ** 2 + (self.y - bowl.y) ** 2)
        if distance <= self.radius + bowl.radius:
            self.radius = random.randint(50,250)
            return True
        return False






    def update(self):
        self.move()
        glColor3f(*self.color)
        self.draw()






#rocket object
class Bowl:
    def __init__(self, x, y, radius, speed, size):
        self.x = x
        self.y = y
        self.radius = radius
        self.size = size
        self.speed = speed
        self.color = 1.0, 1.0, 0.0




    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.x, 0)
        glRotatef(ship_angle, 0, 0, 1)
        glColor3f(1, 1, 1)
        drawLine(-SHIP_SIZE / 2, -SHIP_SIZE / 2, SHIP_SIZE / 2, 0, self.size)
        drawLine(-SHIP_SIZE / 2, -SHIP_SIZE / 2, -SHIP_SIZE / 2, SHIP_SIZE / 2, self.size)
        drawLine(-SHIP_SIZE / 2, SHIP_SIZE / 2, SHIP_SIZE / 2, 0, self.size)
        glPopMatrix()


    def wrap_around(self):
        if self.x < 0:
            self.x = WIDTH
        elif self.x > WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = HEIGHT
        elif self.y > HEIGHT:
            self.y = 0
   
    def checkCollision(self, bubble):
        distance = math.sqrt((self.x - bubble.x) ** 2 + (self.y - bubble.y) ** 2)
        if distance <= self.radius + bubble.radius:
            return True
        return False


    def update(self):
        self.wrap_around()
        glColor3f(*self.color)
        self.draw()








# initial bubbles
num_bubbles = 5
bubbles_list = []
bubbles_speed_limit = 2
for _ in range(num_bubbles):
    # Randomly choose spawn position and direction
    bubbles_speed = 0.5
    spawn_x = random.randint(25, WIDTH - 25)
    spawn_y = random.randint(25, HEIGHT - 25)
    horizontal_direction = random.choice([-1, 1])
    vertical_direction = random.choice([-1, 1])
    speed = random.uniform(0.1, bubbles_speed_limit)
    bubble = Bubble(spawn_x, spawn_y, random.randint(20,60), 50, speed, 2)
    bubble.horizontal_direction = horizontal_direction
    bubble.vertical_direction = vertical_direction
    bubbles_list.append(bubble)




# initial rocket
bowl_x = WIDTH // 2
bowl_y = 50
bowl_radius = 0.2
bowl_speed = 5
bowl_speed_limit = 10
bowl = Bowl(bowl_x, bowl_y, bowl_radius, bowl_speed, 2)




#gameplay function
def gamePlay():
    global bubbles_list, projectile, run, POINT, bowl, lifes, bullets
    for bubble in bubbles_list:
        if projectile:
            if bubble.checkCollision(projectile):
                POINT += 1  # Increase the score by 1
                print("Score: ", POINT)
                bubble.x = random.randint(50, WIDTH - 50)
                bubble.y = HEIGHT - 50
                bubble.color = (random.random(), random.random(), random.random())
                projectile = None  # Reset the projectile after scoring
                if bubbles_speed <= bubbles_speed_limit:
                    bubble.speed += 0.1
                if bowl.speed <= bowl_speed_limit:
                    bowl.speed += 0.3


            elif bowl.checkCollision(bubble):
                lifes -= 1
                bubble.x = random.randint(50, WIDTH - 50)
                bubble.y = HEIGHT - 50
                bubble.color = (random.random(), random.random(), random.random())
                if bubbles_speed <= bubbles_speed_limit:
                    bubble.speed += 0.1
                if bowl.speed <= bowl_speed_limit:
                    bowl.speed += 0.3
                bubbles_list.remove(bubble)
                if lifes <= 0:
                    print("Game Over")
                    print("Overall Score: ", POINT)
                    run = False
                    bowl.color = red_rgb
           
    for bubble in bubbles_list:
        bubble.update()
   
    glutPostRedisplay()
    #glutTimerFunc(10, gamePlay, 0)






#Keyboard functions
def keyPressed(key, x, y):
    global bowl, run, projectile, ship_angle, ship_x, ship_y, bullets
    if run and gameplay:
        if key == b'w':
            ship_x += 5 * math.cos(math.radians(ship_angle))
            bowl.x += 5 * math.cos(math.radians(ship_angle)) + bowl.speed
            ship_y += 5 * math.sin(math.radians(ship_angle))
            bowl.y += 5 * math.sin(math.radians(ship_angle)) + bowl.speed
        elif key == b's':
            ship_x -= 5 * math.cos(math.radians(ship_angle))
            bowl.x -= 5 * math.cos(math.radians(ship_angle)) + bowl.speed
            ship_y -= 5 * math.sin(math.radians(ship_angle))
            bowl.y -= 5 * math.sin(math.radians(ship_angle)) + bowl.speed
        if key == b"a":
            ship_angle += 5
        if key == b"b":
            bowl.speed += 0.5  
        elif key == b"d":
            ship_angle -= 5
                 
        elif key == b" ":  # Spacebar
            if projectile is None:  # Shoot only if there is no existing projectile
                projectile = Projectile(ship_x, ship_y, 2, projectile_speed, 2, ship_angle)








def mouseClick(button, state, x, y):
    global run, gameplay, POINT
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if x >= 250 and x <= 350 and y >= 0 and y <= 100 and run:
            gameplay = not gameplay
            if not gameplay:
                print("Paused")
        elif x >= 0 and x <= 100 and y >= 0 and y <= 100:
            print("Restart")
            reset()
        elif x >= 500 and x <= 600 and y >= 0 and y <= 100:
            run = False
            gameplay = False
            print("Goodbye")
            print("Overall Score: ", POINT)
            glutLeaveMainLoop()
            os._exit(0)






#reset function
def reset():
    global run, gameplay, POINT, bubbles_speed, projectile, lifes
    run = True
    gameplay = True
    POINT = 0
    lifes = 3
    # reset bubbles
    for _ in range(5):
        bubbles_speed = 0.5
        spawn_x = random.randint(25, WIDTH - 25)
        spawn_y = random.randint(25, HEIGHT - 25)
        horizontal_direction = random.choice([-1, 1])
        vertical_direction = random.choice([-1, 1])
        speed = random.uniform(0.1, bubbles_speed_limit)
        bubble = Bubble(spawn_x, spawn_y, random.randint(20, 60), 50, speed, 2)
        bubble.horizontal_direction = horizontal_direction
        bubble.vertical_direction = vertical_direction
        bubbles_list.append(bubble)


    # reset bowl
    bowl.x = WIDTH // 2
    bowl.y = 50
    bowl.radius = 0.2
    bowl.speed = 5
    bowl.color = 1.0, 1.0, 1.0




    # Reset Projectile
    projectile = None








def iterate():
    glViewport(0, 0, WIDTH, HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, WIDTH, 0.0, HEIGHT, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()






#display function
def showScreen():
    global run, bubbles_speed, bubbles, bowl, projectile, bullets
    glClearColor(*BACKGROUND_COLOR)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()


    for bullet in bullets:
        bullet.draw()
    #UI Elements
    glColor3f(*green_rgb)
    drawLeftArrow(2)




    if gameplay:
        glColor3f(*yellow_rgb)
        pause(2)  # pause
    else:
        glColor3f(*blue_rgb)
        play(2)  # play




    glColor3f(*red_rgb)
    cross(2)  # cross




    if run:
        if gameplay:
            gamePlay()
        else:
            for bubble in bubbles_list:
                bubble.draw()
        bowl.update()
        if projectile is not None:
            if projectile.y > HEIGHT or projectile.y < 0 or projectile.x < 0 or projectile.x > WIDTH  :
                projectile = None  # Reset projectile if it goes out of screen
            else:
                projectile.update()




    glutSwapBuffers()








def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA)
    glutInitWindowSize(WIDTH, HEIGHT)  # window size
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Asteroid Clone!")  # window name
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glutDisplayFunc(showScreen)
    glutIdleFunc(gamePlay)
    glutKeyboardFunc(keyPressed)
    glutMouseFunc(mouseClick)
    glutMainLoop()






if __name__ == "__main__":
    main()
