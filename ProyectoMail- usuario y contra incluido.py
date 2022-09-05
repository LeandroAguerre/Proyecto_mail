#importar módulo tkinter
from tkinter import ttk
from tkinter import *
#importar módulo sql base de datos
import sqlite3
import smtplib


#Usuario de prueba
# Pruebaproyectomail1@gmail.com
# Pruebaproyectomail1@ pass
#Contraseña de app google
# windows:   zuorvgamhywxucaz
# linux:    ijegjzqntqbroinu
#NOTA: Google te obliga a crear contraseñas para aplicaciones inseguras para no dar
#tu contraseña oficial. Generás una para cada app y sistema operativo para hacer seguimiento
#a los inicios de sesión


class Contacto:
    # Base de datos
    db_name = 'database.db'

    def __init__(self, window):
        # ventana
        self.wind = window
        self.wind.title('Contactos')

        #Creando un contenedor frame
        frame = LabelFrame(self.wind, text = 'Agregar contacto')
        frame.grid(row = 0, column = 0, columnspan = 3, pady = 20)

        #Input o entrada nombre
        Label(frame, text = 'Nombre :').grid(row = 1, column = 0)
        self.nombre = ttk.Entry(frame)
        self.nombre.focus()
        self.nombre.grid(row = 1, column = 1)

        # Input correo
        Label(frame, text = 'Correo: ').grid(row = 2, column = 0)
        self.correo = ttk.Entry(frame)
        self.correo.grid(row = 2, column = 1)

        #Botón agregar contacto
        ttk.Button(frame, text = 'Guardar Contacto', command = self.add_contacto).grid(row = 3, columnspan = 2, sticky = W + E)

        # mensaje
        self.message = Label(text = '', fg = 'red')
        self.message.grid(row = 3, column = 0, columnspan = 2, sticky = W + E)

        #Tabla #columnspan espaciado 
        self.tree = ttk.Treeview(height = 10, columns = 2)
        self.tree.grid(row = 4, column = 0, columnspan = 3)
        self.tree.heading('#0', text = 'Nombre', anchor = CENTER)
        self.tree.heading('#1', text = 'Correo', anchor = CENTER)

        # Botones eliminar y editar
        ttk.Button(text = 'ELIMINAR', command = self.eliminar_contacto).grid(row = 5, column = 0, sticky = W + E)
        ttk.Button(text = 'EDITAR', command = self.editar_contacto).grid(row = 5, column = 1, sticky = W + E)
        ttk.Button(text = 'ENVIAR MENSAJE', command = self.enviar_mensaje).grid(row = 5, column = 2, sticky = W + E)

        self.get_contacto()

    #función para la base de datos, "ejecutar consulta" - "run query"
    def run_query(self, query, parameters = ()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
        return result

    #get_contacto va a hacer la consulta y nos va a mostrar los datos de la db
    def get_contacto(self):
        # cleaning Table 
        guardados = self.tree.get_children()
        for elemento in guardados:
            self.tree.delete(elemento)
        # obteniendo datos
        query = 'SELECT * FROM contactos ORDER BY nombre DESC'
        db_rows = self.run_query(query)
        # mostrando datos
        for row in db_rows:
            self.tree.insert('', 0, text = row[1], values = row[2])

    #validar que los campos no estén vacios del entry
    def validation(self):
        return len(self.nombre.get()) != 0 and len(self.correo.get()) != 0

    #agregar contacto, obtiene los valores solo si validations es true
    def add_contacto(self):
        if self.validation():
            query = 'INSERT INTO contactos VALUES(NULL, ?, ?)'
            parameters =  (self.nombre.get(), self.correo.get())
            self.run_query(query, parameters)
            self.message['text'] = 'Contacto {} agregado'.format(self.nombre.get())
            self.nombre.delete(0, END)
            self.correo.delete(0, END)
        else:
            self.message['text'] = 'Se requiere nombre y correo'
        self.get_contacto()

    #eliminar contacto
    def eliminar_contacto(self):
        self.message['text'] = ''
        try:
           self.tree.item(self.tree.selection())['text'][0]
        except IndexError as e:
            self.message['text'] = 'Elige un contacto'
            return
        self.message['text'] = ''
        nombre = self.tree.item(self.tree.selection())['text']
        query = 'DELETE FROM contactos WHERE nombre = ?'
        self.run_query(query, (nombre, ))
        self.message['text'] = 'Contacto {} borrado'.format(nombre)
        self.get_contacto()

    #editar contacto
    def editar_contacto(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError as e:
            self.message['text'] = 'Elige un contacto'
            return
        nombre = self.tree.item(self.tree.selection())['text']
        old_correo = self.tree.item(self.tree.selection())['values'][0]
        self.edit_wind = Toplevel()
        self.edit_wind.title = 'Editar contacto'
        # NOmbre actual
        Label(self.edit_wind, text = 'Nombre actual').grid(row = 0, column = 1)
        Entry(self.edit_wind, textvariable = StringVar(self.edit_wind, value = nombre), state = 'readonly').grid(row = 0, column = 2)
        # Nuevo nombre
        Label(self.edit_wind, text = 'Nuevo nombre').grid(row = 1, column = 1)
        new_nombre = Entry(self.edit_wind)
        new_nombre.grid(row = 1, column = 2)

        # Correo actual 
        Label(self.edit_wind, text = 'Correo actual').grid(row = 2, column = 1)
        Entry(self.edit_wind, textvariable = StringVar(self.edit_wind, value = old_correo), state = 'readonly').grid(row = 2, column = 2)
        # Nuevo correo
        Label(self.edit_wind, text = 'Nuevo correo').grid(row = 3, column = 1)
        new_correo= Entry(self.edit_wind)
        new_correo.grid(row = 3, column = 2)

        Button(self.edit_wind, text = 'Guardar', command = lambda: self.edit_guardado(new_nombre.get(), nombre, new_correo.get(), old_correo)).grid(row = 4, column = 2, sticky = W)
        self.edit_wind.mainloop()

    def edit_guardado(self, new_nombre, nombre, new_correo, old_correo):
        query = 'UPDATE contactos SET nombre = ?, correo = ? WHERE nombre = ? AND correo = ?'
        parameters = (new_nombre, new_correo,nombre, old_correo)
        self.run_query(query, parameters)
        self.edit_wind.destroy()
        self.message['text'] = 'Contacto {} actualizado'.format(nombre)
        self.get_contacto()



    #nueva ventana- enviar mensaje
    def enviar_mensaje(self):
        new_ventana = Toplevel()
        new_ventana.geometry("405x400")
        new_ventana.title("Enviar Mensaje")
        
            #Funciones
            #Enviar
        def send():
            try: 
                username = temp_username.get()
                password = temp_password.get()
                to       = temp_receiver.get()
                subject  = temp_subject.get()
                body     = textEntry.get(1.0, "end-1c")
                if username=="" or password=="" or to=="" or subject=="" or body=="":
                        notif.config(text="Se requieren todos los campos", fg="red")
                        return
                else:
                        finalMessage = 'Subject: {}\n\n{}'.format(subject, body)
                        server   = smtplib.SMTP('smtp.gmail.com',587)
                        server.starttls()
                        server.login(username, password)
                        server.sendmail(username,to,finalMessage)
                        notif.config(text="Email fué enviado", fg="green")
            except:
                notif.config(text="Error enviando email", fg="red")

            #reiniciar
        def reset():
            usernameEntry.delete(0,'end')
            passwordEntry.delete(0,'end')
            receiverEntry.delete(0,'end')
            subjectEntry.delete(0,'end')
            textEntry.delete(1.0, 'end-1c')

        

        #Labels de la app
        Label(new_ventana, text="Enviar Correo", font=('',15)).grid(row=0, sticky=N)
        Label(new_ventana, text="Todos los campos son obligatorios.", font=('',11)).grid(row=1, sticky=W, padx=5 ,pady=10)

        Label(new_ventana, text="Email:", font=('', 9)).grid(row=2,sticky=W, padx=5)
        Label(new_ventana, text="Contraseña:", font=('', 9)).grid(row=3,sticky=W, padx=5)
        Label(new_ventana, text="Para:", font=('', 9)).grid(row=4,sticky=W, padx=5)
        Label(new_ventana, text="Asunto:", font=('', 9)).grid(row=5,sticky=W, padx=5)
        Label(new_ventana, text="Mensaje:", font=('', 9)).grid(row=6,sticky=W, padx=5)
        notif = Label(new_ventana, text="", font=('', 9),fg="red")
        notif.grid(row=6, column=0)

        #Temporal
        temp_username = StringVar()
        temp_password = StringVar()
        temp_receiver = StringVar()
        temp_subject  = StringVar()
        # temp_body     = StringVar()

        #Entries de la app
        usernameEntry = ttk.Entry(new_ventana, textvariable = temp_username, width=45)
        usernameEntry.grid(row=2,column=0,sticky= E)
        usernameEntry.insert(0,"Pruebaproyectomail1@gmail.com")
        passwordEntry = ttk.Entry(new_ventana, show="*", textvariable = temp_password, width=45)
        passwordEntry.grid(row=3,column=0, sticky= E)
        passwordEntry.insert(0,"zuorvgamhywxucaz")
        receiverEntry  = ttk.Entry(new_ventana, textvariable = temp_receiver, width=45)
        receiverEntry.grid(row=4,column=0, sticky= E)
        subjectEntry  = ttk.Entry(new_ventana, textvariable = temp_subject, width=45)
        subjectEntry.grid(row=5,column=0, sticky= E)
        # bodyEntry     = ttk.Entry(new_ventana, textvariable = temp_body)
        # bodyEntry.grid(row=6,column=0)
        textEntry = Text(new_ventana, width=50, height=11)
        textEntry.grid(row=7, column=0)



        #Botones
        ttk.Button(new_ventana,width=21, text = "Enviar", command = send).place(x=0, y=375)
        ttk.Button(new_ventana,width=21, text = "Reiniciar", command = reset).place(x=135, y=375)
        ttk.Button(new_ventana,width=21, text = "Cerrar", command = new_ventana.destroy).place(x=270, y=375)
        # ttk.Button(new_ventana, text = "Prueba", command = "").place(x=5, y=375)

    
if __name__ == '__main__':
    window = Tk()
    application = Contacto(window)
    window.mainloop()



