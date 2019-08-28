import wx


app = wx.App()
windows = wx.Frame(None, title="Work Attendence System (WAS)", size=(900, 600))  # 画个框
windows.Show()

faceCheckInButton = wx.Button(windows, label='Register', pos=(60, 84), size=(80, 40))
faceCheckInButton.Bind(wx.EVT_BUTTON, None)  # 第二参数需要添加签到函数

screenShotButton = wx.Button(windows, label='Screen Shot', pos=(60, 208), size=(80, 40))
screenShotButton.Bind(wx.EVT_BUTTON, None)  # 第二参数需要添加截图函数

viewLogButton = wx.Button(windows, label='View & Output Log', pos=(30, 332), size=(140, 40))
viewLogButton.Bind(wx.EVT_BUTTON, None)  # 第二参数需要添加查看表格和导出函数

aboutButton = wx.Button(windows, label='About Out Team & System', pos=(30, 476), size=(140, 40))
aboutButton.Bind(wx.EVT_BUTTON, None)  # 第二参数需要添加团队介绍和程序介绍

# 控制台显示框
terminal = wx.TextCtrl(windows, pos=(200, 10), size=(700, 580), style=wx.TE_MULTILINE | wx.HSCROLL)

app.MainLoop()
