import cv2
import face_recognition
imagen = cv2.imread("imagenes/fabian_0.jpg")
face_loc = face_recognition.face_locations(imagen)[0]

face_imagen_encodings = face_recognition.face_encodings(imagen, known_face_locations=[face_loc])[0]


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
while True:
    ret, frame = cap.read()
    if ret == False: break
    frame = cv2.flip(frame, 1)
    
    face_locations = face_recognition.face_locations(frame)
    if face_locations != []:
        for face_location in face_locations:
            face_frame_encodings = face_recognition.face_encodings(frame, known_face_locations=[face_location])[0]
            result = face_recognition.compare_faces([face_frame_encodings], face_imagen_encodings)
            print("Resultado : ",result)
            cv2.rectangle(frame, (face_location[3], face_location[0]) ,(face_location[1], face_location[2]), (255,0,0), 2)
    
    
    cv2.imshow("Frame", frame)
   
    k = cv2.waitKey(1)
    if k == 27 & 0xFF:
        break
    
cap.release()
cv2.destroyAllWindows()