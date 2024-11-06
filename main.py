import cv2
import face_recognition
import threading
import flet as ft 
from contact_manager import ContactManager
from fpdf import FPDF
import pandas as pd
import datetime
import os
 
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Tabla de Datos', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def reconocimiento(identificacion, texto, page):
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


    

class FormUi(ft.UserControl):
    
    def __init__(self, page):
        
        super().__init__(expand=True)
        self.page = page 
        self.data = ContactManager()
        self.selected_row = None

        self.name = ft.TextField(label="Nombre", border_color= "#00a9c7",bgcolor ="white",border_radius=15,color="black", hover_color="#e9fdff")
        self.age = ft.TextField(label="Edad", border_color= "#00a9c7", bgcolor ="white",border_radius=15,
                                input_filter=ft.NumbersOnlyInputFilter(),
                                max_length =2,color="black",hover_color="#e9fdff")
        self.email =ft.TextField(label="Numero de identificación", border_color= "#00a9c7", bgcolor ="white",border_radius=15,color="black",hover_color="#e9fdff")
        self.phone = ft.TextField(label="Telefono", border_color= "#00a9c7",bgcolor ="white",border_radius=15,
                                  input_filter=ft.NumbersOnlyInputFilter(),
                                  max_length=11,color="black",hover_color="#e9fdff")
        
        self.searh_field = ft.TextField(                        
                            suffix_icon = ft.icons.SEARCH,
                            border_radius=15,
                            label= "Buscar aprendiz",
                            bgcolor="white",
                            border= ft.InputBorder.OUTLINE,
                            border_color= "black",
                            
                            label_style = ft.TextStyle(color= "black"),
                            on_change = self.searh_data,
                        )     
      
        self.data_table =  ft.DataTable(
                            expand= True,
                            bgcolor="white",
                            
                            
                            border=ft.border.all(2, "#00a9c7"),
                            data_row_color = { ft.MaterialState.SELECTED: "#00a9c7", ft.MaterialState.PRESSED: "#5eb6c2"},
                            border_radius=10,
                            show_checkbox_column = True,
                            columns=[
                                ft.DataColumn(ft.Text("Nombre", color="black", )),
                                ft.DataColumn(ft.Text("Edad", color="black", )),
                                ft.DataColumn(ft.Text("Correo", color="black", ), numeric=True),
                                ft.DataColumn(ft.Text("Telefono", color="black", ), numeric=True ),
                            ],
                        )        
        
       
        self.show_data()


        self.form = ft.Container(
    bgcolor="white",
    border_radius=10,
    border=ft.border.all(2, "#008a90"),  # Borde negro de grosor 2
    col=4,
    padding=10,
    content=ft.Column(
        alignment=ft.MainAxisAlignment.SPACE_AROUND,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text(
                "INGRESE SUS DATOS ",
                size=30,
                text_align="center",
            ),
            self.name,
            self.age,
            self.email,
            self.phone,
            ft.Container(
                content=ft.Row(
                    spacing=35,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.TextButton(
                            text="Guardar",
                            icon=ft.icons.SAVE,
                            icon_color="#10884f",
                            style=ft.ButtonStyle(color="black",bgcolor="#e6e6e6" ),
                            on_click=self.add_data,
                        ),
                        ft.TextButton(
                            text="Actualizar",
                            icon=ft.icons.UPDATE,
                            icon_color="#2f4858",
                            style=ft.ButtonStyle(color="black",bgcolor="#e6e6e6"  ),
                            on_click=self.update_data,
                        ),
                        ft.TextButton(
                            text="Borrar",
                            icon=ft.icons.DELETE,
                            icon_color="#e65959",
                            style=ft.ButtonStyle(color="black" ,bgcolor="#e6e6e6"),
                            on_click=self.delete_data,
                        ),
                    ]
                )
            )
        ]
    )
)


        self.table = ft.Container(
            bgcolor= "white",
            border=ft.border.all(2, "#008a90"), 
            border_radius=10,
            padding= 10,
            col = 8,
            content= ft.Column(   
                expand=True,           
                controls=[
                    ft.Container(
                        padding = 10,
                        content= ft.Row(
                            controls=[
                                self.searh_field,
                                ft.IconButton(
                                    icon= ft.icons.EDIT_SQUARE,
                                    on_click= self.edit_flied_text,
                                    icon_color= "#eee8a9",
                                ),
                                ft.IconButton(tooltip="Descargar en PDF",
                                            icon = ft.icons.PICTURE_AS_PDF,
                                            icon_color= "#00a9c7",
                                            on_click= self.save_pdf,
                                            ),     
                                ft.IconButton(tooltip="Descargar en EXCEL",
                                        icon = ft.icons.TABLE_ROWS_OUTLINED,
                                        icon_color= "#10884f",
                                        on_click= self.save_excel,
                                        ),  
                            ]
                        ),
                    ),

                    ft.Column(
                        expand= True, 
                        scroll="auto",
                        controls=[
                        ft.ResponsiveRow([
                            self.data_table
                            ]),
                        ]
                    )
                ]
            )
        )
        self.conent = ft.ResponsiveRow(
            controls=[
                self.form,
                self.table
            ]
        )
    
    def show_data(self):
        self.data_table.rows = []
        for x in self.data.get_contacts():
            self.data_table.rows.append(
                ft.DataRow(
                    on_select_changed= self.get_index, 
                    cells=[
                        ft.DataCell(ft.Text(x[1],color="black")),  
                        ft.DataCell(ft.Text(str(x[2]),color="black")),  
                        ft.DataCell(ft.Text(x[3],color="black")),
                        ft.DataCell(ft.Text(str(x[4]),color="black")),  
                    ]
                )
            )
        self.update()

    def add_data(self, e):
        name = self.name.value
        age = str(self.age.value)
        email = self.email.value
        phone = str(self.phone.value)

        if len(name) and len(age) and len(email) and len(phone) > 0:
            contact_exists = False
            for row in self.data.get_contacts():
                if row[1] == name:
                    contact_exists = True
                    break

            if not contact_exists:
                # Limpiar campos de entrada
                self.clean_fields()

                # Mostrar alerta con instrucciones para la captura de foto
                self.show_capture_alert(email)

            else:
                print("El contacto ya existe en la base de datos.")
        else:
            print("Por favor, completa todos los campos antes de agregar.")

    def show_capture_alert(self, email):
        # Crear el diálogo de alerta
        dialog = ft.AlertDialog(
            title=ft.Text("Captura de foto"),
            content=ft.Text("Para capturar la foto, presiona ESPACIO.\nPara salir sin capturar, presiona ESC."),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self.start_capture(email)),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def start_capture(self, email):
        # Cerrar el diálogo
        self.page.dialog.open = False
        self.page.update()  # Actualiza la página para reflejar el cambio

        # Iniciar la captura de imagen
        self.capture_image(email)

    def capture_image(self, email):
        cap = cv2.VideoCapture(0)
        count = 0

        if not os.path.exists('imagenes'):
            os.makedirs('imagenes')

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cv2.imshow('Capturando Imágenes', frame)
            k = cv2.waitKey(1)
            if k % 256 == 27:  # Presionar 'ESC' para salir
                break
            elif k % 256 == 32:  # Presionar 'ESPACIO' para capturar
                img_name = f"imagenes/{email}_{count}.jpg"
                cv2.imwrite(img_name, frame)
                print(f"{img_name} Guardado!")
                count += 1
                break  # Capturamos una sola imagen

        cap.release()
        cv2.destroyAllWindows()
        

    def get_index(self, e):
        if e.control.selected:
           e.control.selected = False
        else: 
            e.control.selected = True
        name = e.control.cells[0].content.value
        for row in self.data.get_contacts():
            if row[1] == name:
                self.selected_row = row
                break
        self.update()

    def edit_flied_text(self, e):
        try: 
            self.name.value = self.selected_row[1]
            self.age.value = self.selected_row[2]
            self.email.value = self.selected_row[3]
            self.phone.value = self.selected_row[4]   
            self.update()
        except TypeError:
            print("Error")

    def update_data(self,e):
        name = self.name.value
        age = str(self.age.value)
        email = self.email.value
        phone = str(self.phone.value)

        if len(name) and len(age) and len(email) and len(phone) >0:
            self.clean_fields()
            self.data.update_contact(self.selected_row[0], name, age, email, phone)
            self.show_data()

    def delete_data(self, e):
        self.data.delete_contact(self.selected_row[1])
        self.show_data()

    def  searh_data(self, e):
        search = self.searh_field.value.lower()
        name = list(filter(lambda x: search in x[1].lower(), self.data.get_contacts()))
        self.data_table.rows = []
        if not self.searh_field.value == "":
            if len(name)>0:
                for x in name:
                    self.data_table.rows.append(
                        ft.DataRow(
                            on_select_changed=  self.get_index,
                            cells=[
                                ft.DataCell(ft.Text(x[1],color="black")),  
                                ft.DataCell(ft.Text(str(x[2]),color="black")),  
                                ft.DataCell(ft.Text(x[3],color="black")), 
                                ft.DataCell(ft.Text(str(x[4]),color="black")),  
                            ]
                        )
                    )
                    self.update()
        else:
            self.show_data()   

    def clean_fields(self):
        self.name.value = ""
        self.age.value = ""
        self.email.value = ""
        self.phone.value = ""      
        self.update() 
   
    def save_pdf(self, e):
        pdf = PDF()
        pdf.add_page()
        column_widths = [10,40, 20, 80, 40]
        # Agregar filas a la tabla
        data = self.data.get_contacts()
        header = ("ID", "NOMBRE", "EDAD", "CORREO", "TELEFONO")
        data.insert(0, header)
        for row in data:
            for item, width in zip(row, column_widths):
                pdf.cell(width, 10, str(item), border=1)
            pdf.ln()
        file_name =  datetime.datetime.now()
        file_name = file_name.strftime("DATA %Y-%m-%d_%H-%M-%S") + ".pdf"
        pdf.output(file_name)        

    def save_excel(self, e):
        file_name =  datetime.datetime.now()
        file_name = file_name.strftime("DATA %Y-%m-%d_%H-%M-%S") + ".xlsx"
        contacts = self.data.get_contacts()
        df = pd.DataFrame(contacts, columns=["ID", "Nombre", "Edad", "Correo", "Teléfono"])
        df.to_excel(file_name, index=False)

    def build(self):
        return self.conent



