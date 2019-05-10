# -*- coding:utf-8 -*-

import os
import tkinter
import tkinter.filedialog
from time import sleep

import mss
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


def buttonzhuatu():
    with mss.mss() as sct:
        global fullbuttom, fullleft, fullright, fulltop, shuju, code, code1
        monitor = {"top": fulltop, "left": fullleft, "width": fullright - fullleft, "height": fullbuttom - fulltop}
        n = 300
        # 截图
        for i in range(n):
            output = str(i) + ".png"
            sct_img = sct.grab(monitor)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
            sleep(0.2)
        # 计算有效数据区
        for item in area:
            shuju.append((item[0] - fullleft, item[2] - fulltop, item[1] - fullleft, item[3] - fulltop))
        print(shuju)
        # 识别数据
        for i in range(n):
            output = str(i) + ".png"
            img = Image.open(output)
            code = []

            code.clear()
            '''
            print(i,code)
            img = img.convert('RGBA')  # 转换为RGBA
            pix = img.load()
            
            for y in range(img.size[1]):  # 二值化处理，这个阈值为R=95，G=95，B=95
                for x in range(img.size[0]):
                    if  pix[x, y][1] > 13 or pix[x, y][2] > 13:
                        pix[x, y] = (255, 255, 255, 255)

                    else:
                        pix[x, y] = (0, 0, 0, 255)
            img.save('a'+output)
            '''

            # print(shuju)
            code.insert(0, str(i))
            print(code)
            # 选定区域识别
            m = 0
            for item in shuju:

                region = img.crop(item)

                if m == 0:
                    code.append(pytesseract.image_to_string(region, config='-psm 7 sfz', lang='new'))
                    m = m + 1
                else:
                    code.append(pytesseract.image_to_string(region, config='-psm 7 sfz', lang='bh'))
                    m = 0
            # print(i,code)
            print(code)
            code1.append(code)
            print(code1)
        print(code1)
        B1 = []
        A1 = []
        A2 = []
        code2 = []
        sssw = ""
        for item in code1:
            print(item)
            if (item[1] != item[2] or item[1] != sssw):
                B1.append(item[0])
                A1.append(item[1])
                A2.append(item[2])
                code2.append(item)
                sssw = item[1]
        line = Line(init_opts=opts.InitOpts(width="1200px", height="800px"))

        line.set_global_opts(xaxis_opts=opts.AxisOpts(is_scale=True),
                             yaxis_opts=opts.AxisOpts(is_scale=True),
                             title_opts=opts.TitleOpts(title="行情快慢的比较"),
                             datazoom_opts=[opts.DataZoomOpts(is_show=True)],
                             toolbox_opts=opts.ToolboxOpts(is_show=True))

        line.add_xaxis(B1)
        line.add_yaxis("同花顺", A1)
        line.add_yaxis("通达信", A2)

        line.render()
        data_write("data.xls", code2)


if __name__ == "__main__":
    area = []
    fullleft = 99999
    fulltop = 99999
    fullright = 0
    fullbuttom = 0
    shuju = []
    code1 = []
    # 创建tkinter主窗口
    root = tkinter.Tk()
    # 指定主窗口位置与大小
    root.geometry('200x200+400+300')
    # 不允许改变窗口大小
    root.resizable(False, False)
    # 显示选择区域坐标
    lista = tkinter.Listbox(root)
    lista.place(x=10, y=50, width=160, height=60)
    # 选择对比区域
    buttonCapture = tkinter.Button(root, text='选定区域', command=buttonCaptureClick)
    buttonCapture.place(x=10, y=10, width=160, height=20)
    buttonCapture1 = tkinter.Button(root, text='开始截屏', command=buttonzhuatu)
    buttonCapture1.place(x=10, y=35, width=160, height=20)
    # 启动消息主循环

    root.mainloop()
