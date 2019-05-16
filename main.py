# -*- coding:utf-8 -*-
import os
import time
import tkinter
import tkinter.filedialog
from multiprocessing import Process, Queue, Manager
from time import sleep

import mss
import pandas as pd
import pytesseract
import xlwt
from PIL import Image
from PIL import ImageGrab
from pyecharts import options as opts
from pyecharts.charts import Line


class MyCapture:
    def __init__(self, png):
        # 变量X和Y用来记录鼠标左键按下的位置
        self.X = tkinter.IntVar(value=0)
        self.Y = tkinter.IntVar(value=0)
        self.selectPosition = None
        # 屏幕尺寸
        screenWidth = root.winfo_screenwidth()
        # print(screenWidth)
        screenHeight = root.winfo_screenheight()
        # print(screenHeight)
        # 创建顶级组件容器
        self.top = tkinter.Toplevel(root, width=screenWidth, height=screenHeight)
        # 不显示最大化、最小化按钮
        self.top.overrideredirect(True)
        self.canvas = tkinter.Canvas(self.top, bg='white', width=screenWidth, height=screenHeight)
        # 显示全屏截图，在全屏截图上进行区域截图
        self.image = tkinter.PhotoImage(file=png)
        self.canvas.create_image(screenWidth // 2, screenHeight // 2, image=self.image)

        # 鼠标左键按下的位置
        def onLeftButtonDown(event):
            self.X.set(event.x)
            self.Y.set(event.y)
            # 开始截图
            self.sel = True

        self.canvas.bind('<Button-1>', onLeftButtonDown)

        # 鼠标左键移动，显示选取的区域
        def onLeftButtonMove(event):
            if not self.sel:
                return
            global lastDraw
            try:
                # 删除刚画完的图形，要不然鼠标移动的时候是黑乎乎的一片矩形
                self.canvas.delete(lastDraw)
            except Exception as e:
                pass
            lastDraw = self.canvas.create_rectangle(self.X.get(), self.Y.get(), event.x, event.y, outline='red')

        self.canvas.bind('<B1-Motion>', onLeftButtonMove)

        # 获取鼠标左键抬起的位置，保存区域截图
        def onLeftButtonUp(event):
            self.sel = False
            try:
                self.canvas.delete(lastDraw)
            except Exception as e:
                pass
            sleep(0.1)
            # 考虑鼠标左键从右下方按下而从左上方抬起的截图
            myleft, myright = sorted([self.X.get(), event.x])
            mytop, mybottom = sorted([self.Y.get(), event.y])
            self.selectPosition = (myleft, myright, mytop, mybottom)
            self.top.destroy()

        self.canvas.bind('<ButtonRelease-1>', onLeftButtonUp)
        self.canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)


#  将数据写入新EXCEL文件
def data_write(file_path, datas):
    f = xlwt.Workbook()
    sheet1 = f.add_sheet(u'sheet1', cell_overwrite_ok=True)  # 创建sheet

    # 将数据写入第 i 行，第 j 列
    i = 0
    for data in datas:
        for j in range(len(data)):
            sheet1.write(i, j, data[j])
        i = i + 1

    f.save(file_path)  # 保存文件


def buttonCaptureClick():
    # 最小化主窗口
    # root.state('icon')
    # sleep(0.2)
    filename = 'temp.png'
    im = ImageGrab.grab()
    im.save(filename)
    im.close()
    # 显示全屏幕截图
    w = MyCapture(filename)
    buttonCapture.wait_window(w.top)
    lista.insert('end', str(w.selectPosition))
    global fullbuttom, fullleft, fullright, fulltop, shuju
    print(w.selectPosition)
    area.append(w.selectPosition)
    # 计算最大需要截图区域
    for item in area:
        # print(item[0])
        fullleft = item[0] if fullleft > item[0] else fullleft
        fulltop = item[2] if fulltop > item[2] else fulltop
        fullright = item[1] if fullright < item[1] else fullright
        fullbuttom = item[3] if fullbuttom < item[3] else fullbuttom
        print(fullleft, fulltop, fullright, fullbuttom)
    # 截图结束，恢复主窗口，并删除临时的全屏幕截图文件

    root.state('normal')
    os.remove(filename)


def grab(queue, fullleft, fulltop, fullright, fullbuttom, Interval=0.2, numbers=10, ):
    monitor = {"top": fulltop, "left": fullleft, "width": fullright - fullleft, "height": fullbuttom - fulltop}
    with mss.mss() as sct:
        for i in range(numbers):
            queue.put(sct.grab(monitor))
            sleep(Interval)
    queue.put(None)


