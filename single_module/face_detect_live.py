import cv2
import dlib
import time

path_screenshots = "/Users/bruce/Desktop/screenshots/"

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('/Users/bruce/dlib/shape_predictor_68_face_landmarks 2.dat')

cap = cv2.VideoCapture(0)

cap.set(3, 960)

if cap.isOpened():
    print("Camera is on.")

ss_cnt = 0

while cap.isOpened():
    flag, img_rd = cap.read()
    # cv2.imshow("camera", img_rd)

    k = cv2.waitKey(1)

    img_gray = cv2.cvtColor(img_rd, cv2.COLOR_RGB2GRAY)

    faces = detector(img_gray, 0)

    font = cv2.FONT_HERSHEY_SIMPLEX

    if k & 0xFF == ord('q'):
        break
    else:
        if len(faces) != 0:
            # faces_start_width = 0

            for face in faces:
                cv2.rectangle(img_rd, tuple([face.left(), face.top()]), tuple([face.right(), face.bottom()]), (0,255,255), 2)
                # height = face.bottom() - face.top()
                # width = face.right() - face.left()
            cv2.putText(img_rd, "Faces in all: " + str(len(faces)), (20, 350), font, 0.8, (0, 0, 0), 1, cv2.LINE_AA)
        else:
            cv2.putText(img_rd, "no face", (20, 350), font, 0.8, (0, 0, 0), 1, cv2.LINE_AA)

        img_rd = cv2.putText(img_rd, "Press 'S': Screen shot", (20, 400), font, 0.8, (255, 255, 255), 1, cv2.LINE_AA)
        img_rd = cv2.putText(img_rd, "Press 'Q': Quit", (20, 450), font, 0.8, (255, 255, 255), 1, cv2.LINE_AA)

    if k & 0xFF == ord('s'):
        ss_cnt += 1
        print(path_screenshots + "screenshot" + "_" + str(ss_cnt) + "_" + time.strftime("%Y-%m-%d-%H-%M-%S",time.localtime()) + ".jpg")
        cv2.imwrite(path_screenshots + "screenshot" + "_" + str(ss_cnt) + "_" + time.strftime("%Y-%m-%d-%H-%M-%S",time.localtime()) + ".jpg", img_rd)

    cv2.namedWindow("camera", 1)
    cv2.imshow("camera", img_rd)


cap.release()

if not cap.isOpened():
    print("Camera is off.")

cv2.destroyAllWindows()
