import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import ttk
from PIL import ImageTk, Image
import serial.tools.list_ports
import serial

def open_file():
    """Open a file for editing."""
    filepath = askopenfilename(
        filetypes=[("gcode Files", "*.gcode"),("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not filepath:
        return
    txt_edit.delete("1.0", tk.END)
    with open(filepath, mode="r", encoding="utf-8") as input_file:
        text = input_file.read()
        txt_edit.insert(tk.END, text)
    window.title(f"Simple Text Editor - {filepath}")

def save_file():
    """Save the current file as a new file."""
    filepath = asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("gcode Files", "*.gcode"),("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    if not filepath:
        return
    with open(filepath, mode="w", encoding="utf-8") as output_file:
        text = txt_edit.get("1.0", tk.END)
        output_file.write(text)
    window.title(f"Simple Text Editor - {filepath}")

def connectArm():
    pass

def connectBase():
    pass

def conectionConfig():
    secondWindow = tk.Toplevel(window)
    secondWindow.title("Conection configuration")
    secondWindow.resizable(False, False)
    
    label = tk.Label(secondWindow,text="Robotic Arm port: ",font=("Bahnschrift Light", 12))
    label.pack()
    
    puertos_disponibles = [puerto.device for puerto in serial.tools.list_ports.comports()]
    
    seleccion = tk.StringVar(secondWindow)
    puertos_disponibles.append(" ")
    seleccion.set(" ")
    lista_desplegable = tk.OptionMenu(secondWindow, seleccion, *puertos_disponibles)
    lista_desplegable.pack(padx=20, pady=20)

    label2 = tk.Label(secondWindow,text="Base port: ",font=("Bahnschrift Light", 12))
    label2.pack()
    
    puertos_disponibles2 = [puerto.device for puerto in serial.tools.list_ports.comports()]
    
    seleccion2 = tk.StringVar(secondWindow)
    puertos_disponibles2.append(" ")
    seleccion2.set(" ")
    lista_desplegable2 = tk.OptionMenu(secondWindow, seleccion2, *puertos_disponibles2)
    lista_desplegable2.pack(padx=20, pady=20)
    

def up():
    pass

def down():

    pass
def left():

    pass
def right():
    pass

def up3z():
    pass

def up2z():
    pass

def upz():
    pass

def downz():
    pass

def down2z():
    pass

def down3z():
    pass

def up3e():
    pass

def up2e():
    pass

def upe():
    pass

def downe():
    pass

def down2e():
    pass

def down3e():
    pass

def sendgcodebtn():
    pass

def targetTemp(value):
    value=value
    pass

def starthotend():
    if btn_hotend["relief"] == tk.FLAT:
        btn_hotend.config(relief="sunken")
    else:
        btn_hotend.config(relief=tk.FLAT)


def startfan():
    if btn_fan["relief"] == tk.FLAT:
        btn_fan.config(relief="sunken")
    else:
        btn_fan.config(relief=tk.FLAT)

def home():
    pass

def emergencyStop():
    pass
window = tk.Tk()
window.title("3Dbot")


window.rowconfigure(1, minsize=450, weight=1)
window.rowconfigure(2, minsize=100, weight=1)

window.columnconfigure(0, minsize=800, weight=1)

# First Row ----------------------------------------------------------------------------------------------------------------- 
frm_firstrow = tk.Frame(window, relief=tk.RAISED, bd=2, bg="white")
frm_firstrow.grid(row=0, column=0, sticky="nsew")
frm_firstrow.columnconfigure(4, minsize=1, weight=1)


imagen = Image.open("Imagenes_3Dbot_software/open.png")
imagen = imagen.resize((30, 30), Image.ANTIALIAS)
img_boton_open = ImageTk.PhotoImage(imagen)
btn_open = tk.Button(frm_firstrow,text="Open", image=img_boton_open, compound=tk.TOP, command=open_file, border=0, bg="white",
                     font=('Calibri Light', 10, 'normal'))

imagen = Image.open("Imagenes_3Dbot_software/salvar.png")
imagen = imagen.resize((30, 30), Image.ANTIALIAS)
img_boton_open2 = ImageTk.PhotoImage(imagen)
btn_save = tk.Button(frm_firstrow,text="Save As", image=img_boton_open2, compound=tk.TOP, command=save_file, border=0, bg="white",
                     font=('Calibri Light', 10, 'normal'))

imagen = Image.open("Imagenes_3Dbot_software/arm.png")
imagen = imagen.resize((30, 30), Image.ANTIALIAS)
img_boton_open3 = ImageTk.PhotoImage(imagen)
btn_conect_arm = tk.Button(frm_firstrow,text="Conect Arm", image=img_boton_open3, compound=tk.TOP, command=connectArm, border=0, bg="white",
                     font=('Calibri Light', 10, 'normal'))

imagen = Image.open("Imagenes_3Dbot_software/base.png")
imagen = imagen.resize((30, 30), Image.ANTIALIAS)
img_boton_open4 = ImageTk.PhotoImage(imagen)
btn_conect_base = tk.Button(frm_firstrow,text="Conect Base", image=img_boton_open4, compound=tk.TOP, command=connectBase, border=0, bg="white",
                     font=('Calibri Light', 10, 'normal'))

imagen = Image.open("Imagenes_3Dbot_software/config.png")
imagen = imagen.resize((30, 30), Image.ANTIALIAS)
img_boton_open5 = ImageTk.PhotoImage(imagen)
btn_conection_config = tk.Button(frm_firstrow,text="Conection Config", image=img_boton_open5, compound=tk.TOP, command=conectionConfig, border=0, bg="white",
                     font=('Calibri Light', 10, 'normal'))

imagen = Image.open("Imagenes_3Dbot_software/stop.png")
imagen = imagen.resize((30, 30), Image.ANTIALIAS)
img_boton_open25 = ImageTk.PhotoImage(imagen)
btn_emergency_stop = tk.Button(frm_firstrow,text="Emergency Stop", image=img_boton_open25, compound=tk.TOP, command=emergencyStop, border=0, bg="white",
                     font=('Calibri Light', 10, 'normal'))

btn_open.grid(row=0, column=0, sticky="w", padx=8, pady=5)
btn_save.grid(row=0, column=1, sticky="e", padx=15)
btn_conect_arm.grid(row=0, column=2, sticky="w", padx=0)
btn_conect_base.grid(row=0, column=3, sticky="w", padx=5)
btn_conection_config.grid(row=0, column=4, sticky="e", padx=100)
btn_emergency_stop.grid(row=0, column=4, sticky="e", padx=5)

# Second Row ----------------------------------------------------------------------------------------------------------------- 

frm_secondrow = tk.Frame(window, relief=tk.RAISED, bd=2, bg="white")
frm_secondrow.grid(row=1, column=0, sticky="nsew")
frm_secondrow.rowconfigure(0,minsize=150,weight=1)
frm_secondrow.columnconfigure(0,minsize=800,weight=1)
frm_secondrow.columnconfigure(1,minsize=120,weight=1)

frm_txt_edit = tk.Frame(frm_secondrow, relief=tk.RAISED, bd=2, bg="white")
frm_txt_edit.grid(row=0, column=0, sticky="nsew", padx=5, pady=0)
frm_txt_edit.rowconfigure(0,weight=1)
frm_txt_edit.columnconfigure(0,weight=1)

txt_edit = tk.Text(frm_txt_edit,bg="#E0E0E0")
deslizador1 = tk.Scrollbar(frm_txt_edit, command=txt_edit.yview)
txt_edit.config(yscrollcommand=deslizador1.set)
txt_edit.grid(row=0,column=0,sticky="nsew")
deslizador1.grid(row=0,column=0,sticky="nse")


frm_manual_use = tk.Frame(frm_secondrow, relief=tk.GROOVE, bd=2, bg="white")
frm_manual_use.grid(row=0, column=1, sticky="nsew")
frm_manual_use.columnconfigure([0,1,2],minsize=100,weight=1)


label = tk.Label(frm_manual_use,text="Gcode: ",bg="white",font=("Arial", 12, "italic"))
entry = tk.Entry(frm_manual_use, border=4)
label.grid(row=0,column=0,sticky="e",pady=10)
entry.grid(row=0,column=1,sticky="we",pady=10)
btn_send = ttk.Button(frm_manual_use, text="Enviar" ,command=sendgcodebtn)
btn_send.grid(row=0, column=2, sticky="w")

labelpos = tk.Label(frm_manual_use,text="X0 Y86 Z0 E0",bg="white",font=("Bahnschrift Light", 15))
labelpos.grid(row=1,column=0,sticky="w",padx=10 ,pady=5)


frm_manual_usexy = tk.Frame(frm_manual_use, relief=tk.FLAT, bd=2, bg="white")
frm_manual_usexy.grid(row=2, column=0, sticky="we", padx=5, pady=10)
frm_manual_usexy.rowconfigure([0,1,2],minsize=50,weight=1)
frm_manual_usexy.columnconfigure([0,1,2],minsize=50,weight=1)

imagen = Image.open("Imagenes_3Dbot_software/up.png")
imagen = imagen.resize((20, 20), Image.ANTIALIAS)
img_boton_open6 = ImageTk.PhotoImage(imagen)
btn_up = ttk.Button(frm_manual_usexy, image=img_boton_open6, command=up)

imagen = Image.open("Imagenes_3Dbot_software/left.png")
imagen = imagen.resize((20, 20), Image.ANTIALIAS)
img_boton_open7 = ImageTk.PhotoImage(imagen)
btn_left = ttk.Button(frm_manual_usexy, image=img_boton_open7, command=left)

imagen = Image.open("Imagenes_3Dbot_software/right.png")
imagen = imagen.resize((20, 20), Image.ANTIALIAS)
img_boton_open8 = ImageTk.PhotoImage(imagen)
btn_right = ttk.Button(frm_manual_usexy, image=img_boton_open8, command=right)

imagen = Image.open("Imagenes_3Dbot_software/down.png")
imagen = imagen.resize((20, 20), Image.ANTIALIAS)
img_boton_open9 = ImageTk.PhotoImage(imagen)
btn_down = ttk.Button(frm_manual_usexy, image=img_boton_open9, command=down)

btn_up.grid(row=0, column=1, sticky="nsew")
btn_left.grid(row=1, column=0, sticky="nsew")
btn_right.grid(row=1, column=2, sticky="nsew")
btn_down.grid(row=2, column=1, sticky="nsew")


frm_manual_usez = tk.Frame(frm_manual_use, relief=tk.FLAT, bd=2, bg="white")
frm_manual_usez.grid(row=2, column=1, padx=0, pady=10)
frm_manual_usez.rowconfigure([0,1,2,3,4,5],minsize=40,weight=1)
frm_manual_usez.columnconfigure(0,minsize=70,weight=1)

imagen = Image.open("Imagenes_3Dbot_software/up3.png")
imagen = imagen.resize((20, 20), Image.ANTIALIAS)
img_boton_open10 = ImageTk.PhotoImage(imagen)
btn_up3z = ttk.Button(frm_manual_usez, text="    10 mm", compound=tk.LEFT, image=img_boton_open10, command=up3z)

imagen = Image.open("Imagenes_3Dbot_software/up2.png")
imagen = imagen.resize((20, 20), Image.ANTIALIAS)
img_boton_open11 = ImageTk.PhotoImage(imagen)
btn_up2z = ttk.Button(frm_manual_usez, text="     1 mm", compound=tk.LEFT, image=img_boton_open11, command=up2z)

imagen = Image.open("Imagenes_3Dbot_software/up.png")
imagen = imagen.resize((20, 20), Image.ANTIALIAS)
img_boton_open12 = ImageTk.PhotoImage(imagen)
btn_upz = ttk.Button(frm_manual_usez, text="  0.1 mm", compound=tk.LEFT, image=img_boton_open12, command=upz)

imagen = Image.open("Imagenes_3Dbot_software/down.png")
imagen = imagen.resize((20, 20), Image.ANTIALIAS)
img_boton_open13 = ImageTk.PhotoImage(imagen)
btn_downz = ttk.Button(frm_manual_usez, text=" -0.1 mm", compound=tk.LEFT, image=img_boton_open13, command=downz)

imagen = Image.open("Imagenes_3Dbot_software/down2.png")
imagen = imagen.resize((20, 20), Image.ANTIALIAS)
img_boton_open14 = ImageTk.PhotoImage(imagen)
btn_down2z = ttk.Button(frm_manual_usez, text="    -1 mm", compound=tk.LEFT, image=img_boton_open14, command=down2z)

imagen = Image.open("Imagenes_3Dbot_software/down3.png")
imagen = imagen.resize((20, 20), Image.ANTIALIAS)
img_boton_open15 = ImageTk.PhotoImage(imagen)
btn_down3z = ttk.Button(frm_manual_usez, text="  -10 mm", compound=tk.LEFT, image=img_boton_open15, command=down3z)

btn_up3z.grid(row=0, column=0, sticky="nsew")
btn_up2z.grid(row=1, column=0, sticky="nsew")
btn_upz.grid(row=2, column=0, sticky="nsew")
btn_downz.grid(row=3, column=0, sticky="nsew")
btn_down2z.grid(row=4, column=0, sticky="nsew")
btn_down3z.grid(row=5, column=0, sticky="nsew")


frm_manual_useE = tk.Frame(frm_manual_use, relief=tk.FLAT, bd=2, bg="white")
frm_manual_useE.grid(row=2, column=2, sticky="we", padx=0, pady=10)
frm_manual_useE.rowconfigure([0,1,2,3],minsize=40,weight=1)
frm_manual_useE.columnconfigure([0,1],minsize=35,weight=1)

imagen = Image.open("Imagenes_3Dbot_software/up3.png")
imagen = imagen.resize((20, 20), Image.ANTIALIAS)
img_boton_open16 = ImageTk.PhotoImage(imagen)
btn_up3e = ttk.Button(frm_manual_useE, text="    50 mm", compound=tk.BOTTOM, image=img_boton_open16, command=up3e)

imagen = Image.open("Imagenes_3Dbot_software/up2.png")
imagen = imagen.resize((20, 20), Image.ANTIALIAS)
img_boton_open17 = ImageTk.PhotoImage(imagen)
btn_up2e = ttk.Button(frm_manual_useE, text="    10 mm", compound=tk.BOTTOM, image=img_boton_open17, command=up2e)

imagen = Image.open("Imagenes_3Dbot_software/up.png")
imagen = imagen.resize((20, 20), Image.ANTIALIAS)
img_boton_open18 = ImageTk.PhotoImage(imagen)
btn_upe = ttk.Button(frm_manual_useE, text="    1 mm", compound=tk.BOTTOM, image=img_boton_open18, command=upe)

imagen = Image.open("Imagenes_3Dbot_software/down.png")
imagen = imagen.resize((20, 20), Image.ANTIALIAS)
img_boton_open19 = ImageTk.PhotoImage(imagen)
btn_downe = ttk.Button(frm_manual_useE, text="   -1 mm", compound=tk.TOP, image=img_boton_open19, command=downe)

imagen = Image.open("Imagenes_3Dbot_software/down2.png")
imagen = imagen.resize((20, 20), Image.ANTIALIAS)
img_boton_open20 = ImageTk.PhotoImage(imagen)
btn_down2e = ttk.Button(frm_manual_useE, text="   -10 mm", compound=tk.TOP, image=img_boton_open20, command=down2e)

imagen = Image.open("Imagenes_3Dbot_software/down3.png")
imagen = imagen.resize((20, 20), Image.ANTIALIAS)
img_boton_open21 = ImageTk.PhotoImage(imagen)
btn_down3e = ttk.Button(frm_manual_useE, text="  -50 mm", compound=tk.TOP, image=img_boton_open21, command=down3e)

btn_up3e.grid(row=1, column=1, sticky="nsew")
btn_up2e.grid(row=0, column=0, sticky="nsew")
btn_upe.grid(row=1, column=0, sticky="nsew")
btn_downe.grid(row=2, column=0, sticky="nsew")
btn_down2e.grid(row=3, column=0, sticky="nsew")
btn_down3e.grid(row=2, column=1, sticky="nsew")



frm_manual_temp = tk.Frame(frm_manual_use, relief=tk.FLAT, bd=2, bg="white")
frm_manual_temp.grid(row=3, column=0, sticky="we", padx=0, pady=10)
frm_manual_temp.rowconfigure(0,minsize=40,weight=1)
frm_manual_temp.columnconfigure([0,1],minsize=35,weight=1)

imagen = Image.open("Imagenes_3Dbot_software/hotend.png")
imagen = imagen.resize((40, 40), Image.ANTIALIAS)
img_boton_open22 = ImageTk.PhotoImage(imagen)
btn_hotend = tk.Button(frm_manual_temp, image=img_boton_open22, command=starthotend, relief=tk.FLAT, background="white")
btn_hotend.grid(row=0, column=0)


barra = tk.Scale(frm_manual_temp,from_=0, to=240, orient='horizontal',background="white", command=targetTemp )
barra.grid(row=0, column=1,sticky="we")


labeltemp = tk.Label(frm_manual_use,text="T: 60°C",bg="white",font=("Bahnschrift Light", 15))
labeltemp.grid(row=3,column=1,sticky="w",padx=10 ,pady=5)


frm_manual_fan_home = tk.Frame(frm_manual_use, relief=tk.FLAT, bd=2, bg="white")
frm_manual_fan_home.grid(row=3, column=2, sticky="we", padx=0, pady=10)
frm_manual_fan_home.rowconfigure(0,minsize=40,weight=1)
frm_manual_fan_home.columnconfigure([0,1],minsize=35,weight=1)


imagen = Image.open("Imagenes_3Dbot_software/fan.png")
imagen = imagen.resize((40, 40), Image.ANTIALIAS)
img_boton_open23 = ImageTk.PhotoImage(imagen)
btn_fan = tk.Button(frm_manual_fan_home, image=img_boton_open23, command=startfan, relief=tk.FLAT, background="white")


imagen = Image.open("Imagenes_3Dbot_software/home.png")
imagen = imagen.resize((40, 40), Image.ANTIALIAS)
img_boton_open24 = ImageTk.PhotoImage(imagen)
btn_home = tk.Button(frm_manual_fan_home, image=img_boton_open24, command=home, relief=tk.FLAT, background="white")


btn_fan.grid(row=0, column=0)
btn_home.grid(row=0, column=1)


# Third Row ----------------------------------------------------------------------------------------------------------------- 

frm_thirdrow = tk.Frame(window, relief=tk.RAISED, bd=2, bg="white")
frm_thirdrow.grid(row=2, column=0, sticky="nsew")
frm_thirdrow.rowconfigure(0,minsize=40,weight=1)
frm_thirdrow.rowconfigure(1,minsize=100,weight=1)
frm_thirdrow.columnconfigure(0,minsize=400,weight=1)
frm_thirdrow.columnconfigure(1,minsize=400,weight=1)


label_arm_terminal = tk.Label(frm_thirdrow,text="Arm Terminal",bg="white",font=("Bahnschrift Light", 12))
label_arm_terminal.grid(row=0,column=0,sticky="w",padx=5 ,pady=0)

label_base_terminal = tk.Label(frm_thirdrow,text="Base Terminal",bg="white",font=("Bahnschrift Light", 12))
label_base_terminal.grid(row=0,column=1,sticky="w",padx=5 ,pady=0)

frm_arm_terminal = tk.Frame(frm_thirdrow, relief=tk.RAISED, bd=2, bg="white")
frm_arm_terminal.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
frm_arm_terminal.rowconfigure(0,weight=1)
frm_arm_terminal.columnconfigure(0,weight=1)
txt_arm_terminal = tk.Text(frm_arm_terminal,bg="#E0E0E0")
deslizador2 = tk.Scrollbar(frm_arm_terminal, command=txt_edit.yview)
txt_arm_terminal.config(yscrollcommand=deslizador2.set)
txt_arm_terminal.grid(row=0,column=0,sticky="nsew")
deslizador2.grid(row=0,column=0,sticky="nse")

frm_base_terminal = tk.Frame(frm_thirdrow, relief=tk.RAISED, bd=2, bg="white")
frm_base_terminal.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
frm_base_terminal.rowconfigure(0,weight=1)
frm_base_terminal.columnconfigure(0,weight=1)
txt_base_terminal = tk.Text(frm_base_terminal,bg="#E0E0E0")
deslizador3 = tk.Scrollbar(frm_base_terminal, command=txt_edit.yview)
txt_base_terminal.config(yscrollcommand=deslizador3.set)
txt_base_terminal.grid(row=0,column=0,sticky="nsew")
deslizador3.grid(row=0,column=0,sticky="nse")


window.mainloop()