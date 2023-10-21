import customtkinter as ctk
import pandas as pd
import requests
import matplotlib.pyplot as plt
import threading

# Ставим темную тему
ctk.set_appearance_mode("dark")

# Ставим тему dark-blue
ctk.set_default_color_theme("dark-blue")

# Создаем главное окно
root = ctk.CTk()
root.geometry("640x480")
root.title("3d Graphs")

# Создаем фрейм внутри главного окна
frame = ctk.CTkFrame(master=root)
frame.pack(pady=20, padx=20, fill="both", expand=True)

# Создаем список для хранения параметров
parametrs = ["Гумус","P","K","Mn","Co","Cu","Zn","B","Ca","Mg","N_NH4","N_NO3","NDVI"]

name = ""
def optionmenu_callback(choice):
    global name
    name = choice
    button.configure(state="normal")

# Функция для получения высоты по координатам с использованием API opentopodata.org
def get_elevations(latitude, longitude):
    locations = []
    for i in range(len(latitude)):
        locations.append(f"{latitude[i]},{longitude[i]}|")
    locations = ''.join(locations)
    locations = locations[:-1]
    url = f"https://api.opentopodata.org/v1/aster30m?locations={locations}"

    try:
        response = requests.get(url)
    except:
        return None
    
    data = response.json()
    elevations = []
    for result in data['results']:
        elevations.append(result['elevation'])
    return elevations

def makeGraph():
    global name
    if name not in data.columns:
        print("Неверный параметр")
        return
    
    cmap = plt.cm.rainbow

    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.scatter3D(X, Y, elevations, c=data[name], cmap=cmap)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # Отображаем цветовую шкалу
    fig.colorbar(ax.scatter(X, Y, elevations, c=data[name], cmap=cmap), shrink=0.5, aspect=5)
    plt.title(name)
    plt.show()

# Список для хранения высот
elevations = []

# Функция для получения высоты в отдельном потоке
def get_elevations_thread(latitude, longitude):
    print("Получение данных о высоте")
    global elevations
    elevations = get_elevations(latitude, longitude)
    if elevations != None:
        print("Данные о высоте получены")
        optionmenu.configure(state="normal")
    else:
        raise Exception("Ошибка при получении данных о высоте. Возможно, отсутствует подключение к интернету")
        
# Получение координат из файла
data = pd.read_csv('altitude.csv')
X = data[['X']]
Y = data[['Y']]

# Запускаем поток для получения высоты
elevation_thread = threading.Thread(target=get_elevations_thread, args=(Y['Y'], X['X']))
elevation_thread.start()

width = 0.4
# Создаем выпадающий список для выбора параметра
optionmenu_var = ctk.StringVar(value="Выберите параметр")
optionmenu = ctk.CTkOptionMenu(master=frame, values=parametrs,command=optionmenu_callback, variable=optionmenu_var, font=("Roboto", 14), state="disabled")
optionmenu.place(relx=(1-width)/2, rely=0.2, relwidth=width, relheight=0.05)

# Создаем кнопку для отображения графика
button = ctk.CTkButton(master=frame, text="Построить график", command=makeGraph, font=("Roboto", 20, "bold"), state="disabled")
button.place(relx=(1-width)/2, rely=0.7, relwidth=width, relheight=0.1)

root.mainloop()