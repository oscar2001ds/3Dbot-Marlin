import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import ttk
from PIL import ImageTk, Image
import serial.tools.list_ports
import serial

import threading
import time
from cnc.gcode import GCode, GCodeException
from cnc.coordinates import *
import sys
from math import sin, cos, pi, atan
import cmath


class GUI3Dbot:
    def serialWrite(self, msg):
        try:
            self.serial_port.write(msg)
        except:
            pass

    def Serial1Reader(self):
        while self.stop_threads == False:
            try:
                response = self.serial_port.readline()
            except:
                self.serial_port.flush()

            if response:
                self.msgFromMarlin = response.decode('UTF-8')
                if response == b'echo:busy: processing\n':
                    self.fullBufferAlert = True
                    self.emptyBufferAlert = False
                    self.okAlert = False
                    self.otherAlert = False
                    self.txt_arm_terminal.insert(tk.END, self.msgFromMarlin)
                    self.txt_arm_terminal.see(tk.END)

                elif response == b'wait\n':
                    self.fullBufferAlert = False
                    self.emptyBufferAlert = True
                    self.okAlert = False
                    self.otherAlert = False

                    if self.msgFromMarlin != self.lastMsg:
                        self.txt_arm_terminal.insert(
                            tk.END, self.msgFromMarlin)
                        self.txt_arm_terminal.see(tk.END)

                elif response == b'ok\n':
                    self.contOk += 1
                    self.fullBufferAlert = False
                    self.emptyBufferAlert = False
                    self.okAlert = True
                    self.otherAlert = False
                    self.txt_arm_terminal.insert(tk.END, self.msgFromMarlin)
                    self.txt_arm_terminal.see(tk.END)

                elif b'T:' in response:
                    indice = self.msgFromMarlin.find("T:")+2
                    indice2 = self.msgFromMarlin.find("/")
                    self.current_temp = self.msgFromMarlin[indice:indice2]
                    self.fullBufferAlert = False
                    self.emptyBufferAlert = False
                    self.okAlert = False
                    self.otherAlert = True

                    self.txt_arm_terminal.insert(tk.END, self.msgFromMarlin)
                    self.txt_arm_terminal.see(tk.END)
                    self.labeltemp.config(text=self.current_temp)

                else:
                    if "Error:" in self.msgFromMarlin:
                        break
                    self.fullBufferAlert = False
                    self.emptyBufferAlert = False
                    self.okAlert = False
                    self.otherAlert = True

                    self.txt_arm_terminal.insert(tk.END, self.msgFromMarlin)
                    self.txt_arm_terminal.see(tk.END)

                self.lastMsg = self.msgFromMarlin

        self.serial_port.flush()
        self.serial_port.close()

    def Serial2Reader(self):
        while self.stop_threads == False:
            try:
                response2 = self.serial_port2.readline()
            except:
                pass

            if response2:
                self.msgFromBase = response2.decode('UTF-8')
                if response2 == b'ok\n':
                    self.okAlertBase = True
                self.txt_base_terminal.insert(tk.END, self.msgFromBase)
                self.txt_base_terminal.see(tk.END)

        self.serial_port2.flush()
        self.serial_port2.close()

    def open_file(self):
        """Open a file for editing."""
        self.filepath = askopenfilename(
            filetypes=[("gcode Files", "*.gcode"),
                       ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not self.filepath:
            return
        self.txt_edit.delete("1.0", tk.END)
        with open(self.filepath, mode="r", encoding="utf-8") as input_file:
            text = input_file.read()
            self.txt_edit.insert(tk.END, text)
        self.window.title(f"Simple Text Editor - {self.filepath}")

    def save_file(self):
        """Save the current file as a new file."""
        filepath = asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("gcode Files", "*.gcode"),
                       ("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not filepath:
            return
        with open(filepath, mode="w", encoding="utf-8") as output_file:
            text = self.txt_edit.get("1.0", tk.END)
            output_file.write(text)
        self.window.title(f"Simple Text Editor - {filepath}")

    def connectArm(self):
                   
        if self.seleccion.get() != " ":
            self.comArm = self.seleccion.get()
            self.serial_port = serial.Serial(
                self.comArm, baudrate=250000, timeout=1)
            time.sleep(1)
            self.btn_conect_arm.config(state="disable")
            # secondWindow = tk.Toplevel(self.window)
            # secondWindow.title("Succes Conect")
            # secondWindow.resizable(False, False)
            # label = tk.Label(secondWindow,text="Successful Connection",font=("Bahnschrift Light", 12))
            # label.pack()
            self.arm_conected = True
            self.SR1 = threading.Thread(
                target=self.Serial1Reader, name="Reader")
            self.SR1.start()

            self.txt_arm_terminal.delete("1.0", tk.END)
            self.txt_arm_terminal.insert(
                tk.END, "Successful Conection to Arm\n")
        else:
            secondWindow = tk.Toplevel(self.window)
            secondWindow.title("ALERT")
            secondWindow.resizable(False, False)
            label = tk.Label(secondWindow, text="Select Port",
                             font=("Bahnschrift Light", 12))
            label.pack()

    def connectBase(self):
        if self.seleccion2.get() != " ":
            self.comBase = self.seleccion2.get()
            self.serial_port2 = serial.Serial(
                self.comBase, baudrate=250000, timeout=1)
            time.sleep(1)
            self.btn_conect_base.config(state="disable")
            # secondWindow = tk.Toplevel(self.window)
            # secondWindow.title("Succes Conect")
            # secondWindow.resizable(False, False)
            # label = tk.Label(secondWindow,text="Successful Connection",font=("Bahnschrift Light", 12))
            # label.pack()
            self.base_conected = True
            self.SR2 = threading.Thread(
                target=self.Serial2Reader, name="Reader2")
            self.SR2.start()

            self.txt_base_terminal.delete("1.0", tk.END)
            self.txt_base_terminal.insert(
                tk.END, "Successful Conection to Base\n")
        else:
            secondWindow = tk.Toplevel(self.window)
            secondWindow.title("ALERT")
            secondWindow.resizable(False, False)
            label = tk.Label(secondWindow, text="Select Port",
                             font=("Bahnschrift Light", 12))
            label.pack()

    def postProcessing(self):

        def postProcessingOnePiece(filepath,offset):
            def postProcessingOnePieceP():
                ofl = float(entry_offsetFirstLayer.get())
                secondWindow.destroy()

                postProcessingPerParts(filepath,offset,0)
                quad = 0
                
                x1_min = 999
                x1_max = -999
                y1_max = -999
                y1_min = 999

                x2_min = 999
                x2_max = -999
                y2_max = -999
                y2_min = 999

                x3_min = 999
                x3_max = -999
                y3_max = -999
                y3_min = 999

                x4_min = 999
                x4_max = -999
                y4_max = -999
                y4_min = 999

                x5_min = 999
                x5_max = -999
                y5_max = -999
                y5_min = 999

                with open("Gcodes/postProcessing.gcode", "r") as file:
                    for line in file:
                        if line.startswith(";quadrant"):
                            tokens = line.strip().split()
                            for i in range(len(tokens)):
                                if tokens[i].startswith('P'):
                                    quad = int(tokens[i][1:])

                        elif line.startswith('G0') or line.startswith('G1'):
                            tokens = line.strip().split()  # Dividir la línea en tokens
                            for i in range(len(tokens)):
                                    if tokens[i].startswith('X'):
                                        x = float(tokens[i][1:])  

                                    if tokens[i].startswith('Y'):
                                        y = float(tokens[i][1:])

                                    if tokens[i].startswith('Z'):
                                        z = float(tokens[i][1:])

                            if quad == 1:
                                if z == ofl:
                                    if x < x1_min:
                                        x1_min = x
                                    if x > x1_max:
                                        x1_max = x
                                    if y < y1_min:
                                        y1_min = y
                                    if y > y1_max:
                                        y1_max = y

                            elif quad == 2:
                                if z == ofl:
                                    if x < x2_min:
                                        x2_min = x
                                    if x > x2_max:
                                        x2_max = x
                                    if y < y2_min:
                                        y2_min = y
                                    if y > y2_max:
                                        y2_max = y

                            elif quad == 3:
                                if z == ofl:
                                    if x < x3_min:
                                        x3_min = x
                                    if x > x3_max:
                                        x3_max = x
                                    if y < y3_min:
                                        y3_min = y
                                    if y > y3_max:
                                        y3_max = y

                            elif quad == 4:
                                if z == ofl:
                                    if x < x4_min:
                                        x4_min = x
                                    if x > x4_max:
                                        x4_max = x
                                    if y < y4_min:
                                        y4_min = y
                                    if y > y4_max:
                                        y4_max = y

                            elif quad == 5:
                                if z == ofl:
                                    if x < x5_min:
                                        x5_min = x
                                    if x > x5_max:
                                        x5_max = x
                                    if y < y5_min:
                                        y5_min = y
                                    if y > y5_max:
                                        y5_max = y
                                        
                print(f"x1max: {x1_max}  x2min: {x2_min}")
                print(f"x2max: {x2_max}  x3min: {x3_min}")
                print(f"x3max: {x3_max}  x4min: {x4_min}")
                print(f"x4max: {x4_max}  x5min: {x5_min}")

                postProcessingPerParts(filepath,offset,1)

                dif1 = 0
                dif2 = 0
                dif3 = 0
                dif4 = 0

                with open("Gcodes/postProcessing.gcode", "r+") as file:
                    lines = file.readlines()
                    file.seek(0)
                    for line in lines:
                        if line.startswith(";quadrant"):
                            tokens = line.strip().split()
                            for i in range(len(tokens)):
                                if tokens[i].startswith('P'):
                                    quad = int(tokens[i][1:])
                            file.write(line)

                        elif line.startswith("G7"):
                            if quad == 2:
                                dif1 = x2_min-x1_max
                                y_movement = 90 - dif1
                                line_update = line.replace("G7",f"G7 X0 Y{y_movement} F800\n;x1max: {x1_max}  x2min: {x2_min} //")
                                file.write(line_update)

                            elif quad == 3:
                                dif2 = x3_min-x2_max
                                y_movement = 180 - dif2
                                line_update = line.replace("G7",f"G7 X0 Y{y_movement} F800\n;x2max: {x2_max}  x3min: {x3_min} //")
                                file.write(line_update)

                            elif quad == 4:
                                dif3 = x4_min-x3_max
                                y_movement = 270 - dif3
                                line_update = line.replace("G7",f"G7 X0 Y{y_movement} F800\n;x3max: {x3_max}  x4min: {x4_min} //")
                                file.write(line_update)

                            elif quad == 5:
                                dif4 = x5_min-x4_max
                                y_movement = 360 - dif4
                                line_update = line.replace("G7",f"G7 X0 Y{y_movement} F800\n;x4max: {x4_min}  x5min: {x5_min} //")
                                file.write(line_update)

                            else:
                                file.write(line)  
                        else:
                          file.write(line)  

                thirdWindow.destroy()
                quarterWindow = tk.Toplevel(self.window)
                quarterWindow.title("Post processing state")
                quarterWindow.resizable(False, False)

                label = tk.Label(quarterWindow, text="Successful post processing", font=("Bahnschrift Light", 12))
                label.pack()
                label2 = tk.Label(quarterWindow, text="stored in 'Gcodes/postProcessing.gcode'", font=("Bahnschrift Light", 12))
                label2.pack()


            offset = float(entry_offset.get())

            thirdWindow = tk.Toplevel(self.window)
            thirdWindow.title("Post Processing One Piece")
            thirdWindow.resizable(False, False)

            frm_onePiece = tk.Frame(thirdWindow, relief=tk.RAISED, bd=2, bg="white")

            frm_onePiece.rowconfigure([0, 1], minsize=50, weight=1)
            frm_onePiece.columnconfigure([0, 1], minsize=50, weight=1)
            
            tk.Label(thirdWindow, text="Altura de la primera capa (mm):",
                    font=("Bahnschrift Light", 12)).grid(row=0, column=0, sticky="nsew",padx=5,pady=2)
            v1=tk.StringVar(value="0.8")
            entry_offsetFirstLayer = tk.Entry(thirdWindow, border=4, textvariable=v1, width=5)
            entry_offsetFirstLayer.grid(row=0, column=1, sticky="nsew",padx=5,pady=2)

            button_okOnePiece = tk.Button(thirdWindow, text="OK", command=postProcessingOnePieceP, height=1, width=4)
            button_okOnePiece.grid(row=1, column=0, columnspan=2,pady=5)

        def postProcessingPerParts(filepath,offset,change):
            with open(filepath, 'r') as f_in:
                xoffset_pass = 1
                velBase = 800
                with open('Gcodes/postProcessing.gcode', 'w') as f_out:
                    for line in f_in:
                        # Buscar comandos G0 o G1 (movimiento)
                        if line.startswith('G0') or line.startswith('G1'):
                            tokens = line.strip().split()  # Dividir la línea en tokens
                            for i in range(len(tokens)):
                                # Buscar la coordenada X
                                if tokens[i].startswith('X'):
                                    # Obtener el valor numérico de la coordenada X
                                    x_coord = float(tokens[i][1:])
                                    x_coord_r = x_coord
                                    if x_coord >= 0-offset and x_coord < 90-offset:
                                        rest = 0
                                        x_coord -= rest
                                        if xoffset_pass != rest:
                                            line = ';quadrant P1\n'+f'G7 X0 Y{rest} F{velBase}\n'
                                            f_out.write(line)
                                            xoffset_pass = rest

                                    elif x_coord >= 90-offset and x_coord < 180-offset:
                                        rest = 90
                                        x_coord -= rest  # Restar 90 mm a cada linea
                                        if xoffset_pass != rest:
                                            line = ';quadrant P2\n'+f'G7 X0 Y{rest} F{velBase}\n'
                                            f_out.write(line)
                                            xoffset_pass = rest

                                    elif x_coord >= 180-offset and x_coord < 270-offset:
                                        rest = 180
                                        x_coord -= rest
                                        if xoffset_pass != rest:
                                            line = ';quadrant P3\n'+f'G7 X0 Y{rest} F{velBase}\n'
                                            f_out.write(line)
                                            xoffset_pass = rest

                                    elif x_coord >= 270-offset and x_coord < 360-offset:
                                        rest = 270
                                        x_coord -= rest
                                        if xoffset_pass != rest:
                                            line = ';quadrant P4\n'+f'G7 X0 Y{rest} F{velBase}\n'
                                            f_out.write(line)
                                            xoffset_pass = rest

                                    elif x_coord >= 360-offset and x_coord < 450-offset:
                                        rest = 360
                                        x_coord -= rest
                                        if xoffset_pass != rest:
                                            line = ';quadrant P5\n'+f'G7 X0 Y{rest} F{velBase}\n'
                                            f_out.write(line)
                                            xoffset_pass = rest

                                    if change == 0:
                                        x_coord = x_coord_r
                                    
                                    # Actualizar el token de la coordenada X
                                    tokens[i] = f'X{x_coord:.3f}'

                                elif tokens[i].startswith('Y'):
                                    y_coord = float(tokens[i][1:])
                                    y_coord -= 0
                                    tokens[i] = f'Y{y_coord:.3f}'

                            # Unir los tokens actualizados en una línea de texto
                            line = ' '.join(tokens) + '\n'

                        # Escribir la línea en el archivo de salida
                        f_out.write(line)

        def printMode():
            filepath = askopenfilename(
                filetypes=[("gcode Files", "*.gcode"),
                           ("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            if not filepath:
                return
            
            offset = float(entry_offset.get())
            mode = int(entry_mode.get())
            if mode == 0:
                postProcessingPerParts(filepath,offset,1)
                secondWindow.destroy()
                quarterWindow = tk.Toplevel(self.window)
                quarterWindow.title("Post processing state")
                quarterWindow.resizable(False, False)

                label = tk.Label(quarterWindow, text="Successful post processing", font=(
                    "Bahnschrift Light", 12))
                label.pack()
                label2 = tk.Label(
                    quarterWindow, text="stored in 'Gcodes/postProcessing.gcode'", font=("Bahnschrift Light", 12))
                label2.pack()

            elif mode == 1:
                postProcessingOnePiece(filepath,offset)

                

        secondWindow = tk.Toplevel(self.window)
        secondWindow.title("Post Processing Config")
        secondWindow.resizable(False, False)

        frm_printconfig = tk.Frame(secondWindow, relief=tk.RAISED, bd=2, bg="white")

        frm_printconfig.rowconfigure([0, 1, 2, 3], minsize=50, weight=1)
        frm_printconfig.columnconfigure([0, 1], minsize=50, weight=1)
        
        tk.Label(secondWindow, text="Offset en X del Marco de referencia:",
                 font=("Bahnschrift Light", 12)).grid(row=0, column=0, sticky="nsew",padx=5,pady=2)
        v1=tk.StringVar(value="45")
        entry_offset = tk.Entry(secondWindow, border=4, textvariable=v1, width=5)
        entry_offset.grid(row=0, column=1, sticky="nsew",padx=5,pady=2)

        tk.Label(secondWindow, text="Modo de impresion (0=por partes // 1=una pieza):",
                 font=("Bahnschrift Light", 12)).grid(row=1, column=0, sticky="nsew",padx=5,pady=2)
        v2=tk.StringVar(value="0")
        entry_mode = tk.Entry(secondWindow, border=4, textvariable=v2, width=5)
        entry_mode.grid(row=1, column=1, sticky="nsew",padx=5,pady=2)

        button_ok = tk.Button(secondWindow, text="OK", command=printMode, height=1, width=4)
        button_ok.grid(row=3, column=0, columnspan=2,pady=5)

    def conectionConfig(self):
        secondWindow = tk.Toplevel(self.window)
        secondWindow.title("Conection configuration")
        secondWindow.resizable(False, False)

        def on_Select1(port):
            self.i = 0
            for j in puertos_disponibles:
                if port == j:
                    break
                else:
                    self.i = self.i+1
            self.seleccion.set(puertos_disponibles[self.i])

        def on_Select2(port):
            self.i2 = 0
            for j in puertos_disponibles:
                if port == j:
                    break
                else:
                    self.i2 = self.i2+1
            self.seleccion2.set(puertos_disponibles[self.i2])

        puertos_disponibles = [
            puerto.device for puerto in serial.tools.list_ports.comports()]
        puertos_disponibles.append(" ")

        label = tk.Label(secondWindow, text="Robotic Arm port: ",
                         font=("Bahnschrift Light", 12))
        label.pack()
        self.seleccion = tk.StringVar(secondWindow)
        self.seleccion.set(puertos_disponibles[self.i])
        self.lista_desplegable = tk.OptionMenu(
            secondWindow, self.seleccion, *puertos_disponibles, command=on_Select1)
        self.lista_desplegable.pack(padx=20, pady=20)

        label2 = tk.Label(secondWindow, text="Base port: ",
                          font=("Bahnschrift Light", 12))
        label2.pack()
        self.seleccion2 = tk.StringVar(secondWindow)
        self.seleccion2.set(puertos_disponibles[self.i2])
        self.lista_desplegable2 = tk.OptionMenu(
            secondWindow, self.seleccion2, *puertos_disponibles, command=on_Select2)
        self.lista_desplegable2.pack(padx=20, pady=20)

    def getCurrentPositionArm(self, line):
        line = line.strip()
        gc = GCode.parse_line(line)
        if gc is None:
            return None

        if gc.has('X'):
            x = gc.get('X', 0)
            self.xpass = x
        else:
            x = self.xpass

        if gc.has('Y'):
            y = gc.get('Y', 0)
            self.ypass = y
        else:
            y = self.ypass

        if gc.has('Z'):
            z = gc.get('Z', 0)
            self.zpass = z
        else:
            z = self.zpass

        if gc.has('E'):
            e = gc.get('E', 0)
            self.epass = e
        else:
            e = self.epass

        if gc.has('F'):
            f = gc.get('F', 0)
            self.fpass = f
        else:
            f = self.fpass

        return [x, y, z, e, f]

    def currentPositionBase(self, line):
        line = line.strip()
        gc = GCode.parse_line(line)
        if gc is None:
            return None

        if gc.has('X'):
            x = gc.get('X', 0)
            self.xbpass = x
        else:
            x = self.xbpass

        if gc.has('Y'):
            y = gc.get('Y', 0)
            self.ybpass = y
        else:
            y = self.ybpass

        if gc.has('F'):
            f = gc.get('F', 0)
            self.fbpass = f
        else:
            f = self.fbpass

        return [x, y, f]

    def initThreadButtonBase(self, x, y, f):

        self.btbase = True

        def changeBaselabel():
            txt = f"X{x:.1f} Y{y:.1f} F{f:.1f}"
            txt = str(txt)
            self.labelposBase.config(text=txt)
            self.linearMovement(x, y, f)

        self.SBB = threading.Thread(target=changeBaselabel, name="ButtonBase")
        self.SBB.start()

    def up(self):
        if self.changeCenter == False:
            [x, y, z, e, f] = self.getCurrentPositionArm(
                self.labelpos.cget('text'))
            # print("x: ",x," y: ",y," z: ",z," e: ",e," f: ",f)
            y = y+1
            txt = f"X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{f:.1f}"
            txt = str(txt)
            self.labelpos.config(text=txt)
            txt = f"G1 X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{2000:.1f}"
            msg = (txt+"\n").encode()
            self.serialWrite(msg)

        elif self.changeCenter == True:
            [x, y, f] = self.currentPositionBase(
                self.labelposBase.cget('text'))
            x = x+20
            self.initThreadButtonBase(x, y, f)

    def down(self):
        if self.changeCenter == False:
            [x, y, z, e, f] = self.getCurrentPositionArm(
                self.labelpos.cget('text'))
            y = y-1
            txt = f"X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{f:.1f}"
            txt = str(txt)
            self.labelpos.config(text=txt)
            txt = f"G1 X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{2000:.1f}"
            msg = (txt+"\n").encode()
            self.serial_port.write(msg)

        elif self.changeCenter == True:
            [x, y, f] = self.currentPositionBase(
                self.labelposBase.cget('text'))
            x = x-20
            self.initThreadButtonBase(x, y, f)

    def left(self):
        if self.changeCenter == False:
            [x, y, z, e, f] = self.getCurrentPositionArm(
                self.labelpos.cget('text'))
            x = x+1
            txt = f"X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{f:.1f}"
            txt = str(txt)
            self.labelpos.config(text=txt)
            txt = f"G1 X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{2000:.1f}"
            msg = (txt+"\n").encode()
            self.serialWrite(msg)

        elif self.changeCenter == True:
            [x, y, f] = self.currentPositionBase(
                self.labelposBase.cget('text'))
            y = y-20
            self.initThreadButtonBase(x, y, f)

    def right(self):
        if self.changeCenter == False:
            [x, y, z, e, f] = self.getCurrentPositionArm(
                self.labelpos.cget('text'))
            x = x-1
            txt = f"X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{f:.1f}"
            txt = str(txt)
            self.labelpos.config(text=txt)
            txt = f"G1 X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{2000:.1f}"
            msg = (txt+"\n").encode()
            self.serialWrite(msg)

        elif self.changeCenter == True:
            [x, y, f] = self.currentPositionBase(
                self.labelposBase.cget('text'))
            y = y+20
            self.initThreadButtonBase(x, y, f)

    def center(self):
        if self.changeCenter == False:
            self.changeCenter = True
            imagen = Image.open("Imagenes_3Dbot_software/base.png")
            imagen = imagen.resize((20, 20), Image.ANTIALIAS)
            self.img_boton_open27 = ImageTk.PhotoImage(imagen)
            self.btn_center.config(image=self.img_boton_open27)

        elif self.changeCenter == True:
            self.changeCenter = False
            imagen = Image.open("Imagenes_3Dbot_software/arm.png")
            imagen = imagen.resize((20, 20), Image.ANTIALIAS)
            self.img_boton_open27 = ImageTk.PhotoImage(imagen)
            self.btn_center.config(image=self.img_boton_open27)

    def up3z(self):
        [x, y, z, e, f] = self.getCurrentPositionArm(
            self.labelpos.cget('text'))
        z = z+10
        txt = f"X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{f:.1f}"
        txt = str(txt)
        self.labelpos.config(text=txt)
        txt = f"G0 Z{z:.1f} F{2000:.1f}"
        msg = (txt+"\n").encode()
        self.serialWrite(msg)

    def up2z(self):
        [x, y, z, e, f] = self.getCurrentPositionArm(
            self.labelpos.cget('text'))
        z = z+1
        txt = f"X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{f:.1f}"
        txt = str(txt)
        self.labelpos.config(text=txt)
        txt = f"G0 Z{z:.1f} F{2000:.1f}"
        msg = (txt+"\n").encode()
        self.serialWrite(msg)

    def upz(self):
        [x, y, z, e, f] = self.getCurrentPositionArm(
            self.labelpos.cget('text'))
        z = z+0.1
        txt = f"X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{f:.1f}"
        txt = str(txt)
        self.labelpos.config(text=txt)
        txt = f"G0 Z{z:.1f} F{2000:.1f}"
        msg = (txt+"\n").encode()
        self.serialWrite(msg)

    def downz(self):
        [x, y, z, e, f] = self.getCurrentPositionArm(
            self.labelpos.cget('text'))
        z = z-0.1
        txt = f"X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{f:.1f}"
        txt = str(txt)
        self.labelpos.config(text=txt)
        txt = f"G0 Z{z:.1f} F{2000:.1f}"
        msg = (txt+"\n").encode()
        self.serialWrite(msg)

    def down2z(self):
        [x, y, z, e, f] = self.getCurrentPositionArm(
            self.labelpos.cget('text'))
        z = z-1
        txt = f"X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{f:.1f}"
        txt = str(txt)
        self.labelpos.config(text=txt)
        txt = f"G0 Z{z:.1f} F{2000:.1f}"
        msg = (txt+"\n").encode()
        self.serialWrite(msg)

    def down3z(self):
        [x, y, z, e, f] = self.getCurrentPositionArm(
            self.labelpos.cget('text'))
        z = z-10
        txt = f"X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{f:.1f}"
        txt = str(txt)
        self.labelpos.config(text=txt)
        txt = f"G0 Z{z:.1f} F{2000:.1f}"
        msg = (txt+"\n").encode()
        self.serialWrite(msg)

    def up3e(self):
        [x, y, z, e, f] = self.getCurrentPositionArm(
            self.labelpos.cget('text'))
        e = e+50
        txt = f"X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{f:.1f}"
        txt = str(txt)
        self.labelpos.config(text=txt)
        txt = f"G1 X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{100:.1f}"
        msg = (txt+"\n").encode()
        self.serialWrite(msg)

    def up2e(self):
        [x, y, z, e, f] = self.getCurrentPositionArm(
            self.labelpos.cget('text'))
        e = e+10
        txt = f"X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{f:.1f}"
        txt = str(txt)
        self.labelpos.config(text=txt)
        txt = f"G1 X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{100:.1f}"
        msg = (txt+"\n").encode()
        self.serialWrite(msg)

    def upe(self):
        [x, y, z, e, f] = self.getCurrentPositionArm(
            self.labelpos.cget('text'))
        e = e+1
        txt = f"X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{f:.1f}"
        txt = str(txt)
        self.labelpos.config(text=txt)
        txt = f"G1 X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{100:.1f}"
        msg = (txt+"\n").encode()
        self.serialWrite(msg)

    def downe(self):
        [x, y, z, e, f] = self.getCurrentPositionArm(
            self.labelpos.cget('text'))
        e = e-1
        txt = f"X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{f:.1f}"
        txt = str(txt)
        self.labelpos.config(text=txt)
        txt = f"G1 X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{500:.1f}"
        msg = (txt+"\n").encode()
        self.serialWrite(msg)

    def down2e(self):
        [x, y, z, e, f] = self.getCurrentPositionArm(
            self.labelpos.cget('text'))
        e = e-10
        txt = f"X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{f:.1f}"
        txt = str(txt)
        self.labelpos.config(text=txt)
        txt = f"G1 X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{500:.1f}"
        msg = (txt+"\n").encode()
        self.serialWrite(msg)

    def down3e(self):
        [x, y, z, e, f] = self.getCurrentPositionArm(
            self.labelpos.cget('text'))
        e = e-50
        txt = f"X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{f:.1f}"
        txt = str(txt)
        self.labelpos.config(text=txt)
        txt = f"G1 X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{500:.1f}"
        msg = (txt+"\n").encode()
        self.serialWrite(msg)

    def ThreadButtonSend(self):
        self.serial_threadSendButton = True
        self.TBS = threading.Thread(
            target=self.sendgcodecommand, name="ThreadButtonSend")
        self.TBS.start()

    def sendgcodecommand(self):
        txt = self.entry.get()+"\n"
        if "G0" in txt or "G1" in txt:
            [x, y, z, e, f] = self.getCurrentPositionArm(txt)
            txt2 = f"X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{f:.1f}"
            txt2 = str(txt2)
            self.labelpos.config(text=txt2)
            self.gcodeParser(txt)

        else:
            self.gcodeParser(txt)

    def updateTemp(self):
        while self.stop_threads == False and self.stop_hotend == False:
            txt = f"M105"
            msg = (str(txt)+"\n").encode()
            self.serialWrite(msg)
            time.sleep(1)

    def hotend_thread(self):

        if self.hotend_thread_state == False and self.stop_hotend == False:
            self.hotend_thread_state = True
            self.TH = threading.Thread(
                target=self.updateTemp, name="ThreadHotend")
            self.TH.start()

        elif self.hotend_thread_state == True and self.stop_hotend == True:
            self.hotend_thread_state = False
            self.TH.join()

    def targetTemp(self, value):
        self.tarTemp = value

    def starthotend(self):
        if self.btn_hotend["relief"] == tk.FLAT:
            self.btn_hotend.config(relief="sunken")
            txt = f"M104 S{self.tarTemp}"
            msg = (str(txt)+"\n").encode()
            self.serialWrite(msg)
            self.stop_hotend = False

        else:
            self.btn_hotend.config(relief=tk.FLAT)
            txt = "M104 S0"
            msg = (txt+"\n").encode()
            self.serialWrite(msg)
            self.stop_hotend = True

        self.hotend_thread()

    def startfan(self):
        if self.btn_fan["relief"] == tk.FLAT:
            self.btn_fan.config(relief="sunken")
            txt = "M106 S255"
            msg = (txt+"\n").encode()
            self.serialWrite(msg)
        else:
            self.btn_fan.config(relief=tk.FLAT)
            txt = "M107"
            msg = (txt+"\n").encode()
            self.serialWrite(msg)

    def home(self):
        txt = "G28"
        msg = (txt+"\n").encode()
        self.serialWrite(msg)

    def emergencyStop(self):
        txt = "M112"
        msg = (txt+"\n").encode()
        self.serialWrite(msg)

        self.stop_threads = True

        imagen = Image.open("Imagenes_3Dbot_software/arm.png")
        imagen = imagen.resize((20, 20), Image.ANTIALIAS)
        self.img_boton_open27 = ImageTk.PhotoImage(imagen)
        self.btn_center.config(image=self.img_boton_open27)

        if self.progress_bar.winfo_viewable():
            self.progress_bar.grid_remove()

        if self.labelprogress.winfo_viewable():
            self.labelprogress.grid_remove()

        if self.hotend_thread_state == True:
            self.hotend_thread_state = False
            print("Apagaré Hotend")
            self.TH.join()
            print("Apagué Hotend")

        if self.serial_writerGcode == True:
            self.serial_writerGcode = False
            print("Apagaré writerGcode")
            self.SWG.join()
            print("Apagué writerGcode")

        if self.serial_threadSendButton == True:
            self.serial_threadSendButton = False
            print("Apagaré HiloBsend")
            self.TBS.join()
            print("Apagué HiloBsend")

        if self.btbase == True:
            self.btbase = False
            print("Apagaré HiloBbase")
            self.SBB.join()
            print("Apagué HiloBbase")

        if self.arm_conected == True:
            self.arm_conected = False
            print("Apagaré brazo")
            self.SR1.join()
            print("Apagué brazo")
            self.btn_conect_arm.config(state="normal")

        if self.base_conected == True:
            self.base_conected = False
            print("Apagaré Base")
            self.SR2.join()
            print("Apagué Base")
            self.btn_conect_base.config(state="normal")

        txt = "X0.0 Y86.0 Z0.0 E0.0 F2000.0"
        self.labelpos.config(text=txt)

        txt = "X0.0 Y0.0 F1800"
        self.labelposBase.config(text=txt)

        self.initialVariables()

        print("Variables Inicializadas")
        if self.arm_conected == False:
            print("Conectaré Brazo")
            self.connectArm()
            print("Conecté Brazo")

        if self.base_conected == False:
            print("Conectaré Base")
            self.connectBase()
            print("Conecté Base")

        self.btn_hotend.config(relief=tk.FLAT)
        self.barra.set(0)
        self.labeltemp.config(text="0")
        self.btn_fan.config(relief=tk.FLAT)
        self.btn_home.config(relief=tk.FLAT)

    def SerialWriterBase(self):
        if not self.gcodeBase.has('F'):
            self.txt_base_terminal.insert(
                tk.END, "F in mm/min is not specified, default value = 1200 mm/min")
            F = 1200

        X = self.gcodeBase.get('X', 0)
        Y = self.gcodeBase.get('Y', 0)
        F = self.gcodeBase.get('F', 0)

        self.txt_base_terminal.insert(tk.END, "Moving Base...\n")
        txt = f"X{X:.1f} Y{Y:.1f} F{F:.1f}"
        txt = str(txt)
        self.labelposBase.config(text=txt)

        self.linearMovement(X, Y, F)
        if self.stop_threads == True:
            return
        self.txt_base_terminal.insert(tk.END, "Finish movement\n")

    def SerialWriterGcode(self):

        self.serial_writerGcode = True
        timeNow = time.time()
        self.txt_arm_terminal.insert(tk.END, "Start...\n")
        self.txt_arm_terminal.see(tk.END)
        with open(self.filepath, 'r') as f:
            self.total_lines = len(f.readlines())
            f.seek(0)
            msg = "Lineas totales: "+str(self.total_lines)+"\n"
            self.txt_arm_terminal.insert(tk.END, msg)
            self.txt_arm_terminal.see(tk.END)
            self.current_line = 1
            for line in f:
                if self.stop_threads != True:
                    percent = (self.current_line+1)/self.total_lines*100
                    percent = round(percent, 1)
                    self.progress.set(percent)
                    self.labelprogress.config(text=str(percent)+"%")
                    self.window.update()
                    while self.fullBufferAlert == True:
                        if self.stop_threads == True:
                            return
                    if not self.gcodeParser(line):
                        break
                    self.current_line += 1
                else:
                    return

        self.msgFromPython = ""
        msg = "Completado en: " + str(time.time()-timeNow)+"\n"
        self.txt_arm_terminal.insert(tk.END, msg)
        self.txt_arm_terminal.see(tk.END)
        # self.SWG.join()

    def startprint(self):

        self.progress_bar.grid(row=0, column=0, sticky="w", padx=5, pady=25)
        self.labelprogress.grid(row=0, column=1, sticky="w", padx=2, pady=25)
        self.SWG = threading.Thread(
            target=self.SerialWriterGcode, name="WriterGcode")
        self.SWG.start()

    def gcodeParser(self, line):
        # Extract the data within the CNC code.
        txt = line
        msg = (line).encode()
        line = line.strip()
        try:
            gcode = GCode.parse_line(line)
            ans = self.gcodeCommands(gcode, msg, txt)
        except (GCodeException) as e:
            print('ERROR ' + str(e))
            return False
        return True

    def gcodeCommands(self, gcode, msg, txt):
        if gcode is None:
            return None

        c = gcode.command()

        if c == 'G0' or c == 'G1':
            self.serialWrite(msg)
            while self.okAlert != True:
                if self.stop_threads == True:
                    return
            self.okAlert = False

        elif c == 'G7':  # Base Movement.
            self.gcodeBase = gcode
            self.SerialWriterBase()

        elif c == 'G92':  # Set coordinates
            [x, y, z, e, f] = self.getCurrentPositionArm(txt)
            txt = f"X{x:.1f} Y{y:.1f} Z{z:.1f} E{e:.1f} F{f:.1f}"
            txt = str(txt)
            self.labelpos.config(text=txt)
            self.serialWrite(msg)

        elif c == 'M302':  # disable cold extrusion prevention.
            self.serialWrite(msg)
            while self.okAlert != True:
                if self.stop_threads == True:
                    return
            self.okAlert = False
            self.txt_arm_terminal.insert(
                tk.END, "disable cold extrusion prevention.\n")
            self.txt_arm_terminal.see(tk.END)

        # Extruder control.
        elif c == 'M104' or c == 'M109':
            if c == 'M104':
                self.stop_hotend = False
                self.hotend_thread()

            if c == 'M109':  # Set the hottend temperature in °C and do nothing until reached
                self.stop_hotend = True
                temp = gcode.get('S', 0)
                self.txt_arm_terminal.insert(
                    tk.END, "Waiting for extruder to heat up.\n")
                txt = "Goal "+"T:"+str(temp)+"\n"
                self.txt_arm_terminal.insert(tk.END, txt)
                self.txt_arm_terminal.see(tk.END)
                self.serialWrite(msg)

                while self.okAlert != True:
                    if self.stop_threads == True:
                        return
                self.okAlert = False
                self.txt_arm_terminal.insert(tk.END, "Temperature reached.\n")
                self.txt_arm_terminal.see(tk.END)

        elif c is None:  # Command not specified(ie just F was passed)
            pass

        else:
            print(msg)
            self.serialWrite(msg)

    def basePublisher(self, vX, vY, lin_time):
        # Velocity publisher.
        msg = {"vX": round(vX, 2), "vY": round(
            vY, 2), "lt": round(lin_time, 4)}
        msg = str(msg)+'\n'
        self.txt_base_terminal.insert(tk.END, msg)
        self.txt_base_terminal.see(tk.END)
        try:
            self.serial_port2.write(msg.encode('utf-8'))
        except:
            pass
        while self.okAlertBase != True:
            if self.stop_threads == True:
                return
        self.okAlertBase = False

    def linearMovement(self, x, y, velocity):
        # Performs linear movements.
        velocity = velocity/60

        coorX = x-self.baseX_1
        coorY = y-self.baseY_1
        totalDist = cmath.sqrt(coorX**2+coorY**2)
        totalDist = totalDist.real
        # print("CoorX: ",coorX)
        # print("CoorY: ",coorY)

        lin_time = totalDist/velocity
        velocity = velocity/1000

        if (coorX == 0):
            tetha = pi/2
        else:
            tetha = atan(abs(coorY)/abs(coorX))

        self.vx = velocity*cos(tetha)
        self.vy = velocity*sin(tetha)

        if (coorX >= 0 and coorY >= 0):
            self.vx = self.vx
            self.vy = self.vy
        elif (coorX < 0 and coorY >= 0):
            self.vx = -self.vx
            self.vy = self.vy
        elif (coorX < 0 and coorY < 0):
            self.vx = -self.vx
            self.vy = -self.vy
        elif (coorX >= 0 and coorY < 0):
            self.vx = self.vx
            self.vy = -self.vy

        self.basePublisher(self.vx*1000, self.vy*1000, lin_time*1000)
        if self.stop_threads == True:
            return
        self.basePublisher(0, 0, 0.5*1000)
        self.baseX_1 = x
        self.baseY_1 = y

    def initialVariables(self):
        self.msgFromMarlin = ""
        self.msgFromPython = ""
        self.fullBufferAlert = False
        self.emptyBufferAlert = False
        self.okAlert = False
        self.otherAlert = False
        self.contOk = 0
        self.lastMsg = ""

        self.baseX_1 = 0
        self.baseY_1 = 0
        self.vx = 0
        self.vy = 0
        self.okAlertBase = False

        if hasattr(self, 'comArm'):
            pass
        else:
            self.comArm = ""

        if hasattr(self, 'comBase'):
            pass
        else:
            self.comBase = ""

        self.i = 0
        self.i2 = 0

        self.xpass = 0
        self.ypass = 80
        self.zpass = 0
        self.epass = 0
        self.fpass = 0

        self.xbpass = 0
        self.ybpass = 0
        self.fbpass = 1800

        self.tarTemp = 0

        self.changeCenter = False

        if hasattr(self, 'seleccion'):
            pass
        else:
            self.seleccion = tk.StringVar(self.window)
            self.seleccion.set(" ")

        if hasattr(self, 'seleccion2'):
            pass
        else:
            self.seleccion2 = tk.StringVar(self.window)
            self.seleccion2.set(" ")

        if hasattr(self, 'filepath'):
            pass
        else:
            self.filepath = ""

        self.stop_threads = False
        self.stop_hotend = False
        self.arm_conected = False
        self.base_conected = False
        self.serial_writerGcode = False
        self.serial_threadSendButton = False
        self.btbase = False
        self.hotend_thread_state = False

        self.progress = tk.DoubleVar()

    def __init__(self):
        # Window -----------------------------------------------------------------------------------------------------------------
        self.window = tk.Tk()
        self.window.title("3Dbot")

        self.window.rowconfigure(1, minsize=450, weight=1)
        self.window.rowconfigure(2, minsize=100, weight=1)

        self.window.columnconfigure(0, minsize=800, weight=1)

        # Initials variables -----------------------------------------------------------------------------------------------------------------

        self.initialVariables()

        # First Row -----------------------------------------------------------------------------------------------------------------
        frm_firstrow = tk.Frame(
            self.window, relief=tk.RAISED, bd=2, bg="white")
        frm_firstrow.grid(row=0, column=0, sticky="nsew")
        frm_firstrow.columnconfigure(4, minsize=1, weight=1)

        imagen = Image.open("Imagenes_3Dbot_software/open.png")
        imagen = imagen.resize((30, 30), Image.ANTIALIAS)
        img_boton_open = ImageTk.PhotoImage(imagen)
        self.btn_open = tk.Button(frm_firstrow, text="Open", image=img_boton_open, compound=tk.TOP, command=self.open_file, border=0, bg="white",
                                  font=('Calibri Light', 10, 'normal'), width=60)

        imagen = Image.open("Imagenes_3Dbot_software/salvar.png")
        imagen = imagen.resize((30, 30), Image.ANTIALIAS)
        img_boton_open2 = ImageTk.PhotoImage(imagen)
        self.btn_save = tk.Button(frm_firstrow, text="Save As", image=img_boton_open2, compound=tk.TOP, command=self.save_file, border=0, bg="white",
                                  font=('Calibri Light', 10, 'normal'), width=60)

        imagen = Image.open("Imagenes_3Dbot_software/arm.png")
        imagen = imagen.resize((30, 30), Image.ANTIALIAS)
        img_boton_open3 = ImageTk.PhotoImage(imagen)
        self.btn_conect_arm = tk.Button(frm_firstrow, text="Conect Arm", image=img_boton_open3, compound=tk.TOP, command=self.connectArm, border=0, bg="white",
                                        font=('Calibri Light', 10, 'normal'), width=60)

        imagen = Image.open("Imagenes_3Dbot_software/base.png")
        imagen = imagen.resize((30, 30), Image.ANTIALIAS)
        img_boton_open4 = ImageTk.PhotoImage(imagen)
        self.btn_conect_base = tk.Button(frm_firstrow, text="Conect Base", image=img_boton_open4, compound=tk.TOP, command=self.connectBase, border=0, bg="white",
                                         font=('Calibri Light', 10, 'normal'), width=60)

        imagen = Image.open("Imagenes_3Dbot_software/post.png")
        imagen = imagen.resize((30, 30), Image.ANTIALIAS)
        img_boton_open28 = ImageTk.PhotoImage(imagen)
        self.btn_post_processing = tk.Button(frm_firstrow, text="Post Processing", image=img_boton_open28, compound=tk.TOP, command=self.postProcessing, border=0, bg="white",
                                             font=('Calibri Light', 10, 'normal'), width=90)

        imagen = Image.open("Imagenes_3Dbot_software/config.png")
        imagen = imagen.resize((30, 30), Image.ANTIALIAS)
        img_boton_open5 = ImageTk.PhotoImage(imagen)
        self.btn_conection_config = tk.Button(frm_firstrow, text="Conection Config", image=img_boton_open5, compound=tk.TOP, command=self.conectionConfig, border=0, bg="white",
                                              font=('Calibri Light', 10, 'normal'), width=90)

        imagen = Image.open("Imagenes_3Dbot_software/stop.png")
        imagen = imagen.resize((30, 30), Image.ANTIALIAS)
        img_boton_open25 = ImageTk.PhotoImage(imagen)
        self.btn_emergency_stop = tk.Button(frm_firstrow, text="Emergency Stop", image=img_boton_open25, compound=tk.TOP, command=self.emergencyStop, border=0, bg="white",
                                            font=('Calibri Light', 10, 'normal'), width=90)

        imagen = Image.open("Imagenes_3Dbot_software/print.png")
        imagen = imagen.resize((30, 30), Image.ANTIALIAS)
        img_boton_open26 = ImageTk.PhotoImage(imagen)
        self.btn_print = tk.Button(frm_firstrow, text="Start Print", image=img_boton_open26, compound=tk.TOP, command=self.startprint, border=0, bg="white",
                                   font=('Calibri Light', 10, 'normal'), width=60)

        self.btn_open.grid(row=0, column=0, sticky="w", padx=5, pady=8)
        self.btn_save.grid(row=0, column=1, sticky="w", padx=5)
        self.btn_conect_arm.grid(row=0, column=2, sticky="w", padx=5)
        self.btn_conect_base.grid(row=0, column=3, sticky="w", padx=5)
        self.btn_print.grid(row=0, column=4, sticky="w", padx=5)
        self.btn_post_processing.grid(row=0, column=5, sticky="e", padx=255)
        self.btn_conection_config.grid(row=0, column=5, sticky="e", padx=130)
        self.btn_emergency_stop.grid(row=0, column=5, sticky="e", padx=5)

        self.frm_progress = tk.Frame(
            frm_firstrow, relief=tk.FLAT, bd=2, bg="white")
        self.frm_progress.grid(row=0, column=4, sticky="wns", padx=100)
        self.frm_progress.columnconfigure(2, minsize=1, weight=1)

        self.progress_bar = ttk.Progressbar(
            self.frm_progress,
            orient="horizontal",
            length=400,
            mode="determinate",
            maximum=100,
            variable=self.progress,
            style="custom.Horizontal.TProgressbar"
        )

        style = ttk.Style()
        style.theme_use('default')
        style.configure("custom.Horizontal.TProgressbar",
                        troughcolor='white', bordercolor='gray', background='gray')

        self.labelprogress = tk.Label(self.frm_progress, bg="white")

        # Second Row -----------------------------------------------------------------------------------------------------------------

        frm_secondrow = tk.Frame(
            self.window, relief=tk.RAISED, bd=2, bg="white")
        frm_secondrow.grid(row=1, column=0, sticky="nsew")
        frm_secondrow.rowconfigure(0, minsize=150, weight=1)
        frm_secondrow.columnconfigure(0, minsize=800, weight=1)
        frm_secondrow.columnconfigure(1, minsize=120, weight=1)

        frm_txt_edit = tk.Frame(
            frm_secondrow, relief=tk.RAISED, bd=2, bg="white")
        frm_txt_edit.grid(row=0, column=0, sticky="nsew", padx=5, pady=0)
        frm_txt_edit.rowconfigure(0, weight=1)
        frm_txt_edit.columnconfigure(0, weight=1)

        self.txt_edit = tk.Text(frm_txt_edit, bg="#E0E0E0")
        deslizador1 = tk.Scrollbar(frm_txt_edit, command=self.txt_edit.yview)
        self.txt_edit.config(yscrollcommand=deslizador1.set)
        self.txt_edit.grid(row=0, column=0, sticky="nsew")
        deslizador1.grid(row=0, column=0, sticky="nse")

        frm_manual_use = tk.Frame(
            frm_secondrow, relief=tk.GROOVE, bd=2, bg="white")
        frm_manual_use.grid(row=0, column=1, sticky="nsew")
        frm_manual_use.columnconfigure([0, 1, 2], minsize=100, weight=1)

        label = tk.Label(frm_manual_use, text="Gcode: ",
                         bg="white", font=("Arial", 12, "italic"))
        self.entry = tk.Entry(frm_manual_use, border=4)
        label.grid(row=0, column=0, sticky="e", pady=10)
        self.entry.grid(row=0, column=1, sticky="we", pady=10)
        self.btn_send = ttk.Button(
            frm_manual_use, text="Enviar", command=self.ThreadButtonSend)
        self.btn_send.grid(row=0, column=2, sticky="w")

        image = tk.PhotoImage(file="Imagenes_3Dbot_software/arm.png")
        imageArm = image.subsample(15, 15)
        self.labelpos = tk.Label(frm_manual_use, bg="white", font=(
            "Bahnschrift Light", 15), image=imageArm, text="X0.0 Y86.0 Z0.0 E0.0 F2000.0", compound="left", padx=10)
        self.labelpos.grid(row=1, column=0, sticky="w", padx=2, pady=2)

        image = tk.PhotoImage(file="Imagenes_3Dbot_software/base.png")
        imageBase = image.subsample(15, 15)
        self.labelposBase = tk.Label(frm_manual_use, bg="white", font=(
            "Bahnschrift Light", 15), image=imageBase, text="X0.0 Y0.0 F1800", compound="left", padx=10)
        self.labelposBase.grid(row=2, column=0, sticky="w", padx=2, pady=2)

        self.labelzaxis = tk.Label(
            frm_manual_use, text="Z Axis", bg="white", font=("Bahnschrift Light", 15))
        self.labelzaxis.grid(row=2, column=1, sticky="we", padx=5, pady=5)

        self.labelextruder = tk.Label(
            frm_manual_use, text="Extruder", bg="white", font=("Bahnschrift Light", 15))
        self.labelextruder.grid(row=2, column=2, sticky="we", padx=5, pady=5)

        frm_manual_usexy = tk.Frame(
            frm_manual_use, relief=tk.FLAT, bd=2, bg="white")
        frm_manual_usexy.grid(row=3, column=0, sticky="we", padx=5, pady=0)
        frm_manual_usexy.rowconfigure([0, 1, 2], minsize=50, weight=1)
        frm_manual_usexy.columnconfigure([0, 1, 2], minsize=50, weight=1)

        imagen = Image.open("Imagenes_3Dbot_software/up.png")
        imagen = imagen.resize((20, 20), Image.ANTIALIAS)
        img_boton_open6 = ImageTk.PhotoImage(imagen)
        self.btn_up = ttk.Button(
            frm_manual_usexy, image=img_boton_open6, command=self.up)

        imagen = Image.open("Imagenes_3Dbot_software/left.png")
        imagen = imagen.resize((20, 20), Image.ANTIALIAS)
        img_boton_open7 = ImageTk.PhotoImage(imagen)
        self.btn_left = ttk.Button(
            frm_manual_usexy, image=img_boton_open7, command=self.left)

        imagen = Image.open("Imagenes_3Dbot_software/right.png")
        imagen = imagen.resize((20, 20), Image.ANTIALIAS)
        img_boton_open8 = ImageTk.PhotoImage(imagen)
        self.btn_right = ttk.Button(
            frm_manual_usexy, image=img_boton_open8, command=self.right)

        imagen = Image.open("Imagenes_3Dbot_software/down.png")
        imagen = imagen.resize((20, 20), Image.ANTIALIAS)
        img_boton_open9 = ImageTk.PhotoImage(imagen)
        self.btn_down = ttk.Button(
            frm_manual_usexy, image=img_boton_open9, command=self.down)

        imagen = Image.open("Imagenes_3Dbot_software/arm.png")
        imagen = imagen.resize((20, 20), Image.ANTIALIAS)
        self.img_boton_open27 = ImageTk.PhotoImage(imagen)
        self.btn_center = ttk.Button(
            frm_manual_usexy, image=self.img_boton_open27, command=self.center)

        self.btn_up.grid(row=0, column=1, sticky="nsew")
        self.btn_left.grid(row=1, column=0, sticky="nsew")
        self.btn_center.grid(row=1, column=1, sticky="nsew")
        self.btn_right.grid(row=1, column=2, sticky="nsew")
        self.btn_down.grid(row=2, column=1, sticky="nsew")

        frm_manual_usez = tk.Frame(
            frm_manual_use, relief=tk.FLAT, bd=2, bg="white")
        frm_manual_usez.grid(row=3, column=1, padx=0, pady=0)
        frm_manual_usez.rowconfigure([0, 1, 2, 3, 4, 5], minsize=40, weight=1)
        frm_manual_usez.columnconfigure(0, minsize=70, weight=1)

        imagen = Image.open("Imagenes_3Dbot_software/up3.png")
        imagen = imagen.resize((20, 20), Image.ANTIALIAS)
        img_boton_open10 = ImageTk.PhotoImage(imagen)
        self.btn_up3z = ttk.Button(frm_manual_usez, text="    10 mm",
                                   compound=tk.LEFT, image=img_boton_open10, command=self.up3z)

        imagen = Image.open("Imagenes_3Dbot_software/up2.png")
        imagen = imagen.resize((20, 20), Image.ANTIALIAS)
        img_boton_open11 = ImageTk.PhotoImage(imagen)
        self.btn_up2z = ttk.Button(frm_manual_usez, text="     1 mm",
                                   compound=tk.LEFT, image=img_boton_open11, command=self.up2z)

        imagen = Image.open("Imagenes_3Dbot_software/up.png")
        imagen = imagen.resize((20, 20), Image.ANTIALIAS)
        img_boton_open12 = ImageTk.PhotoImage(imagen)
        self.btn_upz = ttk.Button(frm_manual_usez, text="  0.1 mm",
                                  compound=tk.LEFT, image=img_boton_open12, command=self.upz)

        imagen = Image.open("Imagenes_3Dbot_software/down.png")
        imagen = imagen.resize((20, 20), Image.ANTIALIAS)
        img_boton_open13 = ImageTk.PhotoImage(imagen)
        self.btn_downz = ttk.Button(frm_manual_usez, text=" -0.1 mm",
                                    compound=tk.LEFT, image=img_boton_open13, command=self.downz)

        imagen = Image.open("Imagenes_3Dbot_software/down2.png")
        imagen = imagen.resize((20, 20), Image.ANTIALIAS)
        img_boton_open14 = ImageTk.PhotoImage(imagen)
        self.btn_down2z = ttk.Button(frm_manual_usez, text="    -1 mm",
                                     compound=tk.LEFT, image=img_boton_open14, command=self.down2z)

        imagen = Image.open("Imagenes_3Dbot_software/down3.png")
        imagen = imagen.resize((20, 20), Image.ANTIALIAS)
        img_boton_open15 = ImageTk.PhotoImage(imagen)
        self.btn_down3z = ttk.Button(frm_manual_usez, text="  -10 mm",
                                     compound=tk.LEFT, image=img_boton_open15, command=self.down3z)

        self.btn_up3z.grid(row=0, column=0, sticky="nsew")
        self.btn_up2z.grid(row=1, column=0, sticky="nsew")
        self.btn_upz.grid(row=2, column=0, sticky="nsew")
        self.btn_downz.grid(row=3, column=0, sticky="nsew")
        self.btn_down2z.grid(row=4, column=0, sticky="nsew")
        self.btn_down3z.grid(row=5, column=0, sticky="nsew")

        frm_manual_useE = tk.Frame(
            frm_manual_use, relief=tk.FLAT, bd=2, bg="white")
        frm_manual_useE.grid(row=3, column=2, sticky="we", padx=0, pady=0)
        frm_manual_useE.rowconfigure([0, 1, 2, 3], minsize=40, weight=1)
        frm_manual_useE.columnconfigure([0, 1], minsize=35, weight=1)

        imagen = Image.open("Imagenes_3Dbot_software/up3.png")
        imagen = imagen.resize((20, 20), Image.ANTIALIAS)
        img_boton_open16 = ImageTk.PhotoImage(imagen)
        self.btn_up3e = ttk.Button(frm_manual_useE, text="    50 mm",
                                   compound=tk.BOTTOM, image=img_boton_open16, command=self.up3e)

        imagen = Image.open("Imagenes_3Dbot_software/up2.png")
        imagen = imagen.resize((20, 20), Image.ANTIALIAS)
        img_boton_open17 = ImageTk.PhotoImage(imagen)
        self.btn_up2e = ttk.Button(frm_manual_useE, text="    10 mm",
                                   compound=tk.BOTTOM, image=img_boton_open17, command=self.up2e)

        imagen = Image.open("Imagenes_3Dbot_software/up.png")
        imagen = imagen.resize((20, 20), Image.ANTIALIAS)
        img_boton_open18 = ImageTk.PhotoImage(imagen)
        self.btn_upe = ttk.Button(frm_manual_useE, text="    1 mm",
                                  compound=tk.BOTTOM, image=img_boton_open18, command=self.upe)

        imagen = Image.open("Imagenes_3Dbot_software/down.png")
        imagen = imagen.resize((20, 20), Image.ANTIALIAS)
        img_boton_open19 = ImageTk.PhotoImage(imagen)
        self.btn_downe = ttk.Button(frm_manual_useE, text="   -1 mm",
                                    compound=tk.TOP, image=img_boton_open19, command=self.downe)

        imagen = Image.open("Imagenes_3Dbot_software/down2.png")
        imagen = imagen.resize((20, 20), Image.ANTIALIAS)
        img_boton_open20 = ImageTk.PhotoImage(imagen)
        self.btn_down2e = ttk.Button(frm_manual_useE, text="   -10 mm",
                                     compound=tk.TOP, image=img_boton_open20, command=self.down2e)

        imagen = Image.open("Imagenes_3Dbot_software/down3.png")
        imagen = imagen.resize((20, 20), Image.ANTIALIAS)
        img_boton_open21 = ImageTk.PhotoImage(imagen)
        self.btn_down3e = ttk.Button(frm_manual_useE, text="  -50 mm",
                                     compound=tk.TOP, image=img_boton_open21, command=self.down3e)

        self.btn_up3e.grid(row=1, column=1, sticky="nsew")
        self.btn_up2e.grid(row=0, column=0, sticky="nsew")
        self.btn_upe.grid(row=1, column=0, sticky="nsew")
        self.btn_downe.grid(row=2, column=0, sticky="nsew")
        self.btn_down2e.grid(row=3, column=0, sticky="nsew")
        self.btn_down3e.grid(row=2, column=1, sticky="nsew")

        frm_manual_temp = tk.Frame(
            frm_manual_use, relief=tk.FLAT, bd=2, bg="white")
        frm_manual_temp.grid(row=4, column=0, sticky="we", padx=0, pady=10)
        frm_manual_temp.rowconfigure(0, minsize=40, weight=1)
        frm_manual_temp.columnconfigure([0, 1], minsize=35, weight=1)

        imagen = Image.open("Imagenes_3Dbot_software/hotend.png")
        imagen = imagen.resize((40, 40), Image.ANTIALIAS)
        img_boton_open22 = ImageTk.PhotoImage(imagen)
        self.btn_hotend = tk.Button(frm_manual_temp, image=img_boton_open22,
                                    command=self.starthotend,
                                    relief=tk.FLAT, background="white")
        self.btn_hotend.grid(row=0, column=0)

        self.barra = tk.Scale(frm_manual_temp, from_=0, to=240,
                              orient='horizontal', background="white", command=self.targetTemp)
        self.barra.grid(row=0, column=1, sticky="we")

        self.labeltemp = tk.Label(
            frm_manual_use, text="T:0°C", bg="white", font=("Bahnschrift Light", 15))
        self.labeltemp.grid(row=4, column=1, sticky="w", padx=10, pady=5)

        frm_manual_fan_home = tk.Frame(
            frm_manual_use, relief=tk.FLAT, bd=2, bg="white")
        frm_manual_fan_home.grid(row=4, column=2, sticky="we", padx=0, pady=10)
        frm_manual_fan_home.rowconfigure(0, minsize=40, weight=1)
        frm_manual_fan_home.columnconfigure([0, 1], minsize=35, weight=1)

        imagen = Image.open("Imagenes_3Dbot_software/fan.png")
        imagen = imagen.resize((40, 40), Image.ANTIALIAS)
        img_boton_open23 = ImageTk.PhotoImage(imagen)
        self.btn_fan = tk.Button(frm_manual_fan_home, image=img_boton_open23,
                                 command=self.startfan, relief=tk.FLAT, background="white")

        imagen = Image.open("Imagenes_3Dbot_software/home.png")
        imagen = imagen.resize((40, 40), Image.ANTIALIAS)
        img_boton_open24 = ImageTk.PhotoImage(imagen)
        self.btn_home = tk.Button(frm_manual_fan_home, image=img_boton_open24,
                                  command=self.home, relief=tk.FLAT, background="white")

        self.btn_fan.grid(row=0, column=0)
        self.btn_home.grid(row=0, column=1)

        # Third Row -----------------------------------------------------------------------------------------------------------------

        frm_thirdrow = tk.Frame(
            self.window, relief=tk.RAISED, bd=2, bg="white")
        frm_thirdrow.grid(row=2, column=0, sticky="nsew")
        frm_thirdrow.rowconfigure(0, minsize=40, weight=1)
        frm_thirdrow.rowconfigure(1, minsize=100, weight=1)
        frm_thirdrow.columnconfigure(0, minsize=400, weight=1)
        frm_thirdrow.columnconfigure(1, minsize=400, weight=1)

        label_arm_terminal = tk.Label(
            frm_thirdrow, text="Arm Terminal", bg="white", font=("Bahnschrift Light", 12))
        label_arm_terminal.grid(row=0, column=0, sticky="w", padx=5, pady=0)

        label_base_terminal = tk.Label(
            frm_thirdrow, text="Base Terminal", bg="white", font=("Bahnschrift Light", 12))
        label_base_terminal.grid(row=0, column=1, sticky="w", padx=5, pady=0)

        frm_arm_terminal = tk.Frame(
            frm_thirdrow, relief=tk.RAISED, bd=2, bg="white")
        frm_arm_terminal.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        frm_arm_terminal.rowconfigure(0, weight=1)
        frm_arm_terminal.columnconfigure(0, weight=1)
        self.txt_arm_terminal = tk.Text(frm_arm_terminal, bg="#E0E0E0")
        deslizador2 = tk.Scrollbar(
            frm_arm_terminal, command=self.txt_arm_terminal.yview)
        self.txt_arm_terminal.config(yscrollcommand=deslizador2.set)
        self.txt_arm_terminal.grid(row=0, column=0, sticky="nsew")
        deslizador2.grid(row=0, column=0, sticky="nse")

        frm_base_terminal = tk.Frame(
            frm_thirdrow, relief=tk.RAISED, bd=2, bg="white")
        frm_base_terminal.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        frm_base_terminal.rowconfigure(0, weight=1)
        frm_base_terminal.columnconfigure(0, weight=1)
        self.txt_base_terminal = tk.Text(frm_base_terminal, bg="#E0E0E0")
        deslizador3 = tk.Scrollbar(
            frm_base_terminal, command=self.txt_base_terminal.yview)
        self.txt_base_terminal.config(yscrollcommand=deslizador3.set)
        self.txt_base_terminal.grid(row=0, column=0, sticky="nsew")
        deslizador3.grid(row=0, column=0, sticky="nse")

        self.window.mainloop()


if __name__ == "__main__":
    be = GUI3Dbot()