def identify(queue, queue1, area, fullleft, fulltop, fullright, fullbuttom, code1):

    shuju = []
    i = 0

    # 计算截图后的有效数据区域
    for item in area:
        shuju.append((item[0] - fullleft, item[2] - fulltop, item[1] - fullleft, item[3] - fulltop))

    while "there are identify":

        img = queue.get()
        if img is None:
            break
        img1 = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
        m = 0
        code = []
        code.append(i)
        # 识别每个选择区域的数据
        for item in shuju:
            region = img1.crop(item)
            if m == 0:
                code.append(pytesseract.image_to_string(region, config='-psm 7 sfz', lang='new'))
                m = m + 1
            else:
                code.append(pytesseract.image_to_string(region, config='-psm 7 sfz', lang='new'))
                m = 0
        # 判断有不相等的对比组存图
        for x, y in zip(code[1::2], code[2::2]):
    
            if x != y:
                queue1.put(img1)

        code1.append(code)
        print(code)
        i = i + 1
    queue1.put(None)


def saveData(queue1, outpanth):
    while "there are screenshots":
        img = queue1.get()
        if img is None:
            break
        
        ct = time.time()
        local_time = time.localtime(ct)
        data_secs = int((ct - int(ct)) * 1000)
        filepath = outpanth + str(local_time.tm_hour) + str(local_time.tm_min) + str(local_time.tm_sec) + str(
            data_secs) + ".png"
        img.save(filepath)


def buttonzhuatu():
    global area, fullleft, fulltop, fullright, fullbuttom, code1
    global queue, queue1, p1, p2, p3
    if area:
        local_time = time.localtime(time.time())
        outpath = r"./" + str(local_time.tm_hour) + str(local_time.tm_min) + r"/"
        if not os.path.exists(outpath):
            os.mkdir(outpath)
        queue = Queue()
        queue1 = Queue()
        p1 = Process(target=grab, args=(queue, fullleft, fulltop, fullright, fullbuttom))
        p1.start()
        p2 = Process(target=identify, args=(queue, queue1, area, fullleft, fulltop, fullright, fullbuttom, code1))
        p2.start()
        p3 = Process(target=saveData, args=(queue1, outpath))
        p3.start()
    else:
        print("至少选定两个有效区域")


def chartCreat(code3):
    j = 0
    print(code3)
    dfObj = pd.DataFrame(list(code3))
    
    while "huantu":
        try:
            ddf = dfObj.iloc[:, [0, j + 1, j + 2]].drop_duplicates([j + 1, j + 2])
            templist = ddf.values.tolist()
            
            chartdata = list(map(list, zip(*templist)))
            line = Line(init_opts=opts.InitOpts(width="1600px", height="800px"))
            line.set_global_opts(xaxis_opts=opts.AxisOpts(is_scale=True),
                                 yaxis_opts=opts.AxisOpts(is_scale=True),
                                 title_opts=opts.TitleOpts(title="行情快慢的比较"),
                                 datazoom_opts=[opts.DataZoomOpts(is_show=True)],
                                 toolbox_opts=opts.ToolboxOpts(is_show=True))
            line.add_xaxis(chartdata[0])
            line.add_yaxis("选择" + str(j + 1), chartdata[1], stack="stack1")
            line.add_yaxis("选择" + str(j + 2), chartdata[2], stack="stack1")
            line.render(str(j) + ".html")
            print(chartdata)
            print(len(code3[0]))
            j += 2
            if j >= len(code3[0]) - 1:
                print(len(code3[0]))
                break
        except Exception as e:
            
            pass
        
        
    


def buttonColse():
    global queue, queue1, p1, p2, p3

    if code1:
        chartCreat(code1)
        try:
            data_write("data.xls", code1)
        except Exception as e:
            print("EXCEL保存不成功，看文件是否被打开")
            pass

    try:
        queue.close()
        queue1.close()
        p2.terminate()
        p1.terminate()
        p3.terminate()
    except Exception as e:
        pass
    root.destroy()

if __name__ == "__main__":
    area = []
    fullleft = 99999
    fulltop = 99999
    fullright = 0
    fullbuttom = 0

    manaa = Manager()
    code1 = manaa.list([])
    # 创建tkinter主窗口
    root = tkinter.Tk()
    # 指定主窗口位置与大小
    root.geometry('200x200+400+300')
    # 不允许改变窗口大小
    root.resizable(False, False)
    # 显示选择区域坐标
    lista = tkinter.Listbox(root)
    lista.place(x=10, y=75, width=160, height=60)
    # 选择对比区域
    buttonCapture = tkinter.Button(root, text='选定区域', command=buttonCaptureClick)
    buttonCapture.place(x=10, y=10, width=160, height=20)
    buttonCapture1 = tkinter.Button(root, text='开始截屏', command=buttonzhuatu)
    buttonCapture1.place(x=10, y=35, width=160, height=20)
    buttonCapture1 = tkinter.Button(root, text='停止并保存数据', command=buttonColse)
    buttonCapture1.place(x=10, y=55, width=160, height=20)
    # 启动消息主循环
    root.protocol("WM_DELETE_WINDOW", buttonColse)
    root.mainloop()

