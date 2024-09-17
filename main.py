import cv2
import face_recognition
import flet as ft
import threading

def main(page: ft.Page):
    page.title = "Reconocimiento facial con Flet"
    texto = ft.Text(value="Introduce la cédula y haz clic en el botón", size=30)
    input_identificacion = ft.TextField(label="Ingresa tu cédula", width=200)

    def reconocimiento(identificacion):
        if not identificacion:
            texto.value = "Por favor, ingresa una cédula válida."
            page.update()
            return

        texto.value = f"Realizando reconocimiento para: {identificacion}"
        page.update()

        try:
            imagen = cv2.imread(f"imagenes/{identificacion}_0.jpg")
            if imagen is None:
                texto.value = f"Imagen no encontrada para la cédula: {identificacion}"
                page.update()
                return

            try:
                face_loc = face_recognition.face_locations(imagen)[0]
                face_imagen_encodings = face_recognition.face_encodings(imagen, known_face_locations=[face_loc])[0]
            except IndexError:
                texto.value = "No se encontró ningún rostro en la imagen proporcionada."
                page.update()
                return

            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not cap.isOpened():
                texto.value = "No se pudo acceder a la cámara."
                page.update()
                return

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame = cv2.flip(frame, 1)

                face_locations = face_recognition.face_locations(frame)
                if face_locations:
                    for face_location in face_locations:
                        face_frame_encodings = face_recognition.face_encodings(frame, known_face_locations=[face_location])[0]
                        result = face_recognition.compare_faces([face_imagen_encodings], face_frame_encodings)

                        if result[0]:
                            texto.value = "Eres la misma persona"
                            page.update()
                            cap.release()
                            cv2.destroyAllWindows()
                            return
                        else:
                            texto.value = "No eres la misma persona"
                            page.update()

                        cv2.rectangle(frame, (face_location[3], face_location[0]), (face_location[1], face_location[2]), (255, 0, 0), 2)

                cv2.imshow("Frame", frame)

                if cv2.waitKey(1) & 0xFF == 27:
                    break

            cap.release()
            cv2.destroyAllWindows()

        except Exception as e:
            texto.value = f"Error al procesar la cédula: {str(e)}"
            page.update()

    def iniciar_reconocimiento(identificacion):
        thread = threading.Thread(target=reconocimiento, args=(identificacion,))
        thread.start()

    def boton_click(e):
        iniciar_reconocimiento(input_identificacion.value)

    boton = ft.ElevatedButton(text="Iniciar reconocimiento", on_click=boton_click)
    page.add(texto, input_identificacion, boton)

ft.app(target=main)