def main(page: ft.Page):
    import flet as ft
    

    page.title = "F.R.O.A"
    page.fonts = {
        "Kanit": "https://raw.githubusercontent.com/google/fonts/master/ofl/kanit/Kanit-Bold.ttf",
        "Aleo Bold Italic": "https://raw.githubusercontent.com/google/fonts/master/ofl/aleo/Aleo-BoldItalic.ttf",
        "Aleo Bold": "https://raw.githubusercontent.com/google/fonts/master/ofl/aleo",
    }
    page.update()
    page.theme = ft.Theme(font_family="Aleo Bold Italic")

    # Función para manejar el cambio de rutas
    def route_change(e):
        page.views.clear()  # Limpiar las vistas actuales

        # Vista principal (home)
        if page.route == "/":
            page.views.append(
                ft.View(
                    "/",
                    [
                        ft.AppBar(
                            title=ft.Text("Pagina principal"),
                            bgcolor="#00333e",
                        ),
                        ft.Container(
                            alignment=ft.alignment.center,
                            height=page.window_height,
                              # Centrar el contenedor
                            content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,  # Alinear al centro
                            controls=[
                            ft.Column(
                                controls=[
                                    ft.Text("Bienvenido a F.R.O.A", size=80, weight=ft.FontWeight.BOLD, color="#00a9c7"),
                                    ft.Text("Facial recognition of assists", color="#95b0b4", size=40, italic=True),
                                    
                                    ft.Row(
                                        
                                        controls=[
                                            
                                            ft.TextButton(
                                                "Registrar", 
                                                style=ft.ButtonStyle(color="black", bgcolor="#d9edff"),
                                                icon=ft.icons.CAMERA_ALT,
                                                icon_color="#357db6", 
                                                on_click=lambda _: page.go("/store"),
                                                
                                                
                                            ),
                                            
                                            
                                            
                                            ft.TextButton(
                                                "Tomar asistencia", 
                                                style=ft.ButtonStyle(color="black", bgcolor="#d9edff",),
                                                icon=ft.icons.CHECKLIST,
                                                icon_color="#7ed486", 
                                                
                                                on_click=lambda _: page.go("/registrar"),
                                            ),
                                        ],
                                    ),
                                    
                                ],
                                
                                alignment=ft.MainAxisAlignment.CENTER,  # Centrar el contenido del Column
                            ),
                            
                            
                        ],
                        
                    ),
                ),
            ],
            bgcolor="white"
        )
    )
                       
                    

        # Vista de la tienda (donde estará el formulario)
        elif page.route == "/store":
            page.views.append(
                ft.View(
                    "/store",
                    [
                        ft.AppBar(
                            title=ft.Text("TOMA DE ASISTENCIA"),
                            bgcolor="#00333e",
                        ),
                        FormUi(page),  # Incluir el formulario dentro de esta vista
                        ft.Row(
                            [
                                ft.TextButton(
                                    text="Salir",
                                    icon=ft.icons.EXIT_TO_APP_ROUNDED,
                                    icon_color="red",
                                    style=ft.ButtonStyle(color="black", bgcolor="#e6e6e6"),
                                    on_click=lambda _: page.go("/")
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END  # Botón salir alineado a la derecha
                        ),
                    ],
                    
                    bgcolor="white"
                )
            )
            
            
        elif page.route == "/registrar":
            # Crear el campo de texto y otros controles
            texto = ft.Text(value="Introduce la cédula y haz clic en el botón", size=30)
            input_identificacion = ft.TextField(label="Ingresa tu cédula", width=200)

            def iniciar_reconocimiento():
                identificacion = input_identificacion.value
                if identificacion:
                    texto.value = f"Realizando reconocimiento para: {identificacion}"
                    page.update()
                    thread = threading.Thread(target=reconocimiento, args=(identificacion, texto, page))
                    thread.start()
                else:
                    texto.value = "Por favor, ingresa una cédula válida."
                    page.update()

            # Crear la vista con el formulario
            page.views.append(
                ft.View(
                    "/registrar",
                    [
                        ft.AppBar(
                            title=ft.Text("TOMA DE ASISTENCIA"),
                            bgcolor="#00333e",
                        ),
                        ft.Container(
                            content=ft.Column(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    texto,
                                    input_identificacion,
                                    ft.ElevatedButton(
                                        text="Iniciar reconocimiento",
                                        on_click=lambda _: iniciar_reconocimiento(),
                                    ),
                                ],
                            ),
                            alignment=ft.alignment.center,
                        ),
                        ft.Row(
                            [
                                ft.TextButton(
                                    text="Salir",
                                    icon=ft.icons.EXIT_TO_APP_ROUNDED,
                                    icon_color="red",
                                    style=ft.ButtonStyle(color="black", bgcolor="#e6e6e6"),
                                    on_click=lambda _: page.go("/"),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                    bgcolor="white",
                )
            )

        page.update()  # Refrescar la página para que refleje los cambios de vista

    import threading

    # Función para manejar la navegación de "pop" (volver)
    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
     
    def iniciar_reconocimiento(identificacion):
        texto = ft.Text(value="Realizando reconocimiento para: " + identificacion, size=30)
        thread = threading.Thread(target=reconocimiento, args=(identificacion, texto, page))
        thread.start()
        page.update()

    def boton_click(e):
        identificacion = page.get_control("input_identificacion").value
        iniciar_reconocimiento(identificacion)

    # Asignar funciones a eventos de cambio de ruta
    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Iniciar en la ruta actual
    page.go(page.route)


# Iniciar la aplicación con la función main
ft.app(target=main)
