import cv2
import os


def capture_images(nombre_estudiante):
    cap = cv2.VideoCapture(0)
    count = 0

    if not os.path.exists('imagenes'):
        os.makedirs('imagenes')

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow('Capturing Images', frame)
        k = cv2.waitKey(1)
        if k % 256 == 27: 
            break
        elif k % 256 == 32:  
            img_name = f"imagenes/{nombre_estudiante}_{count}.jpg"
            cv2.imwrite(img_name, frame)
            print(f"{img_name} Guardado!")
            count += 1

    cap.release()
    cv2.destroyAllWindows()

nombre_estudiante = input("ingresa su numero de identificación: ")
capture_images(nombre_estudiante)
    