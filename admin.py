import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter import font
import sys
import os

try:
    from models import *  # Importa todas las clases y configuración de la base de datos
except ImportError:
    messagebox.showerror("Error", "No se pudo importar el archivo de modelos. Asegúrate de que esté en la misma carpeta.")
    sys.exit()

class AdminCursos:
    def __init__(self, root):
        self.root = root
        self.root.title("Administrador de Cursos")
        self.root.geometry("800x600")
        
        # Crear el notebook (pestañas)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Crear las pestañas
        self.crear_pestana_cursos()
        self.crear_pestana_capitulos()
        self.crear_pestana_lecciones()
        self.crear_pestana_recursos()
        
    def crear_pestana_cursos(self):
        # Frame para la pestaña de cursos
        frame_cursos = ttk.Frame(self.notebook)
        self.notebook.add(frame_cursos, text="Cursos")
        
        # Frame para el formulario
        form_frame = ttk.LabelFrame(frame_cursos, text="Crear Nuevo Curso", padding=10)
        form_frame.pack(fill="x", padx=10, pady=5)
        
        # Campos del formulario
        ttk.Label(form_frame, text="Nombre del Curso:").grid(row=0, column=0, sticky="w", pady=2)
        self.curso_nombre = ttk.Entry(form_frame, width=50)
        self.curso_nombre.grid(row=0, column=1, pady=2, padx=(10, 0))
        
        ttk.Label(form_frame, text="Duración (minutos):").grid(row=1, column=0, sticky="w", pady=2)
        self.curso_duracion = ttk.Entry(form_frame, width=20)
        self.curso_duracion.grid(row=1, column=1, sticky="w", pady=2, padx=(10, 0))
        
        ttk.Label(form_frame, text="URL Imagen:").grid(row=2, column=0, sticky="w", pady=2)
        self.curso_imagen = ttk.Entry(form_frame, width=50)
        self.curso_imagen.grid(row=2, column=1, pady=2, padx=(10, 0))
        
        ttk.Label(form_frame, text="ID del Autor:").grid(row=3, column=0, sticky="w", pady=2)
        self.curso_autor = ttk.Entry(form_frame, width=20)
        self.curso_autor.grid(row=3, column=1, sticky="w", pady=2, padx=(10, 0))
        
        # Botón para crear curso
        ttk.Button(form_frame, text="Crear Curso", command=self.crear_curso).grid(row=4, column=1, pady=10, sticky="w", padx=(10, 0))
        
        # Lista de cursos existentes
        lista_frame = ttk.LabelFrame(frame_cursos, text="Cursos Existentes", padding=10)
        lista_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Treeview para mostrar cursos
        self.tree_cursos = ttk.Treeview(lista_frame, columns=("ID", "Nombre", "Duración", "Autor"), show="headings")
        self.tree_cursos.heading("ID", text="ID")
        self.tree_cursos.heading("Nombre", text="Nombre")
        self.tree_cursos.heading("Duración", text="Duración")
        self.tree_cursos.heading("Autor", text="Autor ID")
        
        self.tree_cursos.column("ID", width=50)
        self.tree_cursos.column("Nombre", width=300)
        self.tree_cursos.column("Duración", width=100)
        self.tree_cursos.column("Autor", width=100)
        
        self.tree_cursos.pack(fill="both", expand=True)
        
        # Botón para actualizar lista
        ttk.Button(lista_frame, text="Actualizar Lista", command=self.actualizar_cursos).pack(pady=5)
        
        # Cargar cursos al inicio
        self.actualizar_cursos()
    
    def crear_pestana_capitulos(self):
        frame_capitulos = ttk.Frame(self.notebook)
        self.notebook.add(frame_capitulos, text="Capítulos")
        
        # Formulario para crear capítulos
        form_frame = ttk.LabelFrame(frame_capitulos, text="Crear Nuevo Capítulo", padding=10)
        form_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(form_frame, text="ID del Curso:").grid(row=0, column=0, sticky="w", pady=2)
        self.cap_curso_id = ttk.Entry(form_frame, width=20)
        self.cap_curso_id.grid(row=0, column=1, sticky="w", pady=2, padx=(10, 0))
        
        ttk.Label(form_frame, text="Nombre del Capítulo:").grid(row=1, column=0, sticky="w", pady=2)
        self.cap_nombre = ttk.Entry(form_frame, width=50)
        self.cap_nombre.grid(row=1, column=1, pady=2, padx=(10, 0))
        
        ttk.Label(form_frame, text="Número del Capítulo:").grid(row=2, column=0, sticky="w", pady=2)
        self.cap_numero = ttk.Entry(form_frame, width=20)
        self.cap_numero.grid(row=2, column=1, sticky="w", pady=2, padx=(10, 0))
        
        ttk.Button(form_frame, text="Crear Capítulo", command=self.crear_capitulo).grid(row=3, column=1, pady=10, sticky="w", padx=(10, 0))
        
        # Lista de capítulos
        lista_frame = ttk.LabelFrame(frame_capitulos, text="Capítulos Existentes", padding=10)
        lista_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.tree_capitulos = ttk.Treeview(lista_frame, columns=("ID", "Nombre", "Número", "Curso"), show="headings")
        self.tree_capitulos.heading("ID", text="ID")
        self.tree_capitulos.heading("Nombre", text="Nombre")
        self.tree_capitulos.heading("Número", text="Número")
        self.tree_capitulos.heading("Curso", text="Curso ID")
        
        self.tree_capitulos.pack(fill="both", expand=True)
        ttk.Button(lista_frame, text="Actualizar Lista", command=self.actualizar_capitulos).pack(pady=5)
        
        self.actualizar_capitulos()
    
    def crear_pestana_lecciones(self):
        frame_lecciones = ttk.Frame(self.notebook)
        self.notebook.add(frame_lecciones, text="Lecciones")
        
        # Formulario para crear lecciones
        form_frame = ttk.LabelFrame(frame_lecciones, text="Crear Nueva Lección", padding=10)
        form_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(form_frame, text="ID del Capítulo:").grid(row=0, column=0, sticky="w", pady=2)
        self.lec_capitulo_id = ttk.Entry(form_frame, width=20)
        self.lec_capitulo_id.grid(row=0, column=1, sticky="w", pady=2, padx=(10, 0))
        
        ttk.Label(form_frame, text="Nombre de la Lección:").grid(row=1, column=0, sticky="w", pady=2)
        self.lec_nombre = ttk.Entry(form_frame, width=50)
        self.lec_nombre.grid(row=1, column=1, pady=2, padx=(10, 0))
        
        ttk.Label(form_frame, text="Número:").grid(row=2, column=0, sticky="w", pady=2)
        self.lec_numero = ttk.Entry(form_frame, width=20)
        self.lec_numero.grid(row=2, column=1, sticky="w", pady=2, padx=(10, 0))
        
        ttk.Label(form_frame, text="Duración (min):").grid(row=0, column=2, sticky="w", pady=2, padx=(20, 0))
        self.lec_duracion = ttk.Entry(form_frame, width=20)
        self.lec_duracion.grid(row=0, column=3, sticky="w", pady=2, padx=(10, 0))
        
        ttk.Label(form_frame, text="Créditos:").grid(row=1, column=2, sticky="w", pady=2, padx=(20, 0))
        self.lec_creditos = ttk.Entry(form_frame, width=20)
        self.lec_creditos.grid(row=1, column=3, sticky="w", pady=2, padx=(10, 0))
        
        ttk.Label(form_frame, text="Tema:").grid(row=2, column=2, sticky="w", pady=2, padx=(20, 0))
        self.lec_tema = ttk.Entry(form_frame, width=20)
        self.lec_tema.grid(row=2, column=3, sticky="w", pady=2, padx=(10, 0))
        
        ttk.Label(form_frame, text="Concepto:").grid(row=3, column=0, sticky="nw", pady=2)
        self.lec_concepto = scrolledtext.ScrolledText(form_frame, width=60, height=4)
        self.lec_concepto.grid(row=3, column=1, columnspan=3, pady=2, padx=(10, 0))
        
        ttk.Button(form_frame, text="Crear Lección", command=self.crear_leccion).grid(row=4, column=1, pady=10, sticky="w", padx=(10, 0))
        
        # Lista de lecciones
        lista_frame = ttk.LabelFrame(frame_lecciones, text="Lecciones Existentes", padding=10)
        lista_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.tree_lecciones = ttk.Treeview(lista_frame, columns=("ID", "Nombre", "Número", "Tema", "Capítulo"), show="headings")
        for col in ("ID", "Nombre", "Número", "Tema", "Capítulo"):
            self.tree_lecciones.heading(col, text=col)
        
        self.tree_lecciones.pack(fill="both", expand=True)
        ttk.Button(lista_frame, text="Actualizar Lista", command=self.actualizar_lecciones).pack(pady=5)
        
        self.actualizar_lecciones()
    
    def crear_pestana_recursos(self):
        frame_recursos = ttk.Frame(self.notebook)
        self.notebook.add(frame_recursos, text="Recursos")
        
        # Formulario para crear recursos
        form_frame = ttk.LabelFrame(frame_recursos, text="Crear Nuevo Recurso", padding=10)
        form_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(form_frame, text="ID de la Lección:").grid(row=0, column=0, sticky="w", pady=2)
        self.rec_leccion_id = ttk.Entry(form_frame, width=20)
        self.rec_leccion_id.grid(row=0, column=1, sticky="w", pady=2, padx=(10, 0))
        
        ttk.Label(form_frame, text="Tipo:").grid(row=1, column=0, sticky="w", pady=2)
        self.rec_tipo = ttk.Combobox(form_frame, values=["Visual", "Auditivo", "Kinestésico"], width=20)
        self.rec_tipo.grid(row=1, column=1, sticky="w", pady=2, padx=(10, 0))
        
        ttk.Label(form_frame, text="Afinación:").grid(row=2, column=0, sticky="w", pady=2)
        self.rec_afinacion = ttk.Combobox(form_frame, values=["Video", "Artículo", "Texto", "Práctica", "Audio"], width=20)
        self.rec_afinacion.grid(row=2, column=1, sticky="w", pady=2, padx=(10, 0))
        
        ttk.Label(form_frame, text="Contenido (URL):").grid(row=0, column=2, sticky="w", pady=2, padx=(20, 0))
        self.rec_contenido = ttk.Entry(form_frame, width=40)
        self.rec_contenido.grid(row=0, column=3, pady=2, padx=(10, 0))
        
        ttk.Label(form_frame, text="Externo:").grid(row=1, column=2, sticky="w", pady=2, padx=(20, 0))
        self.rec_externo = ttk.Checkbutton(form_frame)
        self.rec_externo.grid(row=1, column=3, sticky="w", pady=2, padx=(10, 0))
        
        ttk.Label(form_frame, text="Descripción:").grid(row=3, column=0, sticky="nw", pady=2)
        self.rec_descripcion = scrolledtext.ScrolledText(form_frame, width=60, height=3)
        self.rec_descripcion.grid(row=3, column=1, columnspan=3, pady=2, padx=(10, 0))
        
        ttk.Button(form_frame, text="Crear Recurso", command=self.crear_recurso).grid(row=4, column=1, pady=10, sticky="w", padx=(10, 0))
        
        # Lista de recursos
        lista_frame = ttk.LabelFrame(frame_recursos, text="Recursos Existentes", padding=10)
        lista_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.tree_recursos = ttk.Treeview(lista_frame, columns=("ID", "Tipo", "Afinación", "Contenido", "Lección"), show="headings")
        for col in ("ID", "Tipo", "Afinación", "Contenido", "Lección"):
            self.tree_recursos.heading(col, text=col)
        
        self.tree_recursos.pack(fill="both", expand=True)
        ttk.Button(lista_frame, text="Actualizar Lista", command=self.actualizar_recursos).pack(pady=5)
        
        self.actualizar_recursos()
    
    # Métodos para manejar la lógica de base de datos
    def crear_curso(self):
        try:
            nombre = self.curso_nombre.get().strip()
            duracion = int(self.curso_duracion.get() or 0)
            imagen = self.curso_imagen.get().strip()
            autor_id = int(self.curso_autor.get())
            
            if not nombre:
                messagebox.showerror("Error", "El nombre del curso es obligatorio")
                return
            
            curso = Curso(
                nombre=nombre,
                duracion=duracion,
                url_imagen=imagen if imagen else None,
                autor_id=autor_id
            )
            
            session.add(curso)
            session.commit()
            
            messagebox.showinfo("Éxito", f"Curso '{nombre}' creado exitosamente")
            self.limpiar_formulario_curso()
            self.actualizar_cursos()
            
        except ValueError:
            messagebox.showerror("Error", "Verifique que los campos numéricos sean válidos")
        except Exception as e:
            session.rollback()
            messagebox.showerror("Error", f"Error al crear curso: {str(e)}")
    
    def crear_capitulo(self):
        try:
            curso_id = int(self.cap_curso_id.get())
            nombre = self.cap_nombre.get().strip()
            numero = int(self.cap_numero.get())
            
            if not nombre:
                messagebox.showerror("Error", "El nombre del capítulo es obligatorio")
                return
            
            capitulo = Capitulo(
                nombre=nombre,
                numero=numero,
                curso_id=curso_id
            )
            
            session.add(capitulo)
            session.commit()
            
            messagebox.showinfo("Éxito", f"Capítulo '{nombre}' creado exitosamente")
            self.limpiar_formulario_capitulo()
            self.actualizar_capitulos()
            
        except ValueError:
            messagebox.showerror("Error", "Verifique que los campos numéricos sean válidos")
        except Exception as e:
            session.rollback()
            messagebox.showerror("Error", f"Error al crear capítulo: {str(e)}")
    
    def crear_leccion(self):
        try:
            capitulo_id = int(self.lec_capitulo_id.get())
            nombre = self.lec_nombre.get().strip()
            numero = int(self.lec_numero.get())
            duracion = int(self.lec_duracion.get() or 0)
            creditos = int(self.lec_creditos.get() or 0)
            tema = self.lec_tema.get().strip()
            concepto = self.lec_concepto.get("1.0", tk.END).strip()
            
            if not nombre or not concepto:
                messagebox.showerror("Error", "El nombre y concepto de la lección son obligatorios")
                return
            
            leccion = Leccion(
                nombre=nombre,
                numero=numero,
                duracion=duracion if duracion else None,
                creditos=creditos if creditos else None,
                tema=tema if tema else None,
                concepto=concepto,
                capitulo_id=capitulo_id
            )
            
            session.add(leccion)
            session.commit()
            
            messagebox.showinfo("Éxito", f"Lección '{nombre}' creada exitosamente")
            self.limpiar_formulario_leccion()
            self.actualizar_lecciones()
            
        except ValueError:
            messagebox.showerror("Error", "Verifique que los campos numéricos sean válidos")
        except Exception as e:
            session.rollback()
            messagebox.showerror("Error", f"Error al crear lección: {str(e)}")
    
    def crear_recurso(self):
        try:
            leccion_id = int(self.rec_leccion_id.get())
            tipo = self.rec_tipo.get()
            afinacion = self.rec_afinacion.get()
            contenido = self.rec_contenido.get().strip()
            externo = self.rec_externo.instate(['selected'])
            descripcion = self.rec_descripcion.get("1.0", tk.END).strip()
            
            if not all([tipo, afinacion, contenido]):
                messagebox.showerror("Error", "Tipo, afinación y contenido son obligatorios")
                return
            
            recurso = Recurso(
                leccion_id=leccion_id,
                tipo=tipo,
                afinacion=afinacion,
                contenido=contenido,
                externo=externo,
                descripcion=descripcion if descripcion else None
            )
            
            session.add(recurso)
            session.commit()
            
            messagebox.showinfo("Éxito", "Recurso creado exitosamente")
            self.limpiar_formulario_recurso()
            self.actualizar_recursos()
            
        except ValueError:
            messagebox.showerror("Error", "Verifique que el ID de lección sea válido")
        except Exception as e:
            session.rollback()
            messagebox.showerror("Error", f"Error al crear recurso: {str(e)}")
    
    # Métodos para actualizar las listas
    def actualizar_cursos(self):
        for item in self.tree_cursos.get_children():
            self.tree_cursos.delete(item)
        
        try:
            cursos = session.query(Curso).all()
            for curso in cursos:
                self.tree_cursos.insert("", "end", values=(
                    curso.id, curso.nombre, curso.duracion, curso.autor_id
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar cursos: {str(e)}")
    
    def actualizar_capitulos(self):
        for item in self.tree_capitulos.get_children():
            self.tree_capitulos.delete(item)
        
        try:
            capitulos = session.query(Capitulo).all()
            for cap in capitulos:
                self.tree_capitulos.insert("", "end", values=(
                    cap.id, cap.nombre, cap.numero, cap.curso_id
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar capítulos: {str(e)}")
    
    def actualizar_lecciones(self):
        for item in self.tree_lecciones.get_children():
            self.tree_lecciones.delete(item)
        
        try:
            lecciones = session.query(Leccion).all()
            for lec in lecciones:
                self.tree_lecciones.insert("", "end", values=(
                    lec.id, lec.nombre, lec.numero, lec.tema or "", lec.capitulo_id
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar lecciones: {str(e)}")
    
    def actualizar_recursos(self):
        for item in self.tree_recursos.get_children():
            self.tree_recursos.delete(item)
        
        try:
            recursos = session.query(Recurso).all()
            for rec in recursos:
                contenido_corto = rec.contenido[:30] + "..." if len(rec.contenido) > 30 else rec.contenido
                self.tree_recursos.insert("", "end", values=(
                    rec.id, rec.tipo, rec.afinacion, contenido_corto, rec.leccion_id
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar recursos: {str(e)}")
    
    # Métodos para limpiar formularios
    def limpiar_formulario_curso(self):
        self.curso_nombre.delete(0, tk.END)
        self.curso_duracion.delete(0, tk.END)
        self.curso_imagen.delete(0, tk.END)
        self.curso_autor.delete(0, tk.END)
    
    def limpiar_formulario_capitulo(self):
        self.cap_curso_id.delete(0, tk.END)
        self.cap_nombre.delete(0, tk.END)
        self.cap_numero.delete(0, tk.END)
    
    def limpiar_formulario_leccion(self):
        self.lec_capitulo_id.delete(0, tk.END)
        self.lec_nombre.delete(0, tk.END)
        self.lec_numero.delete(0, tk.END)
        self.lec_duracion.delete(0, tk.END)
        self.lec_creditos.delete(0, tk.END)
        self.lec_tema.delete(0, tk.END)
        self.lec_concepto.delete("1.0", tk.END)
    
    def limpiar_formulario_recurso(self):
        self.rec_leccion_id.delete(0, tk.END)
        self.rec_tipo.set("")
        self.rec_afinacion.set("")
        self.rec_contenido.delete(0, tk.END)
        self.rec_externo.state(['!selected'])
        self.rec_descripcion.delete("1.0", tk.END)

if __name__ == "__main__":
    try:
        # Crear las tablas si no existen
        Base.metadata.create_all(Engine)
        
        # Crear la aplicación
        root = tk.Tk()
        app = AdminCursos(root)
        root.mainloop()
        
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        messagebox.showerror("Error", f"Error al iniciar: {e}")
    finally:
        # Cerrar la sesión de la base de datos
        if 'session' in globals():
            session.close()