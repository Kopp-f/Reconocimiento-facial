import sqlite3
class ContactManager:
    def __init__(self):
        self.connection = sqlite3.connect("data.db", check_same_thread=False)

    def add_contact(self, name, age, email, phone):
        query = '''INSERT INTO datos (NOMBRE, EDAD, CORREO, TELEFONO, ) 
                   VALUES (?, ?, ?, ?, ?)'''
        self.connection.execute(query, (name, age, email, phone))
        self.connection.commit()

    def get_contacts(self):
        cursor = self.connection.cursor()
        query = "SELECT * FROM datos"
        cursor.execute(query)
        contacts = cursor.fetchall()
        return contacts

    def delete_contact(self, name):
        query = "DELETE FROM datos WHERE NOMBRE = ?"
        self.connection.execute(query, (name,))
        self.connection.commit()

    def update_contact(self, contact_id, name, age, email, phone, image_path=None):
        query = '''UPDATE datos SET NOMBRE = ?, EDAD = ?, CORREO = ?, TELEFONO = ?'''
        params = [name, age, email, phone]
        self.connection.execute(query, tuple(params))
        self.connection.commit()

    def close_connection(self):
        self.connection.close()
        print("Conexión cerrada")