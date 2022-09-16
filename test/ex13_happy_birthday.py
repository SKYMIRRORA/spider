from tkinter import *
from tkinter import messagebox
root = Tk()#创建主窗口对象
root.title('送给小可爱')
root.geometry('800x280+100+200')
btn01 = Button(root,bg='pink')#创建按钮
btn01['text'] = '惊喜1'
btn01.pack(side='left',padx='19')
btn02 = Button(root)#创建按钮
btn02['text'] = '惊喜2'
btn02['bg'] = 'pink'
btn02.pack(side='left',padx='19')
btnQuit = Button(root, text="退出", command=root.destroy)#t退出按钮
btnQuit['bg'] = 'pink'
btnQuit.pack(side='left',padx='19')
photo = PhotoImage(file='xxxxx.png')#显示图片
label01 = Label(root,text='to sijia',image=photo)
label01.pack()
def birthword(e):     #e为事件对象
    messagebox.showinfo('Message','生日快乐 星星是银河递给月亮的情书 你是世界赠与我的恩赐')
def birthpic(e):    
    messagebox.showinfo('Message', \
        '大海或许真的是最爱小鲤鱼的吧，因为它帮小鲤鱼实现了天天念叨的愿望。你看小鲤鱼天天blue blue blue的，大海就把自己都变成了蓝色了喔。')
btn01.bind('<Button-1>',birthword)    #绑定事件
btn02.bind('<Button-1>',birthpic)     #绑定事件
root.mainloop()     #调用组件的mainloop方法，进入事件循环