import os
import cv2
import dlib
import time
import numpy as np
from aip import AipFace  # AI core
import base64  # for encode use
from PIL import Image
import matplotlib.pyplot as plt

'''APP Detail'''
APP_ID = '17074468'
API_ID = 'tBs6GAGhr1hRow3KacUtQGGk'
SECRET_KEY = 'A4iSePxNobpGFSupM4XTV0McSoqKqyFt'
online_client = AipFace(APP_ID, API_ID, SECRET_KEY)  # Online detect client


def makedir():
    root_path = os.path.dirname(os.path.abspath(__file__))

    sep_path = root_path + "/screenshots/faces_separated/"

    ss_path = root_path + "/screenshots/"

    cc_path = root_path + "/cache/"

    is_exists = os.path.exists(sep_path) and os.path.exists(cc_path)

    if not is_exists:
        os.makedirs(sep_path)
        os.makedirs(cc_path)
        print('Cache path created')
    else:
        print('Cache catalog already exists')

    return sep_path, ss_path, cc_path


def show_img(path):
    img = Image.open(path)
    plt.figure('Guest')
    plt.imshow(img)
    plt.axis('off')
    plt.show()


def clear_images(path_save, path_cache):
    imgs = os.listdir(path_save)
    imgc = os.listdir(path_cache)
    for img in imgs:
        os.remove(path_save + img)
    for img in imgc:
        os.remove(path_cache + img)

    print("Clean finish", '\n')


def face_separate(cc_path, sep_path, detector):
    path_read = cc_path
    img = cv2.imread(path_read + "confirm_cache.jpg")

    path_save = sep_path

    clear_images(path_save, cc_path)

    faces = detector(img, 1)

    print("Number of Faces detected: ", len(faces), '\n')

    for k, d in enumerate(faces):

        height = d.bottom() - d.top()
        width = d.right() - d.left()

        img_blank = np.zeros((height, width, 3), np.uint8)

        for i in range(height):
            for j in range(width):
                img_blank[i][j] = img[d.top() + i][d.left() + j]

        # print("Save to: ", path_save + "img_face_", str(k + 1) + ".jpg")
        cv2.imwrite(path_save + "img_face_" + str(k + 1) + ".jpg", img_blank)

    return len(faces)


def face_recognize(client, read_path):
    with open(read_path, "rb") as f:
        base64_data = base64.b64encode(f.read())
        # print(base64_data)  # encode check

    image = str(base64_data, 'utf-8')
    # error record: error_code:222203 image check fail
    # solution: specific type convert: utf-8
    image_type = "BASE64"
    group_id_list = "test"

    # options = {}
    # options["match_threshold"] = 80

    result = client.search(image, image_type, group_id_list)

    return result


def face_register(client, read_path, group_id, usr_name):
    with open(read_path, "rb") as f:
        base64_data = base64.b64encode(f.read())
        # print(base64_data)  # encode check

    image = str(base64_data, 'utf-8')
    # error record: error_code:222203 image check fail
    # solution: specific type convert: utf-8
    image_type = "BASE64"
    group_id_list = group_id
    user_id = usr_name

    client.addUser(image, image_type, group_id_list, user_id)
    print(user_id + " registration success!")


def live_cam_detect(ss_path, sep_path, cc_path):
    path_screenshots = ss_path

    detector = dlib.get_frontal_face_detector()
    # predictor = dlib.shape_predictor(pre_path)

    cap = cv2.VideoCapture(0)

    cap.set(3, 960)

    if cap.isOpened():
        print("Camera is on.")

    ss_cnt = 0

    while cap.isOpened():
        flag, img_rd = cap.read()

        k = cv2.waitKey(1)

        img_gray = cv2.cvtColor(img_rd, cv2.COLOR_RGB2GRAY)

        faces = detector(img_gray, 0)

        font = cv2.FONT_HERSHEY_SIMPLEX

        if k & 0xFF == ord('q'):
            break
        else:
            if len(faces) != 0:

                for face in faces:
                    cv2.rectangle(img_rd, tuple([face.left(), face.top()]), tuple([face.right(), face.bottom()]),
                                  (0, 255, 255), 2)

                cv2.putText(img_rd, "Faces in all: " + str(len(faces)), (20, 350), font, 0.8, (0, 0, 0), 1, cv2.LINE_AA)
            else:
                cv2.putText(img_rd, "no face", (20, 350), font, 0.8, (0, 0, 0), 1, cv2.LINE_AA)

            img_rd = cv2.putText(img_rd, "Press 'S': Screen shot", (20, 400), font, 0.8, (255, 255, 255), 1,
                                 cv2.LINE_AA)
            img_rd = cv2.putText(img_rd, "Press 'C': Confirm image", (20, 450), font, 0.8, (255, 255, 255), 1,
                                 cv2.LINE_AA)
            img_rd = cv2.putText(img_rd, "Press 'Q': Quit", (20, 500), font, 0.8, (255, 255, 255), 1, cv2.LINE_AA)

        if k & 0xFF == ord('s'):
            ss_cnt += 1
            print(path_screenshots + "screenshot" + "_" + str(ss_cnt) + "_" + time.strftime("%Y-%m-%d-%H-%M-%S",
                                                                                            time.localtime()) + ".jpg")
            cv2.imwrite(path_screenshots + "screenshot" + "_" + str(ss_cnt) + "_" +
                        time.strftime("%Y-%m-%d-%H-%M-%S",time.localtime()) + ".jpg",img_rd)

        if k & 0xFF == ord('c'):
            print("Face info confirmed, detecting ...")
            cv2.imwrite(cc_path + "confirm_cache.jpg", img_rd)
            faces = face_separate(cc_path, sep_path, detector)
            print(faces, " faces detected. Recognizing...")
            print("Please Wait ...")
            stuff_list = []
            guest_list = []
            reco_cnt = 0
            unreco_cnt = 0
            for face_num in range(0, faces):
                read_path = sep_path + "img_face_" + str(face_num + 1) + ".jpg"
                result = face_recognize(online_client, read_path)
                if result['error_msg'] == 'SUCCESS':
                    if result['result']['user_list'][0]['score'] >= 80:
                        stuff_list.append(result['result']['user_list'][0]['user_id'])
                        reco_cnt += 1
                        print('Welcome ', stuff_list[reco_cnt - 1], '! Check in successful.')
                    else:
                        unreco_cnt += 1
                        guest_list.append(read_path)
            print(reco_cnt, ' of ', faces, 'faces recognized. Process complete.')
            if unreco_cnt != 0:
                regist_flag = input("Unemployee faces detected. Register? (Y/N)")
                if regist_flag == 'Y' or regist_flag == 'y':
                    for i in range(0, unreco_cnt):
                        show_img(guest_list[i])
                        name = input("Who is this(name)? Please watch the image on your right side.\n")
                        face_register(online_client, guest_list[i], 'employee', name)
                elif regist_flag == 'N' or regist_flag == 'n':
                    for j in range(0, unreco_cnt):
                        face_register(online_client, guest_list[j], 'guest', time.strftime("%Y-%m-%d-%H-%M-%S",
                                                                                           time.localtime()))

        cv2.namedWindow("camera", 1)
        cv2.imshow("camera", img_rd)

    cap.release()

    if not cap.isOpened():
        print("Camera is off.")

    cv2.destroyAllWindows()


print('Initiallizing ...')
separate_path, screenshot_path, cache_path = makedir()

live_cam_detect(screenshot_path, separate_path, cache_path)





