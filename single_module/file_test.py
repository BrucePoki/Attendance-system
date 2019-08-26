import os

root_path = os.path.dirname(os.path.abspath(__file__))

print(root_path)
path = root_path + "/screenshots/faces_separated/"

isExists = os.path.exists(path)

if not isExists:
    os.makedirs(path)
    print(path + '创建成功')
    # return Ture
else:
    print(path + '目录已存在')
    # return False

