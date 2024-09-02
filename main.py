# DEVELOPED BY JOSEPH SANTAMARIA
import flet as ft
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
import mutagen
import base64
import os
import json
import time
import random
import math
import requests
import win32api
import threading
############################################## Version ##############################################
__version__ = '1.4'
# ------------------------------------------------------------------------------------------------------
############################################## Nombre de la app ##############################################
_AppName_ = 'Beatmash_Setup'

Name = 'Beatmash'
# ------------------------------------------------------------------------------------------------------

def main(page: ft.Page):
    page.fonts = page.fonts = {
        "Baloo": "/fonts/Baloo2.ttf"
    }
    page.title = "beatmash"
    default_config = {
            "volume_value": 1,
            "volume_text": 100,
            "directory_config": None,
            "music_config": None,

    }

    if not os.path.exists("config.json"):
        default_config = {
            "volume_value": 1,
            "volume_text": 100,
            "directory_config": None,
            "music_config": None,
    
        }
        with open("config.json", "w") as f:
            json.dump(default_config, f)

    def close_banner(e):
        page.banner.open = False
        page.update()

    page.banner = ft.Banner(bgcolor="#282f36")
    def show_banner_click():
        page.banner.open = True
        page.update()

    # def download_update(e):
    #     requests.get(link_app_update, stream=True)
    pb = ft.ProgressBar(visible = False)
    def download_update(e):
        if not os.path.exists('tmp'):
            os.makedirs('tmp')
        response_url = requests.get(
                'https://raw.githubusercontent.com/JosephASG/app-versions/main/version-beatmash.txt')
        data_url = response_url.text
        with requests.get(data_url, stream=True) as r:
            # pb.value = int(r.headers.get('Content-Length'))
            # print(int(r.headers.get('Content-Length')))
            pb.visible = True
            r.raise_for_status()
            with open(f'tmp/{_AppName_}-{__version__}.exe', 'wb') as f:
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        pb.visible = True
                        page.update()
            close_banner(None)
        win32api.ShellExecute(0, 'open', f'tmp\\{_AppName_}-{__version__}.exe', None, None, 10)
        if close_banner(e):
            try:
                os.remove('tmp')
            except Exception as error:
                pass
        pb.visible = False
        pb.update()
        # button1.config(text='Install', state=tk.NORMAL)
    
    def check_updates():
        try:
            # -- Online Version File
            # -- Replace the url for your file online with the one below.
            response = requests.get(
                'https://raw.githubusercontent.com/JosephASG/app-versions/main/update-beatmash.txt')
            data = response.text
            print(data)

            if float(data) > float(__version__):
                show_banner_click()
                page.banner.leading=ft.Icon(ft.icons.WARNING_AMBER_ROUNDED, color=ft.colors.AMBER, size=40)
                page.banner.content = ft.Container(
                    ft.Column([
                        ft.Text(f"New update available v{__version__}",font_family="Baloo", size=24, color="#ECC183"),
                        ft.Text(f"Do you want to install the new {Name} update?",font_family="Baloo", size=16, color="#ECC183"),
                        pb
                    ])
                )
                page.banner.actions=[
                    ft.TextButton("Yes", on_click=download_update),
                    ft.TextButton("No", on_click=close_banner),
                ]
            else:
                pass
                # messagebox.showinfo('Software Update', 'No Updates are Available.')
        except requests.exceptions.ConnectionError:
            page.banner.leading=ft.Icon(ft.icons.WARNING_AMBER_ROUNDED, color=ft.colors.AMBER, size=40)
            page.banner.content = ft.Container(
                ft.Column([
                    ft.Text(f"Update Error",font_family="Baloo", size=24, color="#ECC183"),
                    ft.Text(f"Error: No internet connection 🌐",font_family="Baloo", size=16, color="#ECC183")
                ]), padding=ft.padding.symmetric(vertical=30)
            )
            page.banner.actions=[
                ft.TextButton("Okay", on_click=close_banner),
            ]
            show_banner_click()
    check_updates()
    
    # Crear un diccionario con las opciones por defecto
    def save_config(volume_value, volume_text, directory_config, music_config):
        config = {
            "volume_value": volume_value,
            "volume_text": volume_text,
            "directory_config": directory_config,
            "music_config": music_config,
        }

        try:
            with open("config.json", "w") as archivo:
                json.dump(config, archivo)
        except FileNotFoundError:
            config = default_config
        # Guardar las configuraciones en un archivo
            # Crear un diccionario con las opciones por defecto

    def load_config():
        try:
            # Cargar las configuraciones desde un archivo
            with open("config.json", "r") as archivo:
                config = json.load(archivo)
                return config
        except FileNotFoundError:
            config = default_config

    # Acceder a las configuraciones
    conf = load_config()
    version = f"v{__version__}"
    text_splash_info = ft.Text(font_family="Baloo 2", size=16)
    splash_container = ft.Container(ft.Column([
        ft.Container(
            ft.Image(
                src=f"/beatmash-logo.png",
                width=300,
                # height=80,
                fit=ft.ImageFit.COVER,
                repeat=ft.ImageRepeat.NO_REPEAT,
                border_radius=ft.border_radius.all(10),
            ),alignment=ft.alignment.center
        ),
        ft.Container(ft.Text(f"Beatmash {version}",font_family="Baloo 2", size=16), alignment=ft.alignment.center),
        ft.Container(text_splash_info,alignment=ft.alignment.center),
        ft.Container(ft.ProgressBar(width=400), alignment=ft.alignment.center)
    ], alignment=ft.MainAxisAlignment.CENTER), alignment=ft.alignment.center)
    page.splash = splash_container


    # Pick files dialog
    selected_files = ft.Text(font_family='Baloo')
    length_text = ft.Text(font_family='Baloo', size=16)
    global flag_animation
    flag_animation = False
    def pick_files_result(e: ft.FilePickerResultEvent):
        title_text.offset = ft.transform.Offset(0, 0)   
        selected_files.value = (
            ", ".join(map(lambda f: f.path, e.files)) if e.files else "Cancelled!"
        )
        slider_position.disabled = False
        image_album.src_base64 = None
        page.update()
        # Obtiene la información del archivo de música
        load_music_function(selected_files.value, e=e)
        
    

    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)

    music_list_view = ft.Column(height=200, scroll=True)
    music_list = []
    global btn_select_song
    last_songs = []
    
    song_index = 0
    random_play = False
    play_last = False

    def toggle_random_play(e):
        nonlocal random_play
        random_play = not random_play
        random_play_btn_icon_active.visible = not random_play
        random_play_btn_icon_unactive.visible = random_play
        page.update()

    random_play_btn_icon_unactive = ft.Container(
        ft.IconButton(icon=ft.icons.SHUFFLE_ROUNDED, on_click=toggle_random_play, icon_color="#ffffff", tooltip="Desactivar reproducción aleatoria"), 
        visible=random_play, bgcolor="#353446", border_radius=9999)
    random_play_btn_icon_active = ft.Container(
        ft.IconButton(icon=ft.icons.SHUFFLE_ROUNDED, on_click=toggle_random_play, tooltip="Activar reproducción aleatoria", icon_color="#ffffff"), 
        visible=not random_play)
    

    def toggle_loop_song(e):
        nonlocal play_last
        play_last = not play_last
        loop_play_btn_icon_active.visible = not play_last
        loop_btn_icon_unactive.visible = play_last
        page.update()

    loop_btn_icon_unactive = ft.Container(
        ft.IconButton(icon=ft.icons.REPEAT_ROUNDED, on_click=toggle_loop_song, icon_color="#ffffff", tooltip="Desactivar repetición"), 
        visible=play_last, bgcolor="#353446", border_radius=9999)
    loop_play_btn_icon_active = ft.Container(
        ft.IconButton(icon=ft.icons.REPEAT_ROUNDED, on_click=toggle_loop_song, tooltip="Activar repetición", icon_color="#ffffff"), 
        visible=not play_last)

    def play_audio(src, index):
        nonlocal song_index
        song_index = index
        audio1.src = src
        btn_play.visible = False
        btn_pause.visible = True
        btn_resume.visible = False
        page.update()
        load_music_function(src, None)
        audio1.play()
        save_config(round(slider_volumen.value, 2), info_volume_text.value, directory_path.value, audio1.src)

    def on_hover(e):
        e.control.bgcolor = ft.colors.WHITE10 if e.data == "true" else None
        e.control.update()

    def load_all(e):
        music_list.clear()
        try:
            aux = 0
            time_duration_total_musiclist = 0
            directory_path.value = conf["directory_config"]
            btn_launch_dir_playlist.text = conf["directory_config"]
            if directory_path.value:
                slider_position.disabled = False
                # Obtiene una lista de archivos MP3 en la carpeta
                for filename in os.listdir(directory_path.value):
                    if filename.endswith(".mp3"):
                        aux+=1
                        path = os.path.join(directory_path.value, filename)
                        global btn_select_song
                        music_list.append({"id":aux,"ruta":path, "nombre":filename})
                        # print(aux)
                
                for song in music_list:
                    # Abrir el archivo de audio y buscar la imagen de álbum
                    try:
                        audio = MP3(song["ruta"])
                        # tags = ID3(song["ruta"])
                        time_duration_total = str(int(audio.info.length // 60)) + ":" + str(int(audio.info.length % 60)).zfill(2)
                        time_duration_total_musiclist = time_duration_total_musiclist + int(audio.info.length)
                    except Exception as Error:
                        pass
                    btn_launch_dir_playlist.visible = True
                    text_info_path.value = directory_path.value
                    text_info_len_musicList.value = f"{aux} canciones"
                    text_info_duration_musicList.value = str(int(time_duration_total_musiclist // 3600)) + " h " + str(int(time_duration_total_musiclist % 60)).zfill(2) + " min"
                    # btn_obj = ft.TextButton(str(song["id"]) +". " + song["nombre"], on_click=lambda e, src=song["ruta"], index=song["id"]-1: play_audio(src, index))
                    try:
                        btn_obj = ft.Container(
                            ft.Row([
                                ft.Container(ft.Text(str(song["id"]), font_family='Baloo'), alignment=ft.alignment.center, 
                                        margin=ft.margin.symmetric(horizontal=10)),
                                ft.Container(
                                    ft.Row([
                                        ft.Container(
                                            ft.Column([
                                                ft.Text(audio["TIT2"].text[0], font_family='Baloo'),
                                                ft.Text(audio["TPE1"].text[0], font_family='Baloo')
                                            ]), expand=True, 
                                            margin=ft.margin.symmetric(horizontal=10)
                                        ),
                                        ft.Container(ft.Text(audio["TALB"].text[0], font_family='Baloo'), expand=True, margin=ft.margin.symmetric(horizontal=20)),
                                        ft.Container(ft.Text(time_duration_total, font_family='Baloo'), expand=True, margin=ft.margin.symmetric(horizontal=20)),
                                        
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), expand=True, alignment=ft.alignment.center, 
                                        
                                )
                            ]), on_click=lambda e, src=song["ruta"], index=song["id"]-1: play_audio(src, index), on_hover=on_hover,  padding=ft.padding.symmetric(vertical=5), margin=ft.margin.symmetric(vertical=0), border_radius=15
                        )
                        
                    except Exception as Error:
                        btn_obj = ft.Container(
                            ft.Row([
                                ft.Container(ft.Text(str(song["id"]), font_family='Baloo'), alignment=ft.alignment.center, 
                                        margin=ft.margin.symmetric(horizontal=10)),
                                ft.Container(
                                    ft.Row([
                                        ft.Container(
                                            ft.Column([
                                                ft.Text(song['nombre']),
                                                ft.Text("Artista desconocido", font_family='Baloo')
                                            ]), expand=True, 
                                            margin=ft.margin.symmetric(horizontal=10)
                                        ),
                                        ft.Container(ft.Text("Álbum desconocido", font_family='Baloo'), expand=True, margin=ft.margin.symmetric(horizontal=20)),
                                        ft.Container(ft.Text(time_duration_total, font_family='Baloo'), expand=True, margin=ft.margin.symmetric(horizontal=20)),
                                        
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), expand=True, alignment=ft.alignment.center, 
                                        
                                )
                            ]), on_click=lambda e, src=song["ruta"], index=song["id"]-1: play_audio(src, index), on_hover=on_hover,  padding=ft.padding.symmetric(vertical=5), margin=ft.margin.symmetric(vertical=0), border_radius=15
                        )
                    music_list_view.controls.append(btn_obj)
                load_music_function(conf['music_config'], None)
                
                btn_play.visible = True
                btn_pause.visible = False
                btn_resume.visible = False
                page.update()
            page.splash.visible = False
        except Exception as Error:
            pass
            page.splash.visible = False
    
    def get_directory_result(e: ft.FilePickerResultEvent):
        music_list.clear()
        music_list_view.controls.clear()
        btn_play.visible = False
        btn_pause.visible = True
        btn_resume.visible = False
        audio1.autoplay = True
        directory_path.value = e.path if e.path else directory_path.value
        btn_launch_dir_playlist.text = e.path if e.path else directory_path.value
        page.update()
        aux = 0
        time_duration_total = ''
        time_duration_total_musiclist = 0
        if directory_path.value:
            slider_position.disabled = False
        # Obtiene una lista de archivos MP3 en la carpeta
            save_config(round(slider_volumen.value, 2), info_volume_text.value, directory_path.value, audio1.src)
            for filename in os.listdir(directory_path.value):
                if filename.endswith(".mp3"):
                    aux+=1
                    path = os.path.join(directory_path.value, filename)
                    global btn_select_song
                    music_list.append({"id":aux,"ruta":path, "nombre":filename})
                    # print(aux)
            
            for song in music_list:
                # Abrir el archivo de audio y buscar la imagen de álbum
                try:
                    audio = MP3(song["ruta"])
                    # tags = ID3(song["ruta"])
                    time_duration_total = str(int(audio.info.length // 60)) + ":" + str(int(audio.info.length % 60)).zfill(2)
                    time_duration_total_musiclist = time_duration_total_musiclist + int(audio.info.length)
                except Exception as Error:
                    pass
                # btn_obj = ft.TextButton(str(song["id"]) +". " + song["nombre"], on_click=lambda e, src=song["ruta"], index=song["id"]-1: play_audio(src, index))
                try:
                    btn_obj = ft.Container(
                        ft.Row([
                            ft.Container(ft.Text(str(song["id"]), font_family='Baloo'), alignment=ft.alignment.center, 
                                    margin=ft.margin.symmetric(horizontal=10)),
                            ft.Container(
                                ft.Row([
                                    ft.Container(
                                        ft.Column([
                                            ft.Text(audio["TIT2"].text[0], font_family='Baloo'),
                                            ft.Text(audio["TPE1"].text[0], font_family='Baloo')
                                        ]), expand=True, 
                                        margin=ft.margin.symmetric(horizontal=10)
                                    ),
                                    ft.Container(ft.Text(audio["TALB"].text[0], font_family='Baloo'), expand=True, margin=ft.margin.symmetric(horizontal=20)),
                                    ft.Container(ft.Text(time_duration_total, font_family='Baloo'), expand=True, margin=ft.margin.symmetric(horizontal=20)),
                                    
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), expand=True, alignment=ft.alignment.center, 
                                    
                            )
                        ]), on_click=lambda e, src=song["ruta"], index=song["id"]-1: play_audio(src, index), on_hover=on_hover,  padding=ft.padding.symmetric(vertical=5), border_radius=15
                    )
                    # print(audio["TIT2"].text[0])
                    # print(audio["TPE1"].text[0])
                except Exception as Error:
                    btn_obj = ft.Container(
                        ft.Row([
                            ft.Container(ft.Text(str(song["id"]), font_family='Baloo'), alignment=ft.alignment.center, 
                                    margin=ft.margin.symmetric(horizontal=10)),
                                    
                            # ft.Image(src_base64=album_base64, width=50, fit=ft.ImageFit.COVER,
                            #     repeat=ft.ImageRepeat.NO_REPEAT,
                            #     border_radius=ft.border_radius.all(10),), 
                            ft.Container(
                                ft.Row([
                                    ft.Container(
                                        ft.Column([
                                            ft.Text(song["nombre"], font_family='Baloo'),
                                            ft.Text("Artista desconocido", font_family='Baloo')
                                        ]), expand=True, 
                                        margin=ft.margin.symmetric(horizontal=10)
                                    ),
                                    ft.Container(ft.Text("Álbum desconocido", font_family='Baloo'), expand=True, margin=ft.margin.symmetric(horizontal=20)),
                                    ft.Container(ft.Text(time_duration_total, font_family='Baloo'), expand=True, margin=ft.margin.symmetric(horizontal=20)),
                                    
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), expand=True, alignment=ft.alignment.center, 
                                    
                            )
                        ]), on_click=lambda e, src=song["ruta"], index=song["id"]-1: play_audio(src, index), on_hover=on_hover,  padding=ft.padding.symmetric(vertical=5), border_radius=15
                    )
                music_list_view.controls.append(btn_obj)
            load_music_function(music_list[0]['ruta'], e=e)
            text_info_path.value = directory_path.value
            text_info_len_musicList.value = f"{aux} canciones"
            text_info_duration_musicList.value = str(int(time_duration_total_musiclist // 3600)) + " h " + str(int(time_duration_total_musiclist % 60)).zfill(2) + " min"
        btn_launch_dir_playlist.visible = True
        page.update()

    get_directory_dialog = ft.FilePicker(on_result=get_directory_result)
    directory_path = ft.Text(font_family='Baloo', expand=True)  

    def launch_dir_playlist(e):
        page.launch_url(url=directory_path.value, web_window_name=directory_path.value)
    btn_launch_dir_playlist = ft.TextButton(icon=ft.icons.FOLDER_ROUNDED, on_click=launch_dir_playlist, visible=False, style=ft.ButtonStyle(
                                color={
                                    ft.MaterialState.HOVERED: "#0aa2dd",
                                    ft.MaterialState.DEFAULT: "#7e8095",
                                },
                            ))

    def load_music_function(path, e):
        try:
            audio = MP3(path)
            title_text.value = audio["TIT2"].text[0]
            artist_text.value = audio["TPE1"].text[0]
            album_text.value = audio["TALB"].text[0]
            length_text.value = audio.info.length
            audio1.src = path
            audio1.visible = True
            page.update()
        except Exception as Error:
            audio_exp = mutagen.File(path)
            title_text.value = audio_exp.get('TIT2').text[0] if 'TIT2' in audio_exp else (
                ", ".join(map(lambda f: f.name, e.files)) if e.files else "Nombre desconocido"
            )
            artist_text.value = "Artista desconocido"
            album_text.value = "Álbum desconocido"
            length_text.value = audio_exp.info.length
            audio1.src = path
            audio1.visible = True
            page.update()
        # Abrir el archivo de audio y buscar la imagen de álbum
        try:
            tags = ID3(path)
            image_data = tags.getall("APIC")[0].data
            album_base64 = base64.b64encode(image_data).decode('utf-8')
            image_album.src_base64 = album_base64
            image_album.update()
        except Exception as Error:
            image_album.src = "/default_cover.png"
            image_album.update()
        main_function_animation()
    # hide all dialogs in overlay

    page.overlay.extend([pick_files_dialog, get_directory_dialog])

    title_text = ft.Text(font_family='Baloo', size=16, no_wrap=False, animate_offset=ft.animation.Animation(6000, ft.AnimationCurve.EASE_OUT),offset=ft.transform.Offset(0, 0),)
    artist_text = ft.Text(font_family='Baloo', size=12.5, no_wrap=False)
    album_text = ft.Text(font_family='Baloo', size=12.5, no_wrap=False)

    def main_function_animation():
        global flag_animation
        flag_animation = False
        def animate_fun():
            while flag_animation:
                time.sleep(7)
                title_text.offset = ft.transform.Offset(-(count_characters_title/100)-characteres_les/100, 0)
                title_text.update()
                time.sleep(7)
                title_text.offset = ft.transform.Offset(0, 0)
                title_text.update()
        count_characters_title = len(title_text.value)
        characteres_les = count_characters_title - 57
        # print(count_characters_title)
        if count_characters_title >= 57:
            flag_animation = True
            animate_fun()

    
    
    
    # # Carga la imagen del álbum
    # try:
    #     tags = ID3("C:\\Users\\DELL\\Downloads\\Astratify music\\Wiz Khalifa - Black and Yellow (feat. Juicy J, Snoop Dogg & T-Pain) - G-Mix [G-Mix].mp3")
    #     image_data = tags.getall("APIC")[0].data
    #     string_base64 = base64.b64encode(image_data.encode('utf-8'))
    #     # img = ImageTk.PhotoImage(data=image_data)
    # except:
    #     # img = None
    #     string_base64 = None

    # Configuraciones por defecto
    
    def update_time(e):
        audio1.seek(int(e.control.value)*1000)
        # time_duration_change.value = int(e.control.value)*1000
        page.update()
        
    time_duration_change = ft.Text(font_family='Baloo', size=16)
    time_duration_total = ft.Text(font_family='Baloo', size=16)
    slider_position = ft.Slider(on_change=update_time, expand=True, disabled=True, inactive_color="#638392", active_color="#ecebf2",thumb_color="#ecebf2")

    title_text.value = "---"
    artist_text.value = "---"
    album_text.value = "---"
    time_duration_change.value = "---"
    time_duration_total.value = "---"
    

    def change_duration(e):
        current_time = int(e.data)/1000
        slider_position.max = length_text.value
        slider_position.value = current_time
        time_duration_change.value = str(int(current_time // 60)) + ":" + str(int(current_time % 60)).zfill(2)
        time_duration_total.value = str(int(length_text.value // 60)) + ":" + str(int(length_text.value % 60)).zfill(2)
        page.update()

    def change_completed(e):
        if e.data == "completed":
            if music_list == "":
                btn_play.visible = True
                btn_pause.visible = False
                btn_resume.visible = False
                page.update()
            else:
                nonlocal song_index, last_songs, play_last
                if play_last:
                    try:
                        play_audio(music_list[last_songs[-1]]["ruta"], last_songs[-1])
                        return
                    except Exception as Error:
                        play_audio(music_list[song_index]["ruta"], song_index)    
                        return
                if random_play:
                    valid_index = False
                    while not valid_index:
                        index = random.randint(0, len(music_list)-1)
                        if index not in last_songs:
                            valid_index = True
                    song_index = index
                else:
                    song_index = (song_index + 1) % len(music_list)
                last_songs.append(song_index)
                if len(last_songs) > 5:
                    last_songs.pop(0)
                play_audio(music_list[song_index]["ruta"], song_index)
                save_config(round(slider_volumen.value, 2), info_volume_text.value, directory_path.value, audio1.src)
            
    
    aux_volume = []

    def load_audio(e):
        current_time = 0
        aux_volume.append(conf["volume_value"])
        time_duration_change.value = str(int(current_time // 60)) + ":" + str(int(current_time % 60)).zfill(2)
        time_duration_total.value = str(int(length_text.value // 60)) + ":" + str(int(length_text.value % 60)).zfill(2)

    def load_main():
        info_volume_text.value = conf["volume_text"]
        info_volume_container.visible = True
        page.update()
        update_volume_function(conf["volume_value"])

    audio1 = ft.Audio(
        autoplay=False,
        volume=conf["volume_value"],
        balance=0,
        on_loaded=load_audio,
        # on_duration_changed=lambda e: print("Duration changed:", e.data),
        on_position_changed=change_duration,
        on_state_changed=change_completed,
    )

    audio1.visible = False
    def update_volume(e):
        aux_volume.clear()
        audio1.volume = e.control.value
        # print(audio1.volume)
        aux_volume.append(round(e.control.value, 2))
        num_format = "{:.2f}".format(e.control.value)
        info_volume_text.value = str("{:.2f}".format(e.control.value)).replace('0.', '').replace('.', '')
        info_volume_container.visible = True
        page.update()
        save_config(round(slider_volumen.value, 2), info_volume_text.value, directory_path.value, audio1.src)
        update_volume_function(e.control.value)
        page.update()

    slider_volumen = ft.Slider(min=0, max=1, value=conf["volume_value"], on_change=update_volume, inactive_color="#638392", active_color="#ecebf2",thumb_color="#ecebf2")

    def volume_mute(_):
        audio1.volume = 0.0
        slider_volumen.value = aux_volume[0]
        slider_volumen.update()
        audio1.update()
        btn_icon_none_volumen.visible = True
        btn_icon_up_volumen.visible = False
        btn_icon_down_volumen.visible = False
        btn_icon_medium_volumen.visible = False
        page.update()
    def volume_unmute(_):
        audio1.volume = aux_volume[0]
        slider_volumen.value = aux_volume[0]
        slider_volumen.update()
        audio1.update()
        update_volume_function(aux_volume[0])

    def update_volume_function(value):
        if(round(value, 2)>=0.33 and round(value, 2) <=0.66):
            btn_icon_medium_volumen.visible = True
            btn_icon_down_volumen.visible = False
            btn_icon_up_volumen.visible = False
            btn_icon_none_volumen.visible = False
            page.update()
        if(round(value, 2)>=0.66):
            btn_icon_up_volumen.visible = True
            btn_icon_medium_volumen.visible = False
            btn_icon_down_volumen.visible = False
            btn_icon_none_volumen.visible = False
            page.update()
        if(round(value, 2)>0.00 and round(value, 2)<=0.33):
            btn_icon_down_volumen.visible = True
            btn_icon_none_volumen.visible = False
            btn_icon_medium_volumen.visible = False
            btn_icon_up_volumen.visible = False
            page.update()
        if(round(value, 2)==0.00):
            btn_icon_none_volumen.visible = True
            btn_icon_medium_volumen.visible = False
            btn_icon_up_volumen.visible = False
            btn_icon_down_volumen.visible = False
            page.update()

    def play_music(e):
        audio1.play()
        btn_play.visible = False
        btn_pause.visible = True
        page.update()

    def pause_music(e):
        audio1.pause()
        btn_play.visible = False
        btn_pause.visible = False
        btn_resume.visible = True
        page.update()

    def resume_music(e):
        audio1.resume()
        btn_play.visible = False
        btn_pause.visible = True
        btn_resume.visible = False
        page.update()

    global cont
    cont = 0
    def next_song(e):
        nonlocal song_index, last_songs
        if random_play:
            valid_index = False
            while not valid_index:
                index = random.randint(0, len(music_list)-1)
                if index not in last_songs:
                    valid_index = True
            song_index = index
        else:
            song_index = (song_index + 1) % len(music_list)
        last_songs.append(song_index)
        if len(last_songs) > 5:
            last_songs.pop(0)
        play_audio(music_list[song_index]["ruta"], song_index)

    def back_song(e):
        nonlocal song_index, last_songs
        if random_play:
            valid_index = False
            while not valid_index:
                index = random.randint(0, len(music_list)-1)
                if index not in last_songs:
                    valid_index = True
            song_index = index
        else:
            song_index = (song_index - 1) % len(music_list)
        last_songs.append(song_index)
        if len(last_songs) > 5:
            last_songs.pop(0)
        play_audio(music_list[song_index]["ruta"], song_index)

    btn_play = ft.Container(ft.IconButton(ft.icons.PLAY_ARROW_ROUNDED,on_click=play_music, icon_size=25, tooltip="Reproducir", icon_color="#ffffff"), visible=True, border_radius=9999, border=ft.border.all(3,"#ffffff"))
    btn_pause = ft.Container(ft.IconButton(ft.icons.PAUSE,on_click=pause_music, icon_size=25, tooltip="Pausar", icon_color="#ffffff"), visible=False, border_radius=9999, border=ft.border.all(3,"#ffffff"))
    btn_resume = ft.Container(ft.IconButton(ft.icons.PLAY_ARROW_ROUNDED,on_click=resume_music, icon_size=25, tooltip="Reanudar", icon_color="#ffffff"), visible=False, border_radius=9999, border=ft.border.all(3,"#ffffff"))
    
    btn_back = ft.Container(ft.IconButton(ft.icons.SKIP_PREVIOUS_ROUNDED,on_click=back_song, icon_size=25, tooltip="Anterior", icon_color="#ffffff"))
    btn_forward = ft.Container(ft.IconButton(ft.icons.SKIP_NEXT_ROUNDED,on_click=next_song, icon_size=25, tooltip="Siguiente", icon_color="#ffffff"))

    # btn_refresh_playlist = ft.IconButton(icon=ft.icons.REFRESH_ROUNDED, on_click=load_all)

    btn_icon_none_volumen = ft.Container(ft.IconButton(ft.icons.VOLUME_OFF_ROUNDED, on_click=volume_unmute, tooltip="Volumen", icon_color="#ffffff"), visible=False)
    btn_icon_down_volumen = ft.Container(ft.IconButton(ft.icons.VOLUME_MUTE_ROUNDED, on_click=volume_mute, tooltip="Volumen", icon_color="#ffffff"), visible=False)
    btn_icon_medium_volumen = ft.Container(ft.IconButton(ft.icons.VOLUME_DOWN_ROUNDED, on_click=volume_mute, tooltip="Volumen", icon_color="#ffffff"), visible=False)
    btn_icon_up_volumen = ft.Container(ft.IconButton(ft.icons.VOLUME_UP_ROUNDED, on_click=volume_mute, tooltip="Volumen", icon_color="#ffffff"), visible=False)
    info_volume_text = ft.Text(conf["volume_text"], font_family="Baloo", size=16)
    info_volume_container = ft.Container(info_volume_text, visible=False)

    text_info_path = ft.Text(font_family="Baloo")
    text_info_len_musicList = ft.Text(font_family="Baloo")
    text_info_duration_musicList = ft.Text(font_family="Baloo")

    image_album = ft.Image(
                        # src_base64=string_base64,
                        width=80,
                        fit=ft.ImageFit.COVER,
                        repeat=ft.ImageRepeat.NO_REPEAT,
                        border_radius=ft.border_radius.all(10),
                    )
    image_album.src = "/default_cover.png"
    list_view_info_container = ft.Container(
                    ft.Row([
                        ft.Container(ft.Text("#", font_family='Baloo'), alignment=ft.alignment.center, 
                                margin=ft.margin.symmetric(horizontal=10)),
                        ft.Container(
                            ft.Row([
                                ft.Container(
                                    ft.Text("Título", font_family='Baloo')
                                    , expand=True, 
                                    margin=ft.margin.symmetric(horizontal=10)
                                ),
                                ft.Container(ft.Text("Álbum", font_family='Baloo'), expand=True, margin=ft.margin.only(left=20)),
                                ft.Container(ft.Text("Duración", font_family='Baloo'), expand=True),
                                # ft.Container(
                                #         btn_refresh_playlist
                                #     ),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), expand=True, alignment=ft.alignment.center, 
                                margin=ft.margin.symmetric(vertical=2.5)
                        )
                    ]), border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.WHITE24)), padding=ft.padding.symmetric(vertical=10)
                )
     
    main_list_view = ft.Stack(
        [
            ft.Container(
                    ft.Column([
                        ft.Image(
                            src=f"/beatmash.png",
                            width=300,
                            height=300,
                            fit=ft.ImageFit.CONTAIN,
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER), alignment=ft.alignment.bottom_center,height=page.window_height / 1.5,opacity=0.1
            ),
            ft.Row([
                        ft.Container(
                            ft.Column(
                                [   
                                    ft.Container(ft.Text("SELECCIÓN", font_family='Baloo', color="#ffffff", size=16),padding=ft.padding.symmetric(horizontal=10)),
                                    ft.Container(
                                        ft.TextButton(
                                            "Elegir canción",
                                            icon=ft.icons.AUDIO_FILE_ROUNDED,
                                            on_click=lambda _: pick_files_dialog.pick_files(
                                                allow_multiple=False,
                                                allowed_extensions=["mp3",]
                                            ),
                                            style=ft.ButtonStyle(
                                                color={
                                                    ft.MaterialState.HOVERED: "#0aa2dd",
                                                    ft.MaterialState.DEFAULT: "#7e8095",
                                                },
                                            )
                                        ), padding=ft.padding.symmetric(vertical=5), alignment=ft.alignment.center_left
                                    ),
                                    ft.Container(
                                        ft.TextButton(
                                            "Agregar playlist",
                                            icon=ft.icons.LIBRARY_ADD_ROUNDED,
                                            on_click=lambda _: get_directory_dialog.get_directory_path(),
                                            disabled=page.web,
                                            style=ft.ButtonStyle(
                                                color={
                                                    ft.MaterialState.HOVERED: "#0aa2dd",
                                                    ft.MaterialState.DEFAULT: "#7e8095",
                                                },
                                            )
                                        ),padding=ft.padding.only(bottom=30), alignment=ft.alignment.center_left
                                    ),
                                    ft.Container(
                                        ft.Column([
                                            ft.Container(
                                                ft.Row([
                                                    ft.Icon(ft.icons.MUSIC_NOTE_ROUNDED),
                                                    ft.Container(ft.Text("Archivo actual", font_family='Baloo')),
                                                ]), padding=ft.padding.symmetric(horizontal=20, vertical=10), border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.WHITE24)),alignment=ft.alignment.center_left
                                            ),
                                            ft.Container(selected_files, padding=ft.padding.symmetric(horizontal=20, vertical=5)),
                                            ft.Container(
                                                ft.Row([
                                                    ft.Icon(ft.icons.LIBRARY_MUSIC_ROUNDED),
                                                    ft.Container(ft.Text("Playlist actual", font_family='Baloo')),
                                                ]), padding=ft.padding.symmetric(horizontal=20, vertical=10), border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.WHITE24)),alignment=ft.alignment.center_left
                                            ),
                                            ft.Container(btn_launch_dir_playlist, padding=ft.padding.symmetric(horizontal=20, vertical=5)),
                                        ]), border=ft.border.all(1, ft.colors.WHITE24),border_radius=10, padding=ft.padding.symmetric(horizontal=20, vertical=10)
                                    )
                                ],alignment=ft.MainAxisAlignment.START
                            ),alignment=ft.alignment.top_center, width=320, padding=ft.padding.symmetric(vertical=20, horizontal=20),height=page.window_height / 1.5, 
                            # border=ft.border.only(right=ft.border.BorderSide(1, ft.colors.WHITE24)), 
                            bgcolor="#353446",
                            gradient=ft.LinearGradient(
                                begin=ft.alignment.top_left,
                                end=ft.Alignment(0.8, 1),
                                colors=[
                                    "#1D1C2F",
                                    "#141131",
                                    "#131227",
                                ],
                                tile_mode=ft.GradientTileMode.MIRROR,
                                rotation=math.pi / 3,
                            ),
                            border_radius=ft.border_radius.only(bottom_right=40, top_right=40)
                        ),
                        ft.Container(ft.Column([
                            list_view_info_container,
                            ft.Container(music_list_view, padding=ft.padding.symmetric(vertical=10), expand=True, height=page.window_height / 1.5),
                            ft.Container(
                                ft.Row([
                                    ft.Container(text_info_path, expand=True),
                                    ft.Container(text_info_len_musicList, expand=True),
                                    ft.Container(text_info_duration_musicList, expand=True),
                                ]), border=ft.border.only(top=ft.border.BorderSide(1, ft.colors.WHITE24)), padding=ft.padding.symmetric(vertical=10, horizontal=20)
                            )
                        ]),border_radius=10, padding=ft.padding.symmetric(horizontal=20), expand=True, height=page.window_height / 1.5),                      
                    ], alignment=ft.MainAxisAlignment.START),
        ],
    )
    main_view_player = ft.Container(
                    ft.Column([
                        ft.Container(
                            ft.Row([
                                ft.Container(
                                    ft.Row([
                                        ft.Container(
                                            image_album, alignment=ft.alignment.center_left, 
                                            padding=ft.padding.only(right=5)
                                        ),
                                        ft.Column([
                                            ft.Container(title_text, clip_behavior=ft.ClipBehavior.ANTI_ALIAS_WITH_SAVE_LAYER),
                                                ft.Row([
                                                    ft.Container(artist_text),
                                                    ft.Container(ft.Text("•", font_family='Baloo', size=16)),
                                                    ft.Container(album_text),
                                                    # length_text
                                                ])
                                        ], wrap=True)
                                    ],alignment=ft.MainAxisAlignment.START), alignment=ft.alignment.center_left, expand=True, clip_behavior=ft.ClipBehavior.ANTI_ALIAS_WITH_SAVE_LAYER, margin=ft.margin.only(left=10,right=20)
                                ),
                                ft.Container(
                                    ft.Column([
                                            ft.Row([
                                                ft.Row([
                                                    random_play_btn_icon_unactive,
                                                    random_play_btn_icon_active,
                                                ]),
                                                btn_back,
                                                btn_play,
                                                btn_pause,
                                                btn_resume,
                                                btn_forward,
                                                ft.Row([
                                                    loop_btn_icon_unactive,
                                                    loop_play_btn_icon_active,
                                                ]),
                                                
                                            ], alignment=ft.MainAxisAlignment.CENTER),
                                            ft.Row([
                                                ft.Container(time_duration_change, alignment=ft.alignment.center),
                                                ft.Container(slider_position, alignment=ft.alignment.center, expand=True, ),
                                                ft.Container(time_duration_total, alignment=ft.alignment.center),
                                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                                    ], alignment=ft.MainAxisAlignment.CENTER), alignment=ft.alignment.center, expand=True, padding=ft.padding.only(top=10)
                                ),
                                ft.Container(
                                    ft.Row([
                                        btn_icon_none_volumen,
                                        btn_icon_medium_volumen,
                                        btn_icon_down_volumen,
                                        btn_icon_up_volumen,
                                        slider_volumen,
                                        info_volume_container
                                    ], alignment=ft.MainAxisAlignment.END), alignment=ft.alignment.center_right, expand=True, margin=ft.margin.only(right=20)
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), alignment=ft.alignment.center
                        )
                    ],alignment=ft.MainAxisAlignment.END), alignment=ft.alignment.bottom_center, padding=ft.padding.symmetric(horizontal=5, vertical=10), gradient=ft.LinearGradient(
                        begin=ft.alignment.top_left,
                        end=ft.Alignment(0.8, 1),
                        colors=[
                            "#131227",
                            "#131436",
                            "#1f2247"
                        ],
                        tile_mode=ft.GradientTileMode.MIRROR,
                        rotation=math.pi / 3,
                    ), border_radius=ft.border_radius.only(top_left=40, top_right=40)
                )

    config_astradown = ft.Container(
        ft.Container(
            ft.Column([
            ft.Container(ft.Text("Acerca de beatmash", font_family="Baloo 2", size=22, weight=ft.FontWeight.W_900), border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.WHITE24)), padding=ft.padding.only(bottom=15), alignment=ft.alignment.center_left, margin=ft.margin.only(bottom=10)),
            ft.Row([
                            ft.Container(ft.Text("Reproductor de música", font_family="Baloo 2", size=18)),
                            ft.Icon(ft.icons.HEADPHONES_ROUNDED)
                        ]),
                        ft.Container(ft.Text(f"Version {version} beta", font_family="Baloo 2", size=18, color=ft.colors.WHITE24),),
            ft.Container(
                ft.Row([
                    ft.Image(src='/beatmash.png', width=50),
                    ft.Text("beatmash", font_family='Baloo', size=24, weight=ft.FontWeight.W_700)
                ], expand=True), padding=ft.padding.symmetric(vertical=10)
            ),
            ft.Text("© 2023 Mashcode Beatmash. Todos los derechos reservados", font_family='Baloo', size=18)    
            ], alignment=ft.MainAxisAlignment.CENTER,expand=True,), border=ft.border.all(1, "#ffffff"), padding=ft.padding.symmetric(horizontal=20, vertical=30),border_radius=10,
        ),
        alignment=ft.alignment.center,
        # bgcolor="#1F1F31",
        padding=ft.padding.symmetric(horizontal=50, vertical=30),
        border_radius=50,
        margin=ft.margin.only(top=20),
    )
    component_help_1 = ft.Column([ft.Container(
                ft.Column([
                ft.Container(ft.Text("¿Problemas al intentar agregar una playlist?", font_family="Baloo 2", size=22, weight=ft.FontWeight.W_900, expand=True), border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.WHITE24)), padding=ft.padding.only(bottom=15), alignment=ft.alignment.center_left, margin=ft.margin.only(bottom=10)),
                ft.Column([
                    ft.Row([
                        ft.Container(ft.Text("Solución para agregar y reproducir una playlist", font_family="Baloo 2", size=18),alignment=ft.alignment.center_left, padding=ft.padding.symmetric(vertical=10)),
                        ft.Container(ft.Icon(ft.icons.LIBRARY_MUSIC_ROUNDED))
                    ]),
                    ft.Container(
                        ft.Row([
                            ft.Container(ft.Text("Cierre Beatmash y ábralo nuevamente con permisos de administrador", font_family="Baloo 2", size=18, color=ft.colors.WHITE38), padding=ft.padding.symmetric(vertical=10)),
                            ft.Container(ft.Icon(ft.icons.ADMIN_PANEL_SETTINGS_ROUNDED, color=ft.colors.WHITE38))
                        ],expand=True,),
                    )
                ]),
                ], alignment=ft.MainAxisAlignment.CENTER,expand=True,), border=ft.border.all(1, "#ffffff"), padding=ft.padding.symmetric(horizontal=20, vertical=30),border_radius=10,
            ),
        ])
    help_astradown = ft.Container(
        component_help_1,
        alignment=ft.alignment.center,
        # bgcolor="#1F1F31",
        padding=ft.padding.symmetric(horizontal=50, vertical=30),
        border_radius=50,
        margin=ft.margin.only(top=20),
    )
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                # text="Home",
                icon=ft.icons.HOME_ROUNDED,
                content=ft.Column([
                    ft.Container(
                        main_list_view,
                        alignment=ft.alignment.top_center,  padding=ft.padding.symmetric(vertical=5)
                    ),
                    ft.Container(
                        main_view_player,alignment=ft.alignment.bottom_center
                    )
                ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN,)
            ),
            ft.Tab(
                # text="Home",
                icon=ft.icons.SETTINGS_SHARP,
                content=ft.Column([
                    config_astradown
                ],expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                scroll=True,)

            ),
            ft.Tab(
                # text="Home",
                icon=ft.icons.HELP_OUTLINE_ROUNDED,
                content=ft.Column([
                    help_astradown
                ],expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                scroll=True,)

            ),
        ], 
    expand=1)
    def change_route( route):
        page.views.clear()  # CLEAR THE VIEWS
        # page.views.append()  # BUILD THE VIEW 1
        main_page = ft.View(
            route='/main',
            controls=[
                tabs
            ],
            padding=ft.padding.all(0),
            bgcolor="#131227",
        )
        page.views.append(main_page)
        page.update()

    # def page_resize(e):
    #     print("New page size:", page.window_width, page.window_height)
    # page.on_resize = page_resize

    load_main()
    load_all(None)
    page.overlay.append(audio1)
    page.on_route_change = change_route
    page.window_min_width = 812
    page.go(page.route)
    page.update()
    

ft.app(target=main, assets_dir="assets")



# ----------------------------------------------------------------
# pygame.mixer.music.set_volume(0.5)  # El valor va de 0 a 1
# # Reproduce la música
# pygame.mixer.music.play()

# # Mantén el programa funcionando mientras se reproduce la música
# while pygame.mixer.music.get_busy() == True:
#     continue