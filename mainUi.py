import wx  # 图形界面依赖库
import xlwt  # Excel表格写
import xlrd  # Excel表格读
import dlib  # 人脸识别核心库
import time  # 用于获取当前时间
import shutil  # 文件的相关操作
import numpy as np  # 人脸识别相关
import base64  # base64编码器
import os  # 调用系统功能，路径，控制台等
import cv2  # opencv，用于图像识别和摄像头等
import matplotlib.pyplot as plt  # 图像显示

from PIL import Image  # 图像处理
from aip import AipFace  # AI core
from xlutils.copy import copy  # Excel相关

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
            print('Connection Lost.\nThis software requires Online Network.')
            print('Next connection check in 10s')
            time.sleep(10)
        else:
            print('Network Connection checked sucessful.')
            flag = 0


def makedir():
    """
初始化创建必需的缓存文件夹。包括截图文件夹，人脸分离文件夹以及人脸检测缓存文件夹
    :return: 返回三种文件夹的路径str
    """
    root_path = os.path.dirname(os.path.abspath(__file__))  # 获取该源文件所在文件夹的绝对路径

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
            print('IndexError...')
            print('Facial info must be FULLY contained!!\n')
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
        print(user_id + " registration success!")
    # 如果出现错误则打印错误信息。
    # 错误历史记录：名字过长导致图片上传失败，当时没有传回报错信息。
    # 故此处添加了如果出错则打印出错信息。
    if result['error_msg'] != 'SUCCESS':
        print('register failed. Error message:' + result['error_msg'])
    return result


