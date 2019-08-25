import dlib
import numpy as np
import cv2
import os

path_read = "/Users/bruce/Desktop/screenshots/"
img = cv2.imread(path_read + "multiple_faces_test.jpeg")

path_save = "/Users/bruce/Desktop/screenshots/faces_separated/"


def clear_images():
    imgs = os.listdir(path_save)

    for img in imgs:
        os.remove(path_save + img)

    print("Clean finish", '\n')


clear_images()

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('/Users/bruce/dlib/shape_predictor_68_face_landmarks 2.dat')


faces = detector(img, 1)

print("人脸数: ", len(faces), '\n')

for k, d in enumerate(faces):
    pos_start = tuple([d.left(), d.top()])
    pos_end = tuple([d.right(), d.bottom()])

    height = d.bottom() - d.top()
    width = d.right() - d.left()

    img_blank = np.zeros((height, width, 3), np.uint8)

    for i in range(height):
        for j in range(width):
            img_blank[i][j] = img[d.top() + i][d.left() + j]

    print("Save to: ", path_save + "img_face_", str(k+1) + ".jpg")
    cv2.imwrite(path_save + "img_face_" + str(k+1) + ".jpg", img_blank)