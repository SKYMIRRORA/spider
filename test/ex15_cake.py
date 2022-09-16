import turtle 
import math
import random

def drawX(a, i):
    angle = math.radians(i)
    return a * math.cos(angle)
 
def drawY(b, i):
    angle = math.radians(i)
    return b * math.sin(angle)
# turtle.setup(width,height,startx,starty)
turtle.setup(800,600,400,300)
turtle.goto(100,100)
turtle.goto(100,-100)
turtle.goto(-100,-100)
turtle.goto(-100,100)
turtle.goto(0,0)
turtle.fillcolor('yellow')
turtle.pencolor('pink')
turtle.begin_fill()
# turtle.circle(r,angle)
turtle.circle(100,360)
#当前距离后退
turtle.bk(100)
#当前距离前进
turtle.fd(100)
#seth()改变海龟行进方向；
#angle为据对度数；
#seth()只改变呢方向但是不行进
# turtle.seth(angle)
turtle.seth(30)
turtle.fd(100)
turtle.right(30)

turtle.left(30)
turtle.fd(100)
turtle.colormode('tomato')
turtle.fd(100)
# turtle.setup(100,)
#海龟飞起
turtle.penup()
turtle.goto(-100,0)
#海龟落下
turtle.pendown()

#设置填充颜色
turtle.fillcolor("#f1add1")
#海龟写字
turtle.write("hello world", font=("Curlz MT", 50))
turtle.done()

# screen = turtle.Screen()
# turtle.forward(100)
# turtle.mainloop()









