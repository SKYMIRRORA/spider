import turtle
import math
import time


def draw_arc(width,lenght,angle):
    rad = math.radians(angle)
    x = width * math.cos(rad)
    y = lenght * math.sin(rad)
    return x,y
# for angle in range(180):
#     x,y = draw_arc(100,70,angle)
#     turtle.goto(x,-y)

def draw_spiral():
    for x in range(360):
        turtle.forward(x)
        turtle.left(59)

def draw_flower():
    for i in range(6):
        for j in range(2):
            for k in range(90):
                turtle.forward(1) 
                turtle.right(1)
            turtle.right(90)
        turtle.right(60)


turtle.setup(800,600,400,300)
turtle.pencolor('black')
turtle.fillcolor('pink')
turtle.begin_fill()
# turtle.forward(100)
# turtle.goto(100,100)
# turtle.goto(-100,100)
# turtle.goto(-100,0)
# turtle.goto(0,0)
#画圆，角度，弧度，边
# turtle.circle(100,90,3)

# draw_flower()
draw_spiral()
turtle.end_fill()

#
# turtle.delay(1000)
turtle.done()









