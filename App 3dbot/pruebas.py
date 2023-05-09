import tkinter as tk

# paleta de colores para el modo claro
light_bg = 'white'
light_fg = 'black'

# paleta de colores para el modo oscuro
dark_bg = '#292929'
dark_fg = 'white'

# función para cambiar los colores de los widgets
def change_theme(theme):
    if theme == 'light':
        bg_color = light_bg
        fg_color = light_fg
    elif theme == 'dark':
        bg_color = dark_bg
        fg_color = dark_fg
    else:
        return

    # cambia el color de fondo y de primer plano de cada widget
    for widget in root.winfo_children():
        widget.config(bg=bg_color, fg=fg_color)

# crea la ventana principal
root = tk.Tk()

# crea algunos widgets
label = tk.Label(root, text='Hello World!')
entry = tk.Entry(root)
button = tk.Button(root, text='Change Theme', command=lambda: change_theme('dark'))

# coloca los widgets en la ventana
label.pack()
entry.pack()
button.pack()

# establece el tema claro como predeterminado
change_theme('light')

# inicia el bucle de eventos
root.mainloop()