def live_cam_detect(ss_path, sep_path, cc_path, usr_list):
    """
程序核心函数，主要利用opencv使用摄像头，然后调用上述函数进行完整的程序过程
    :param usr_list: 从参数入口传入初始化获取的员工列表
    :param ss_path: screenshots路径
    :param sep_path: separate路径
    :param cc_path: 缓存路径
    """
    path_screenshots = ss_path

    # 人脸检测模块
    detector = dlib.get_frontal_face_detector()
    # dlib同样支持轮廓预测
    # predictor = dlib.shape_predictor(pre_path)

    # 开启笔记本默认摄像头
    cap = cv2.VideoCapture(0)

    # 设置分辨率及格式
    cap.set(3, 960)

    if cap.isOpened():  # 检测摄像头是否开启
        print("Camera is on.")

    ss_cnt = 0  # 仅用于screenshot计数，图片起名字用。测试用

    while cap.isOpened():  # 程序主循环，保持摄像头开启状态
        flag, img_rd = cap.read()  # 两个参数，
        # 一个flag是接收读取图片状态，即True or False第二个是frame表示截取到的一帧的图片

        k = cv2.waitKey(1)  # 等待信号指令

        img_gray = cv2.cvtColor(img_rd, cv2.COLOR_RGB2GRAY)
        # 灰度测试并保存，用于人脸的探测
        # 灰度有利于提高检测速度

        faces = detector(img_gray, 0)  # 利用灰度检查人脸

        font = cv2.FONT_HERSHEY_SIMPLEX  # 设置指令显示的字体

        if k & 0xFF == ord('q'):  # 输入q时退出循环
            break
        else:  # 否则，开始干正事
            # 开始画方框用于标识人脸
            if len(faces) != 0:

                for face in faces:  # faces并非数字类型，其包含了众多实用的函数通过这些函数计算出矩形框的长宽
                    cv2.rectangle(img_rd, tuple([face.left(), face.top()]), tuple([face.right(), face.bottom()]),
                                  (0, 255, 255), 2)

                # 写入文字，显示总共显示的人脸数
                cv2.putText(img_rd, "Faces in all: " + str(len(faces)), (20, 350), font, 0.8, (255, 215, 0), 2
                            , cv2.LINE_AA)

            else:  # 如果人脸数为零则显示没有脸
                cv2.putText(img_rd, "no face", (20, 350), font, 0.8, (255, 215, 0), 2, cv2.LINE_AA)

            # 注明指令和要求并设置字体格式 字体：HERSHEY_SIMPLEX 颜色：GOLD 粗细：2
            img_rd = cv2.putText(img_rd, "Press 'S': Screen shot", (20, 400), font, 0.8, (255, 215, 0), 2,
                                 cv2.LINE_AA)
            img_rd = cv2.putText(img_rd, "Press 'C': Confirm image", (20, 450), font, 0.8, (255, 215, 0), 2,
                                 cv2.LINE_AA)
            img_rd = cv2.putText(img_rd, "Press 'Q': Quit", (20, 500), font, 0.8, (255, 215, 0), 2, cv2.LINE_AA)
            img_rd = cv2.putText(img_rd, "Press 'O': Output", (20, 550), font, 0.8, (255, 215, 0), 2, cv2.LINE_AA)
            img_rd = cv2.putText(img_rd, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), (900, 50), font, 0.8
                                 , (255, 255, 0), 2, cv2.LINE_AA)

        # s键保存截图，仅作为初期测试用功能
        if k & 0xFF == ord('s'):
            ss_cnt += 1
            print(path_screenshots + "screenshot" + "_" + str(ss_cnt) + "_" + time.strftime("%Y-%m-%d-%H-%M-%S",
                                                                                            time.localtime()) + ".jpg")
            cv2.imwrite(path_screenshots + "screenshot" + "_" + str(ss_cnt) + "_" +
                        time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".jpg", img_rd)

        # c->confirm 确认录入信息，程序开始进行比对
        if k & 0xFF == ord('c'):
            print('\n', '*' * 50, '\n')
            print("Face info confirmed, detecting ...")
            cv2.imwrite(cc_path + "confirm_cache.jpg", img_rd)  # 将截图写入缓存路径
            faces = face_separate(cc_path, sep_path, detector)  # 从缓存路径读取原始图片并分割
            print(faces, " faces detected. Recognizing...")
            print("Please Wait ...")

            stuff_list = []  # 员工列表
            guest_list = []  # 客人列表
            reco_cnt = 0  # 识别出的人脸数
            unreco_cnt = 0  # 未识别出的人脸数

            for face_num in range(0, faces):
                read_path = sep_path + "img_face_" + str(face_num + 1) + ".jpg"  # 自动依次读取分割路径下的图片
                result = face_recognize(online_client, read_path)  # 开始上传检测
                if result['error_msg'] == 'SUCCESS':  # 如果检测成功
                    if result['result']['user_list'][0]['score'] >= 80:  # 相似度阀值定为80
                        stuff_list.append(result['result']['user_list'][0]['user_id'])
                        reco_cnt += 1

                        rb = xlrd.open_workbook('./log/employee.xls')
                        wb = copy(rb)
                        ws = wb.get_sheet(0)
                        sheet1 = rb.sheet_by_index(0)

                        if sheet1.cell_value(usr_list.index(stuff_list[reco_cnt - 1]) + 1, 1) == 'Registered':
                            wx.MessageBox("* * " + stuff_list[reco_cnt - 1] + ' has already checked in. * *'
                                          , caption='Ops!')
                            # print("* * ", stuff_list[reco_cnt - 1], ' has already checked in. * *')
                        else:
                            wx.MessageBox('* *Welcome ' + stuff_list[reco_cnt - 1] + '! Check in successful.* *'
                                          , caption='Congratulate!')
                            # print('* *Welcome ', stuff_list[reco_cnt - 1], '! Check in successful.* *')

                        # 打开已经初始化的表格准备修改状态
                        ws.write(usr_list.index(stuff_list[reco_cnt - 1]) + 1, 1, 'Registered')
                        ws.write(usr_list.index(stuff_list[reco_cnt - 1]) + 1, 2, time.strftime("%Y-%m-%d %H:%M:%S"
                                                                                                , time.localtime()))
                        wb.save('./log/employee.xls')

                    else:  # 未达到80相似度，稍后询问是否手动录入
                        unreco_cnt += 1
                        guest_list.append(read_path)

            print(reco_cnt, ' of ', faces, 'faces recognized. Process complete.')

            # 如果存在未识别的人脸
            if unreco_cnt != 0:
                type_flag = 1
                while type_flag:  # type flag仅作为防止输入错误指令用
                    regist_flag = input("Unemployee faces detected. Register? (Y/N)\n")
                    if regist_flag == 'Y' or regist_flag == 'y':
                        for i in range(0, unreco_cnt):
                            show_img(guest_list[i])  # 显示未识别成员工的图片，请求用户指认该人脸姓名
                            name = input("Who is this(name)? Please watch the image on your right side.\n")
                            face_register(online_client, guest_list[i], 'employee', name)  # 录入姓名

                            rb = xlrd.open_workbook('./log/employee.xls')
                            wb = copy(rb)
                            ws = wb.get_sheet(0)

                            # 在上传的同时更新本地出勤表
                            ws.write(len(usr_list) + 2, 0, name)
                            ws.write(len(usr_list) + 2, 1, 'Registered')
                            ws.write(len(usr_list) + 2, 2, time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))

                            wb.save('./log/employee.xls')

                            type_flag = 0

                    elif regist_flag == 'N' or regist_flag == 'n':
                        for j in range(0, unreco_cnt):
                            face_register(online_client, guest_list[j], 'guest', time.strftime("%Y%m%d%H%M%S"
                                                                                               , time.localtime()))
                            type_flag = 0  # 如果录入成功则改变flag终止循环

                    else:
                        print('Invalid Command.')

            print('\n', '*' * 50, '\n')

        if k & 0xFF == ord('o'):
            # 请求输入导出出勤表的路径
            output_path = input("Please input output path (Backspace for default path):")

            # 设置空格为默认路径
            if output_path == ' ':
                shutil.copy('./log/employee.xls', './')
                print('File has been saved to ' + os.path.dirname(os.path.abspath('./employee.xls')))

            elif os.path.exists(output_path):
                shutil.copy('./log/employee.xls', output_path)
                print('File has been saved to ' + output_path)

            else:
                # 无效路径
                print('Invalid path.')

        # 设置摄像头窗口的相关参数
        cv2.namedWindow("camera", 1)
        cv2.imshow("camera", img_rd)

    cap.release()  # 释放摄像头

    if not cap.isOpened():  # 检测摄像头状态
        print("Camera is off.")

    cv2.destroyAllWindows()  # 关闭所有窗口


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, -1, title="员工考勤系统", size=(800, 590))
        self.SetBackgroundColour('white')
        self.Center()

        self.frame = ''

        self.PunchcardButton = wx.Button(parent=self, pos=(120, 460), size=(80, 50), label='刷脸签到')

        self.LogcatButton = wx.Button(parent=self, pos=(455, 460), size=(80, 50), label='日志查看')

        self.InstructButton = wx.Button(parent=self, pos=(280, 460), size=(80, 50), label='操作说明')

        self.AboutButton = wx.Button(parent=self, pos=(630, 460), size=(80, 50), label='小组成员')

        self.Bind(wx.EVT_BUTTON, self.OnPunchCardButtonClicked, self.PunchcardButton)
        self.Bind(wx.EVT_BUTTON, self.OnLogcatButtonClicked, self.LogcatButton)
        self.Bind(wx.EVT_BUTTON, self.OnInstructButtonClicked, self.InstructButton)
        self.Bind(wx.EVT_BUTTON, self.OnAboutButtonClicked, self.AboutButton)

        # 封面图片
        self.image_cover = wx.Image(main2, wx.BITMAP_TYPE_ANY).Scale(520, 360)
        # 显示图片
        self.bmp = wx.StaticBitmap(parent=self, pos=(140, 80), bitmap=wx.Bitmap(self.image_cover))

    # 事件方法，的第二个参数evt或者event一定不要忘了，不然这个方法会报错
    # 类中可能有很多个方法，事件方法建议约定一个容易识别的命名方式，比如我这里是以“on_”开头

    def OnPunchCardButtonClicked(self, event):

        # 主函数部分
        print('Initiallizing ...')

        # network_test() 测试功能哈哈哈，先不用。用于监测网络连接状态

        # 创建程序所需的目录
        separate_path, screenshot_path, cache_path = makedir()

        # userList = initialize(online_client)

        # 程序核心函数，打开摄像头并开始接收指令
        live_cam_detect(screenshot_path, separate_path, cache_path, userList)

    def OnLogcatButtonClicked(self, event):
        os.system('open ' + os.path.dirname(os.path.abspath('./log/employee.xls')) + '/employee.xls')

    def OnInstructButtonClicked(self, event):
        wx.MessageBox("操作说明尚未完成。")

    def OnAboutButtonClicked(self, event):
        wx.MessageBox(message="技术支持:蒋正韬 江文思    专业班级:通信1703班" +
                              "\n所在学院:计算机学院       所在单位:中南大学", caption="关于我们")


userList = initialize(online_client)

if __name__ == '__main__':
    app = wx.App()
    myframe = MyFrame()
    myframe.Show()
    app.MainLoop()

