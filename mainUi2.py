import wx  # 图形界面库
import xlwt  # Excel表格相关
import xlrd  # Excel表格相关
import dlib  # 人脸识别核心库
import time  # 用于获取当前时间
import shutil  # 文件的相关操作
import numpy as np  # 人脸识别相关
import base64  # for encode use
import os  # 调用系统功能，路径，控制台等
import cv2  # opencv，用于图像识别和摄像头等
import matplotlib.pyplot as plt  # 图像显示

from PIL import Image  # 图像处理
from aip import AipFace  # AI core
from xlutils.copy import copy  # Excel相关

COVER = './venv/csu.jpg'
main1 = "./venv/icon.png"
main2 = "./venv/csu.jpg"
file_path = os.getcwd()+r'\data\logcat.csv'
# 一般GUI程序的最外层框架使用wx.Frame

'''APP Detail'''
APP_ID = '17074468'
API_ID = 'tBs6GAGhr1hRow3KacUtQGGk'
SECRET_KEY = 'A4iSePxNobpGFSupM4XTV0McSoqKqyFt'
online_client = AipFace(APP_ID, API_ID, SECRET_KEY)  # Online detect client


def network_test():
    """
临时起意想写的测试网络的小函数。。。
    """
    flag = 1
    while flag:
        exit_code = os.system('ping -c 3 www.baidu.com')
        if exit_code:
            wx.MessageBox('Connection Lost.\nThis software requires Online Network.\nNext connection check in 10s')
            time.sleep(10)
        else:
            print('Network Connection checked sucessful.')
            flag = 0


def makedir():
    """
初始化创建必需的缓存文件夹。包括截图文件夹，人脸分离文件夹以及人脸检测缓存文件夹
    :return: 返回三种文件夹的路径str
    """
    root_path = os.path.dirname(os.path.abspath(__file__))  # 获取main.py所在文件夹的绝对路径

    # 直观地创建三个文件夹的路径
    sep_path = root_path + "/screenshots/faces_separated/"
    ss_path = root_path + "/screenshots/"
    cc_path = root_path + "/cache/"
    log_path = root_path + "/log/"
    past_log = log_path + "record/"

    # 检测路径是否已经存在
    is_exists = os.path.exists(sep_path) and os.path.exists(cc_path) and os.path.exists(log_path)

    # 如果没有存在则创建，如果存在则跳过创建
    if not is_exists:
        os.makedirs(sep_path)
        os.makedirs(cc_path)
        os.makedirs(log_path)
        os.makedirs(past_log)
        print('Cache path created')
    else:
        print('Cache catalog already exists')

    return sep_path, ss_path, cc_path


