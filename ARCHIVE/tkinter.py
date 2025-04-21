import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageEnhance, ImageTk
import sys
import os

is_workingdir_set = False
is_outdir_set = False

current_version = "1.2"

output_directory = ""  # Set output directory

if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(__file__)

window = None


def create_window():
    global is_workingdir_set
    global is_outdir_set
    global base_dir
    global window
    window = tk.Tk()
    window.title("Árpád Média vízjelező")
    window.geometry("400x350")

    # Set folder icon
    folder_icon_photo = Image.open(os.path.join(base_dir, 'folder.png'))
    folder_icon_photo = folder_icon_photo.resize((20, 20), Image.LANCZOS)

    folder_icon = ImageTk.PhotoImage(folder_icon_photo)

    # Set the window size fix
    window.resizable(False, False)
    window.minsize(400, 350)

    # Set window icon
    window.iconbitmap(os.path.join(base_dir, 'logo.ico'))

    progress = ttk.Progressbar(
        window, orient="horizontal", length=350, mode="determinate")

    # Set title label
    title_label = tk.Label(window, text="Árpád Média vízjelező", font=(
        "Arial", 20, "bold"), fg="#1c265a")
    title_label.grid(row=0, column=0, pady=10)

    # Set working directory
    directory_label = tk.Label(
        window, text="Vízjelezendő képek: ", font=("Arial", 11, "bold"))
    directory_label.grid(row=1, column=0, padx=10, pady=10, sticky="W")

    set_dir_button = tk.Button(
        window, text="Tallózás", image=folder_icon, compound="left", command=lambda: set_working_directory(), font=("Arial", 10), relief="raised", cursor="hand2", bg="grey", fg="white")
    set_dir_button.grid(row=1, column=0, padx=10, pady=10, sticky="E")

    # Set project name
    project_name_label = tk.Label(
        window, text="Vízjelezett képek neve: ", font=("Arial", 12, "bold"))
    project_name_label.grid(row=3, column=0, padx=10, pady=0)

    project_name_input = tk.Entry(window, width=20, font=("Arial", 12))
    project_name_input.grid(row=4, column=0, padx=10, pady=5)

    # Set output directory
    output_label = tk.Label(window, text="Mentés ide: ",
                            font=("Arial", 12, "bold"))
    output_label.grid(row=5, column=0, padx=10, pady=10, sticky="W")

    set_out_button = tk.Button(
        window, text="Tallózás", image=folder_icon, compound="left", command=lambda: set_output_directory(), font=("Arial", 10), relief="raised", cursor="hand2", bg="grey", fg="white")
    set_out_button.grid(row=5, column=0, padx=10, pady=10, sticky="E")

    def watermark_and_progress():
        if not is_workingdir_set or not is_outdir_set:
            messagebox.showerror("Hiba", "Nincs mappa kiválasztva")
            return
        progress['value'] = 0
        window.update()
        project_name = project_name_input.get()
        done_watermaring = watermark(project_name, progress)

        if done_watermaring:
            # Show message box
            messagebox.showinfo("Siker", "A vízjelezés befejeződött")

        # Open the output directory
        os.startfile(output_directory)

    submit_button = tk.Button(
        window,
        text="Mehet!",
        command=lambda: watermark_and_progress(),
        bg="green",
        fg="white",
        font=("Arial", 12, "bold"),
        width=10,
        height=1,
        relief="raised",
        cursor="hand2")
    submit_button.grid(row=7, column=0, padx=10, pady=10)

    progress.grid(row=8, column=0, padx=10, pady=10)

    # Author label
    author_label = tk.Label(
        window, text="Készítette: Kerkuska Máté", font=("Arial", 8))
    author_label.grid(row=9, column=0)

    current_version_label = tk.Label(
        window, text=f"Verzió: {current_version}", font=("Arial", 8, "italic"))
    current_version_label.grid(row=10, column=0)

    # Configure the columns to equally distribute space
    window.grid_columnconfigure(0, weight=1)

    window.update_idletasks()

    # Get the screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate the position to center the window
    position_top = int(screen_height / 2 - window.winfo_height() / 2)
    position_right = int(screen_width / 2 - window.winfo_width() / 2)

    # Position the window
    window.geometry("+{}+{}".format(position_right, position_top))

    window.mainloop()


