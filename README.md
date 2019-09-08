## 项目和作者简介

基于OpenCV，dlib以及百度AI开放平台的员工刷脸考勤系统。

作者与@inspurer学长同一学校:) 课程设计题目真就不带变的。本程序写于2019/09/

QQ:1274616186  
由于使用了云服务辅助实现功能，所以通用性不强。开源仅供交流参考，如有建议还请多指教<3

## 使用说明

1.IDE:Pycharm  
2.环境:Python 3.7  
3.第三方依赖库:pip install -r requirements.txt  

#### main.py（v1.0)
main.py是第一个版本的程序，没有GUI界面，所有操作均需要在控制台进行。注册过程是通过matplotlib配合PIL展示图片让用户识别。

#### mainUi.py (v2.0)
mainUi.py是第二个版本的程序，有GUI界面。但是摄像头界面与主程序框分离，是老师检查前的最后版本。

#### mainUi2.py (v2.1)
mainUi2.py是结合了老师提出的相关建议写出的。把摄像头画面嵌入到了程序框中，各个功能也都细化成了按钮。

#### 相关运行测试结果及程序编写的完整思路详见课程设计报告.pdf

## 参考资料

[http://dlib.net/](http://dlib.net/)

[https://wxpython.org/](https://wxpython.org/)

[http://www.cnblogs.com/AdaminXie](http://www.cnblogs.com/AdaminXie)

[https://www.cnblogs.com/monsteryang/p/6574550.html](https://www.cnblogs.com/monsteryang/p/6574550.html)

[https://ai.baidu.com/docs#/Face-Python-SDK/6e12bec2](https://ai.baidu.com/docs#/Face-Python-SDK/6e12bec2)

[https://blog.csdn.net/qq_41646358/article/details/81292310](https://blog.csdn.net/qq_41646358/article/details/81292310)

[https://blog.csdn.net/yaningli/article/details/86736108](https://blog.csdn.net/yaningli/article/details/86736108)

学长的思路借鉴：[https://github.com/inspurer/WorkAttendanceSystem](https://github.com/inspurer/WorkAttendanceSystem)

扩展内容：视频流嵌入 [http://blog.sina.com.cn/s/blog_49b3ba190102yukm.html](http://blog.sina.com.cn/s/blog_49b3ba190102yukm.html)