def initialize(client):
    """
初始化函数，主要是在执行主程序前准备好出勤表格
    :param client: 为了从云端服务器获取员工信息并在本地建立表格
    :return: 返回获取的员工列表
    """
    if os.path.exists("./log/employee.xls"):
        # 如果原存储员工表格的路径已经存在则转移到日志记录路径作为保存
        shutil.move("./log/employee.xls", "./log/record/" + time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.xls')
    xls = xlwt.Workbook()  # 创建Excel表格文件
    sht1 = xls.add_sheet('Sheet1')  # 创建工作表

    # 添加列标题
    sht1.write(0, 0, 'Name')
    sht1.write(0, 1, 'Status')
    sht1.write(0, 2, 'Reg time')

    # 从云端获取列表
    result = client.getGroupUsers('employee')
    length = len(result['result']['user_id_list'])  # 取得列表长度

    # 默认初始员工状态为未注册
    for i in range(0, length):
        sht1.write(i + 1, 0, result['result']['user_id_list'][i])
        sht1.write(i + 1, 1, 'Unregistered')
    xls.save('./log/employee.xls')  # 保存至默认路径
    return result['result']['user_id_list']


def show_img(path):
    """
辅助用函数，用于显示图片。入口参数为图片路径。用户不可修改路径，软件内置。
    :param path: 图片路径
    """
    img = Image.open(path)
    plt.figure('Guest')
    plt.imshow(img)
    plt.axis('off')
    plt.show()  # 显示函数


def clear_images(path_save, path_cache):
    """
清除所在文件夹的所有图片，用于初始化
    :param path_save: 截图存储路径
    :param path_cache: 缓存图片存储路径
    """
    imgs = os.listdir(path_save)
    imgc = os.listdir(path_cache)
    for img in imgs:
        os.remove(path_save + img)
    for img in imgc:
        os.remove(path_cache + img)

    print("Catalog Clean finished.", '\n')


def face_separate(cc_path, sep_path, detector):
    """
人脸分离函数。主要功能是将人脸从静态图片中剪切并导出。
    :param cc_path: 缓存图片路径，用于存储原始图片
    :param sep_path: 被剪切的人脸图像保存路径
    :param detector: dlib参数，此处用作入口参数传入减小代码重复率
    :return: 返回检测到的人脸数量
    """
    path_read = cc_path
    img = cv2.imread(path_read + "confirm_cache.jpg")  # 从缓存路径读取原始图片

    path_save = sep_path

    clear_images(path_save, cc_path)  # 清除缓存

    faces = detector(img, 1)  # 检测人脸数

    print("Number of Faces detected: ", len(faces), '\n')

    for k, d in enumerate(faces):

        height = d.bottom() - d.top()
        width = d.right() - d.left()

        img_blank = np.zeros((height, width, 3), np.uint8)  # 设置剪切图片的宽高

        try:
            # bug record: 如果只出现半张脸会出现检测下标超过边界 IndexError
            for i in range(height):
                for j in range(width):
                    img_blank[i][j] = img[d.top() + i][d.left() + j]
        except IndexError:
            wx.MessageBox('Facial info must be FULLY contained!!', caption='IndexError')
            return 0

        # print("Save to: ", path_save + "img_face_", str(k + 1) + ".jpg")
        cv2.imwrite(path_save + "img_face_" + str(k + 1) + ".jpg", img_blank)  # 依次写入剪切的图片

    return len(faces)


def face_recognize(client, read_path):
    """
该模块用于人脸比对，利用百度ai人脸识别接口
    :param client: 百度ai客户端验证
    :param read_path: 人脸图片读取路径
    :return: 返回识别结果
    """
    with open(read_path, "rb") as f:  # 打开文件
        base64_data = base64.b64encode(f.read())
        # print(base64_data)  # encode check

    image = str(base64_data, 'utf-8')
    # error record: error_code:222203 image check fail
    # solution: specific type convert: utf-8
    image_type = "BASE64"  # 默认
    group_id_list = "employee"

    # options = {}
    # options["match_threshold"] = 80
    # 相似度可选，后来选择的自己手动检测相似度这样更加灵活

    # 模块核心函数
    result = client.search(image, image_type, group_id_list)

    return result


def face_register(client, read_path, group_id, usr_name):
    """
人脸注册模块，主要是向云端上传人脸图片以及自定义人名
    :param client: 减少复用，client作为参数传入
    :param read_path: 上传图片的路径
    :param group_id:云端图片组名称
    :param usr_name: 新注册用户名称
    :return: 返回注册结果
    """
    with open(read_path, "rb") as f:  # 打开文件
        base64_data = base64.b64encode(f.read())
        # print(base64_data)  # encode check

    image = str(base64_data, 'utf-8')
    # error record: error_code:222203 image check fail
    # solution: specific type convert: utf-8
    image_type = "BASE64"  # 默认
    group_id_list = group_id
    user_id = usr_name

    options = {"action_type": "APPEND"}  # 选项设置，此处设定注册重复名称则追加照片，不覆盖
    # 模块核心函数
    result = client.addUser(image, image_type, group_id_list, user_id, options)
    if group_id != 'guest':  # 如果注册的是guest则不显示签到成功信息，只记录
        # 如果出现错误则打印错误信息。
        # 错误历史记录：名字过长导致图片上传失败，当时没有传回报错信息。
        # 故此处添加了如果出错则打印出错信息。
        if result['error_msg'] != 'SUCCESS':
            wx.MessageBox('register failed. Error message:' + result['error_msg'], caption='Ops! Error occured')
        else:
            wx.MessageBox(user_id + " registration success!")
    return result


def live_cam_detect(sep_path, cc_path, usr_list, self):
    """
程序核心函数，主要利用opencv使用摄像头，然后调用上述函数进行完整的程序过程
    :param self:
    :param usr_list: 从参数入口传入初始化获取的员工列表
    :param sep_path: separate路径
    :param cc_path: 缓存路径
    """

    self.sep_path = sep_path
    self.cc_path = cc_path
    self.usr_list = usr_list

    # 开启笔记本默认摄像头
    self.cap = cv2.VideoCapture(0)

    # 设置分辨率及格式
    self.cap.set(3, 480)

    if self.cap.isOpened():  # 检测摄像头是否开启
        print("Camera is on.")

    while self.cap.isOpened():  # 程序主循环，保持摄像头开启状态
        flag, img_rd = self.cap.read()  # 两个参数，
        # 一个flag是接收读取图片状态，即True or False第二个是frame表示截取到的一帧的图片
        self.flag = flag
        self.img_rd = img_rd

        self.k = cv2.waitKey(1)  # 等待信号指令

        img_gray = cv2.cvtColor(img_rd, cv2.COLOR_RGB2GRAY)
        # 灰度测试并保存，用于人脸的探测
        # 灰度有利于提高检测速度

        self.faces = self.detector(img_gray, 0)  # 利用灰度检查人脸

        font = cv2.FONT_HERSHEY_SIMPLEX  # 设置指令显示的字体

        # 开始画方框用于标识人脸
        if len(self.faces) != 0:

            for face in self.faces:  # faces并非数字类型，其包含了众多实用的函数通过这些函数计算出矩形框的长宽
                cv2.rectangle(img_rd, tuple([face.left(), face.top()])
                              , tuple([face.right(), face.bottom()]), (0, 255, 255), 2)

        # 注明指令和要求并设置字体格式 字体：HERSHEY_SIMPLEX 颜色：GOLD 粗细：2
        img_rd = cv2.putText(img_rd, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), (900, 50), font, 0.8
                             , (255, 255, 0), 2, cv2.LINE_AA)

        height, width = img_rd.shape[:2]
        image1 = cv2.cvtColor(img_rd, cv2.COLOR_BGR2RGB)
        pic = wx.Bitmap.FromBuffer(width, height, image1)
        # 显示图片在panel上
        self.bmp.SetBitmap(pic)
        self.grid_bag_sizer.Fit(self)

    self.cap.release()  # 释放摄像头

    cv2.destroyAllWindows()  # 关闭所有窗口