def set_working_directory():
    global window
    global is_workingdir_set
    dir_path = filedialog.askdirectory()
    if dir_path:
        os.chdir(dir_path)
        # Updateing working directories
        is_workingdir_set = True
        current_dir_label = window.winfo_children()[3]

        if (dir_path.__len__() > 30):
            shorted_dir_path = "..." + dir_path[-30:]
        else:
            shorted_dir_path = dir_path
        current_dir_label.config(text=f"{shorted_dir_path}")

        window.update()
        print(f"Working directory set to {dir_path}")


def set_output_directory():
    global window
    global is_outdir_set
    global output_directory
    dir_path = filedialog.askdirectory()
    if dir_path:
        output_directory = dir_path
        # Updateing output directories
        is_outdir_set = True
        output_dir_label = window.winfo_children()[7]

        if (dir_path.__len__() > 40):
            shorted_dir_path = "..." + dir_path[-40:]
        else:
            shorted_dir_path = dir_path


        output_dir_label.config(text=f"{shorted_dir_path}")

        window.update()
        print(f"Output directory set to {dir_path}")


def watermark(project_name, progress_bar):

    global window
    try:
        global is_workingdir_set
        global is_outdir_set
        global output_directory
        global base_dir
        print("Watermarking...")

        directory = os.getcwd()
        watermark_image_path = os.path.join(base_dir, 'watermark.png')

        images = [f for f in os.listdir(directory) if f.endswith(
            ('.png', '.jpg', '.jpeg', '.JPG', '.JPEG', '.PNG'))]

        progress_length = len(images)

        i = 0

        for filename in images:

            i += 1
            image_path = os.path.join(directory, filename)
            image = Image.open(image_path).convert("RGBA")

            # Check for EXIF data (only available for .jpg)
            if 'exif' in image.info and filename.lower().endswith(('.jpg', '.jpeg')):
                exif_data = image.getexif()
                if exif_data:
                    for tag, value in exif_data.items():
                        if tag == 274:  # 274 is the tag for Orientation
                            if value == 3:  # Rotated 180 degrees
                                image = image.rotate(180)
                            elif value == 6:  # Rotated 90 degrees to the right
                                image = image.rotate(-180)
                                image = image.transpose(
                                    Image.Transpose.ROTATE_90)
                            elif value == 8:  # Rotated 90 degrees to the left
                                image = image.rotate(+180)
                                image = image.transpose(
                                    Image.Transpose.ROTATE_270)

            # Scale watermark
            watermark = Image.open(watermark_image_path).convert("RGBA")

            # Create an enhancer for the alpha channel
            enhancer = ImageEnhance.Brightness(watermark.split()[3])

            # Reduce the brightness of the alpha channel to make the watermark 50% transparent
            watermark.putalpha(enhancer.enhance(0.5))

            # Get the image dimensions
            image_width, image_height = image.size

            if image_width < image_height:
                scaling_factor = image_height
            else:
                scaling_factor = image_width
            # Set watermark size
            watermark_size = (scaling_factor // 11, scaling_factor // 11)

            watermark = watermark.resize(watermark_size, Image.LANCZOS)

            if project_name == "":
                project_name = filename.split('.')[0]

            # Set watermark image name
            converted_image_path = f"{output_directory}\{project_name}-{i}.{filename.split('.')[1]}"
            # print(converted_image_path)

            # Change position if needed
            width, height = image.size
            watermark_width, watermark_height = watermark.size
            position = (width - (watermark_width + 15),
                        height - (watermark_height + 8))

            image.paste(watermark, position, watermark)

            rgb_image = image.convert("RGB")
            rgb_image.save(converted_image_path)
            progress_bar['value'] += 100 / progress_length
            window.update()

        print("Watermarking complete")

        # Updateing selected directories

        is_workingdir_set = False
        current_dir_label = window.winfo_children()[3]
        current_dir_label.config(text="Mappa")

        is_outdir_set = False
        output_dir_label = window.winfo_children()[7]
        output_dir_label.config(text="Mappa")

        progress_bar['value'] = 100
        window.update()
        return True
    except Exception as e:
        print(e)
        messagebox.showerror("Hiba", "Hiba történt a vízjelezés közben")
        return False


try:
    create_window()
except Exception as e:
    print(e)
    sys.exit(1)
