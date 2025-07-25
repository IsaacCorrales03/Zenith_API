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
        self.root.geometry("900x700")
        
        # Crear el notebook (pestañas)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Crear las pestañas
        self.crear_pestana_cursos()
        self.crear_pestana_capitulos()
        self.crear_pestana_lecciones()
        self.crear_pestana_recursos()
        self.crear_pestana_parrafos()
        
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
        self.rec_afinacion = ttk.Combobox(
            form_frame,
            values=[
                "Lectura", "Graficos", "Diagramas", "Videos", "Imagenes",       # Visual
                "Escuchar_clase", "Grabaciones", "Musica", "Podcast", "Debates",  # Auditivo
                "Experimentos", "Simulaciones", "Proyectos", "Practica", "Juegos"  # Kinestésico
            ],
            width=20
        )
        self.rec_afinacion.grid(row=2, column=1, sticky="w", pady=2, padx=(10, 0))

                
        ttk.Label(form_frame, text="Contenido o URL:").grid(row=0, column=2, sticky="w", pady=2, padx=(20, 0))
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
    
    def crear_pestana_parrafos(self):
        frame_parrafos = ttk.Frame(self.notebook)
        self.notebook.add(frame_parrafos, text="Párrafos Explicativos")
        
        # Formulario para crear párrafos explicativos
        form_frame = ttk.LabelFrame(frame_parrafos, text="Crear Nuevo Párrafo Explicativo", padding=10)
        form_frame.pack(fill="x", padx=10, pady=5)
        
        # Primera fila de campos
        ttk.Label(form_frame, text="ID de la Lección:").grid(row=0, column=0, sticky="w", pady=2)
        self.par_leccion_id = ttk.Entry(form_frame, width=20)
        self.par_leccion_id.grid(row=0, column=1, sticky="w", pady=2, padx=(10, 0))
        
        ttk.Label(form_frame, text="Orden:").grid(row=0, column=2, sticky="w", pady=2, padx=(20, 0))
        self.par_orden = ttk.Entry(form_frame, width=20)
        self.par_orden.grid(row=0, column=3, sticky="w", pady=2, padx=(10, 0))
        
        # Botón para obtener próximo orden automáticamente
        ttk.Button(form_frame, text="Obtener Próximo Orden", 
                  command=self.obtener_proximo_orden).grid(row=0, column=4, pady=2, padx=(10, 0))
        
        # Campo de contenido
        ttk.Label(form_frame, text="Contenido:").grid(row=1, column=0, sticky="nw", pady=2)
        self.par_contenido = scrolledtext.ScrolledText(form_frame, width=80, height=8)
        self.par_contenido.grid(row=1, column=1, columnspan=4, pady=2, padx=(10, 0))
        
        # Botón para crear párrafo
        ttk.Button(form_frame, text="Crear Párrafo", command=self.crear_parrafo).grid(row=2, column=1, pady=10, sticky="w", padx=(10, 0))
        
        # Lista de párrafos explicativos
        lista_frame = ttk.LabelFrame(frame_parrafos, text="Párrafos Explicativos Existentes", padding=10)
        lista_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Treeview para mostrar párrafos
        self.tree_parrafos = ttk.Treeview(lista_frame, columns=("ID", "Orden", "Contenido", "Lección"), show="headings")
        self.tree_parrafos.heading("ID", text="ID")
        self.tree_parrafos.heading("Orden", text="Orden")
        self.tree_parrafos.heading("Contenido", text="Contenido")
        self.tree_parrafos.heading("Lección", text="Lección ID")
        
        self.tree_parrafos.column("ID", width=50)
        self.tree_parrafos.column("Orden", width=80)
        self.tree_parrafos.column("Contenido", width=400)
        self.tree_parrafos.column("Lección", width=100)
        
        self.tree_parrafos.pack(fill="both", expand=True)
        
        # Botones de acción
        botones_frame = ttk.Frame(lista_frame)
        botones_frame.pack(fill="x", pady=5)
        
        ttk.Button(botones_frame, text="Actualizar Lista", command=self.actualizar_parrafos).pack(side="left", padx=5)
        ttk.Button(botones_frame, text="Eliminar Párrafo", command=self.eliminar_parrafo).pack(side="left", padx=5)
        ttk.Button(botones_frame, text="Editar Párrafo", command=self.editar_parrafo).pack(side="left", padx=5)
        
        # Cargar párrafos al inicio
        self.actualizar_parrafos()
    
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
    
    def crear_parrafo(self):
        try:
            leccion_id = int(self.par_leccion_id.get())
            orden = int(self.par_orden.get())
            contenido = self.par_contenido.get("1.0", tk.END).strip()
            
            if not contenido:
                messagebox.showerror("Error", "El contenido del párrafo es obligatorio")
                return
            
            if len(contenido) > 2000:
                messagebox.showerror("Error", "El contenido no puede exceder los 2000 caracteres")
                return
            
            # Verificar si ya existe un párrafo con el mismo orden para esta lección
            parrafo_existente = session.query(ParrafoExplicativo).filter_by(
                leccion_id=leccion_id, orden=orden
            ).first()
            
            if parrafo_existente:
                messagebox.showerror("Error", f"Ya existe un párrafo con el orden {orden} para esta lección")
                return
            
            parrafo = ParrafoExplicativo(
                leccion_id=leccion_id,
                orden=orden,
                contenido=contenido
            )
            
            session.add(parrafo)
            session.commit()
            
            messagebox.showinfo("Éxito", "Párrafo explicativo creado exitosamente")
            self.limpiar_formulario_parrafo()
            self.actualizar_parrafos()
            
        except ValueError:
            messagebox.showerror("Error", "Verifique que los campos numéricos sean válidos")
        except Exception as e:
            session.rollback()
            messagebox.showerror("Error", f"Error al crear párrafo: {str(e)}")
    
    def obtener_proximo_orden(self):
        try:
            leccion_id = int(self.par_leccion_id.get())
            
            # Obtener el orden más alto para esta lección
            max_orden = session.query(func.max(ParrafoExplicativo.orden)).filter_by(
                leccion_id=leccion_id
            ).scalar()
            
            proximo_orden = (max_orden or 0) + 1
            
            self.par_orden.delete(0, tk.END)
            self.par_orden.insert(0, str(proximo_orden))
            
        except ValueError:
            messagebox.showerror("Error", "Primero ingrese un ID de lección válido")
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener próximo orden: {str(e)}")
    
    def eliminar_parrafo(self):
        seleccion = self.tree_parrafos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un párrafo para eliminar")
            return
        
        item = self.tree_parrafos.item(seleccion[0])
        parrafo_id = item['values'][0]
        
        respuesta = messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este párrafo?")
        if respuesta:
            try:
                parrafo = session.query(ParrafoExplicativo).get(parrafo_id)
                if parrafo:
                    session.delete(parrafo)
                    session.commit()
                    messagebox.showinfo("Éxito", "Párrafo eliminado exitosamente")
                    self.actualizar_parrafos()
                else:
                    messagebox.showerror("Error", "Párrafo no encontrado")
            except Exception as e:
                session.rollback()
                messagebox.showerror("Error", f"Error al eliminar párrafo: {str(e)}")
    
    def editar_parrafo(self):
        seleccion = self.tree_parrafos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un párrafo para editar")
            return
        
        item = self.tree_parrafos.item(seleccion[0])
        parrafo_id = item['values'][0]
        
        try:
            parrafo = session.query(ParrafoExplicativo).get(parrafo_id)
            if parrafo:
                # Llenar el formulario con los datos del párrafo
                self.par_leccion_id.delete(0, tk.END)
                self.par_leccion_id.insert(0, str(parrafo.leccion_id))
                
                self.par_orden.delete(0, tk.END)
                self.par_orden.insert(0, str(parrafo.orden))
                
                self.par_contenido.delete("1.0", tk.END)
                self.par_contenido.insert("1.0", parrafo.contenido)
                
                # Cambiar el botón de crear por actualizar temporalmente
                messagebox.showinfo("Modo Edición", "Los datos se han cargado en el formulario. Modifique lo necesario y haga clic en 'Actualizar Párrafo'")
                
                # Crear ventana de edición
                self.ventana_edicion_parrafo(parrafo)
                
            else:
                messagebox.showerror("Error", "Párrafo no encontrado")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar párrafo: {str(e)}")
    
    def ventana_edicion_parrafo(self, parrafo):
        # Crear ventana de edición
        ventana = tk.Toplevel(self.root)
        ventana.title("Editar Párrafo Explicativo")
        ventana.geometry("600x400")
        ventana.resizable(True, True)
        
        # Frame principal
        main_frame = ttk.Frame(ventana, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Campos de edición
        ttk.Label(main_frame, text="ID de la Lección:").grid(row=0, column=0, sticky="w", pady=2)
        leccion_entry = ttk.Entry(main_frame, width=20)
        leccion_entry.grid(row=0, column=1, sticky="w", pady=2, padx=(10, 0))
        leccion_entry.insert(0, str(parrafo.leccion_id))
        
        ttk.Label(main_frame, text="Orden:").grid(row=0, column=2, sticky="w", pady=2, padx=(20, 0))
        orden_entry = ttk.Entry(main_frame, width=20)
        orden_entry.grid(row=0, column=3, sticky="w", pady=2, padx=(10, 0))
        orden_entry.insert(0, str(parrafo.orden))
        
        ttk.Label(main_frame, text="Contenido:").grid(row=1, column=0, sticky="nw", pady=2)
        contenido_text = scrolledtext.ScrolledText(main_frame, width=70, height=15)
        contenido_text.grid(row=1, column=1, columnspan=3, pady=2, padx=(10, 0))
        contenido_text.insert("1.0", parrafo.contenido)
        
        # Frame para botones
        botones_frame = ttk.Frame(main_frame)
        botones_frame.grid(row=2, column=1, columnspan=3, pady=10)
        
        def actualizar_parrafo():
            try:
                nueva_leccion_id = int(leccion_entry.get())
                nuevo_orden = int(orden_entry.get())
                nuevo_contenido = contenido_text.get("1.0", tk.END).strip()
                
                if not nuevo_contenido:
                    messagebox.showerror("Error", "El contenido del párrafo es obligatorio")
                    return
                
                if len(nuevo_contenido) > 2000:
                    messagebox.showerror("Error", "El contenido no puede exceder los 2000 caracteres")
                    return
                
                # Verificar si el nuevo orden ya existe (solo si cambió)
                if nueva_leccion_id != parrafo.leccion_id or nuevo_orden != parrafo.orden:
                    parrafo_existente = session.query(ParrafoExplicativo).filter_by(
                        leccion_id=nueva_leccion_id, orden=nuevo_orden
                    ).first()
                    
                    if parrafo_existente and parrafo_existente.id != parrafo.id:
                        messagebox.showerror("Error", f"Ya existe un párrafo con el orden {nuevo_orden} para esta lección")
                        return
                
                # Actualizar el párrafo
                parrafo.leccion_id = nueva_leccion_id
                parrafo.orden = nuevo_orden
                parrafo.contenido = nuevo_contenido
                
                session.commit()
                
                messagebox.showinfo("Éxito", "Párrafo actualizado exitosamente")
                ventana.destroy()
                self.actualizar_parrafos()
                
            except ValueError:
                messagebox.showerror("Error", "Verifique que los campos numéricos sean válidos")
            except Exception as e:
                session.rollback()
                messagebox.showerror("Error", f"Error al actualizar párrafo: {str(e)}")
        
        def cancelar():
            ventana.destroy()
        
        ttk.Button(botones_frame, text="Actualizar", command=actualizar_parrafo).pack(side="left", padx=5)
        ttk.Button(botones_frame, text="Cancelar", command=cancelar).pack(side="left", padx=5)
    
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
    
    def actualizar_parrafos(self):
        for item in self.tree_parrafos.get_children():
            self.tree_parrafos.delete(item)
        
        try:
            parrafos = session.query(ParrafoExplicativo).order_by(
                ParrafoExplicativo.leccion_id, ParrafoExplicativo.orden
            ).all()
            
            for parrafo in parrafos:
                contenido_corto = parrafo.contenido[:50] + "..." if len(parrafo.contenido) > 50 else parrafo.contenido
                self.tree_parrafos.insert("", "end", values=(
                    parrafo.id, parrafo.orden, contenido_corto, parrafo.leccion_id
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar párrafos: {str(e)}")
    
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
    
    def limpiar_formulario_parrafo(self):
        self.par_leccion_id.delete(0, tk.END)
        self.par_orden.delete(0, tk.END)
        self.par_contenido.delete("1.0", tk.END)

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