class face_emotion(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1024, 768))
        self.panel = wx.Panel(self)
        self.Center()


        # 封面图片
        self.image_cover = wx.Image(COVER, wx.BITMAP_TYPE_ANY).Scale(960, 720)
        # 显示图片在panel上
        self.bmp = wx.StaticBitmap(self.panel, -1, wx.Bitmap(self.image_cover))

        start_button = wx.Button(self.panel, label='Camera On')
        close_button = wx.Button(self.panel, label='Camera Off')
        confirm_button = wx.Button(self.panel, label='Check in')
        viewlog_button = wx.Button(self.panel, label='View Log')

        self.Bind(wx.EVT_BUTTON, self.learning_face, start_button)
        self.Bind(wx.EVT_BUTTON, self.close_face, close_button)
        self.Bind(wx.EVT_BUTTON, self.confirm_face, confirm_button)
        self.Bind(wx.EVT_BUTTON, self.view_log, viewlog_button)

        # 基于GridBagSizer的界面布局
        # 先实例一个对象
        self.grid_bag_sizer = wx.GridBagSizer(hgap=5, vgap=5)
        # 注意pos里面是先纵坐标后横坐标
        self.grid_bag_sizer.Add(self.bmp, pos=(0, 0), flag=wx.ALL | wx.EXPAND, span=(4, 4), border=5)
        self.grid_bag_sizer.Add(start_button, pos=(4, 1), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, span=(1, 1), border=5)
        self.grid_bag_sizer.Add(close_button, pos=(4, 2), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, span=(1, 1), border=5)
        self.grid_bag_sizer.Add(confirm_button, pos=(4, 3), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, span=(1, 1), border=5)
        self.grid_bag_sizer.Add(viewlog_button, pos=(4, 4), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, span=(1, 1), border=5)

        self.grid_bag_sizer.AddGrowableCol(0, 1)
        # grid_bag_sizer.AddGrowableCol(0,2)

        self.grid_bag_sizer.AddGrowableRow(0, 1)
        # grid_bag_sizer.AddGrowableRow(0,2)

        self.panel.SetSizer(self.grid_bag_sizer)
        # 界面自动调整窗口适应内容
        self.grid_bag_sizer.Fit(self)

        """dlib的初始化调用"""
        # 使用人脸检测器get_frontal_face_detector
        self.detector = dlib.get_frontal_face_detector()

        self.userList = initialize(online_client)

    def _learning_face(self,event):
        # 主函数部分
        print('Initiallizing ...')

        # network_test() 测试功能哈哈哈，先不用。用于监测网络连接状态

        # 创建程序所需的目录
        separate_path, screenshot_path, cache_path = makedir()

        # 程序核心函数，打开摄像头并开始接收指令
        live_cam_detect(separate_path, cache_path, self.userList, self)

    def confirm_face(self, event):
        print('\n', '*' * 50, '\n')
        print("Face info confirmed, detecting ...")
        cv2.imwrite(self.cc_path + "confirm_cache.jpg", self.img_rd)  # 将截图写入缓存路径
        faces = face_separate(self.cc_path, self.sep_path, self.detector)  # 从缓存路径读取原始图片并分割
        print(self.faces, " faces detected. Recognizing...")
        print("Please Wait ...")

        stuff_list = []  # 员工列表
        guest_list = []  # 客人列表
        reco_cnt = 0  # 识别出的人脸数
        unreco_cnt = 0  # 未识别出的人脸数

        for face_num in range(0, faces):
            read_path = self.sep_path + "img_face_" + str(face_num + 1) + ".jpg"  # 自动依次读取分割路径下的图片
            result = face_recognize(online_client, read_path)  # 开始上传检测
            if result['error_msg'] == 'SUCCESS':  # 如果检测成功
                if result['result']['user_list'][0]['score'] >= 80:  # 相似度阀值定为80
                    stuff_list.append(result['result']['user_list'][0]['user_id'])
                    reco_cnt += 1

                    rb = xlrd.open_workbook('./log/employee.xls')
                    wb = copy(rb)
                    ws = wb.get_sheet(0)
                    sheet1 = rb.sheet_by_index(0)

                    if sheet1.cell_value(self.usr_list.index(stuff_list[reco_cnt - 1]) + 1, 1) == 'Registered':
                        wx.MessageBox("* * " + stuff_list[reco_cnt - 1] + ' has already checked in. * *'
                                      , caption='Ops!')
                        # print("* * ", stuff_list[reco_cnt - 1], ' has already checked in. * *')
                    else:
                        wx.MessageBox('* *Welcome ' + stuff_list[reco_cnt - 1] + '! Check in successful.* *'
                                      , caption='Congratulate!')
                        # print('* *Welcome ', stuff_list[reco_cnt - 1], '! Check in successful.* *')

                    # 打开已经初始化的表格准备修改状态
                    ws.write(self.usr_list.index(stuff_list[reco_cnt - 1]) + 1, 1, 'Registered')
                    ws.write(self.usr_list.index(stuff_list[reco_cnt - 1]) + 1, 2, time.strftime("%Y-%m-%d %H:%M:%S"
                                                                                            , time.localtime()))
                    wb.save('./log/employee.xls')

                else:  # 未达到80相似度，稍后询问是否手动录入
                    unreco_cnt += 1
                    guest_list.append(read_path)

        print(reco_cnt, ' of ', faces, 'faces recognized. Process complete.')

        # 如果存在未识别的人脸
        if unreco_cnt != 0:
            dialog1 = wx.MessageDialog(None, 'Unregistered employee detected! Register?', 'Ops!'
                                       , wx.YES_NO or wx.ICON_QUESTION)
            if dialog1.ShowModal() == wx.ID_YES:
                for i in range(0, unreco_cnt):
                    os.system('open ' + guest_list[i])
                    # show_img(guest_list[i])  # 显示未识别成员工的图片，请求用户指认该人脸姓名
                    dialog = wx.TextEntryDialog(None, "Who is this?", 'Info input', ' ')
                    if dialog.ShowModal() == wx.ID_OK:
                        response = dialog.GetValue()
                        face_register(online_client, guest_list[i], 'employee', response)  # 录入姓名

                        rb = xlrd.open_workbook('./log/employee.xls')
                        wb = copy(rb)
                        ws = wb.get_sheet(0)

                        # 在上传的同时更新本地出勤表
                        ws.write(len(self.usr_list) + 2, 0, response)
                        ws.write(len(self.usr_list) + 2, 1, 'Registered')
                        ws.write(len(self.usr_list) + 2, 2, time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))

                        wb.save('./log/employee.xls')

                    else:
                        for j in range(0, unreco_cnt):
                            face_register(online_client, guest_list[j], 'guest', time.strftime("%Y%m%d%H%M%S"
                                                                                               , time.localtime()))

            else:
                for j in range(0, unreco_cnt):
                    face_register(online_client, guest_list[j], 'guest', time.strftime("%Y%m%d%H%M%S"
                                                                                       , time.localtime()))
        print('\n', '*' * 50, '\n')

    def learning_face(self, event):
        """使用多线程，子线程运行后台的程序，主线程更新前台的UI，这样不会互相影响"""
        import _thread
        # 创建子线程，按钮调用这个方法，
        _thread.start_new_thread(self._learning_face, (event,))

    def close_face(self,event):
        """关闭摄像头，显示封面页"""
        self.cap.release()
        if not self.cap.isOpened():
            print('Camera is off.')
        self.bmp.SetBitmap(wx.Bitmap(self.image_cover))
        self.grid_bag_sizer.Fit(self)

    def view_log(self,event):
        os.system('open ' + os.path.dirname(os.path.abspath('./log/employee.xls')) + '/employee.xls')


class mainApp(wx.App):
    # OnInit 方法在主事件循环开始前被wxPython系统调用，是wxpython独有的
    def OnInit(self):
        frame = face_emotion(parent=None, title="Work Attendance System")
        frame.Show(True)
        return True


if __name__ == "__main__":
    network_test()
    app = mainApp()
    app.MainLoop()
