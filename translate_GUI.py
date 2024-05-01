from tkinter.ttk import *
from tkinter import *
import translate_UI
import customtkinter as ctk

from PIL import ImageTk, Image, ImageFont
from customtkinter import filedialog as fd
import tkinter.messagebox 
import translate_from_dir
import os
import easyocr
import tkinter.font as font
import cv2
import uuid
import sys
import requests

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

#----------------------------------------------------------------------

class MainWindow(ctk.CTk):

    #----------------
    
    def __init__(self, main):

        # Temp var
        # self.find_text_model_cn = easyocr.Reader(['ch_tra'], gpu=False)
        self.find_text_model_kr = easyocr.Reader(['ko'], gpu=False)
        self.find_text_model_jp = easyocr.Reader(['ja'], gpu=False)
        self.read_text_model = translate_from_dir.init_model(pretrained_model = resource_path('lib/manga_ocr/manga-ocr-base'),gpu = False)
        self.main_lang_detect = None
        # self.find_text_model_kr = ""
        # self.find_text_model_jp = ""
        # self.read_text_model =""

        self.main = main
        self.main.grid_rowconfigure(0, weight=1)
        self.font_path = resource_path(r"font\Roboto\Roboto-Regular.ttf")
        self.font_size = 30
        self.font = ImageFont.truetype(self.font_path,self.font_size)
        self.temp_pixel = PhotoImage(width=1, height=1)
        self.list_preview_image = []
        self.list_result_image = []
        self.preview_image_number = 0
        self.result_image_number = 0
        self.not_found_img = Image.open(resource_path(r"assets\not_found_img (1).jpg"))
        self.not_found_img.thumbnail((500, 500), resample = Image.Resampling.LANCZOS)
        self.not_found_img = ImageTk.PhotoImage(self.not_found_img)
        self.save_dir = "None"
        self.internet_connection = "Connected"

        #FRAME
        self.function_frame = ctk.CTkFrame(main, width = 140, height= (self.main.winfo_height()))
        self.function_frame.configure(fg_color = 'transparent')
        self.function_frame.grid_columnconfigure(0, weight=1)
        self.function_frame.grid(column= 0, row= 0, sticky=NSEW, padx=(0,5))
        self.function_frame.update()
        self.preview_frame = ctk.CTkFrame(main, height= (self.main.winfo_height()), width=((self.main.winfo_width()-740)/3))
        self.preview_frame.configure(fg_color = 'transparent')
        self.preview_frame.grid(column= 1, row= 0, sticky=NSEW, padx=(5,0))
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.update()
        self.translate_button_frame = ctk.CTkFrame(main, height= (self.main.winfo_height()), width=(200))
        self.translate_button_frame.configure(fg_color = 'transparent')
        self.translate_button_frame.grid(column= 2, row= 0, sticky=NSEW)
        self.translate_button_frame.grid_columnconfigure(2, weight=1)
        self.translate_button_frame.grid_rowconfigure(0, weight=1)
        self.translate_button_frame.grid_rowconfigure(1, weight=1)
        self.translate_button_frame.update()
        self.result_frame = ctk.CTkFrame(main, height= (self.main.winfo_height()), width=((self.main.winfo_width()-740)/3))
        self.result_frame.configure(fg_color = 'transparent')
        self.result_frame.grid(column= 3, row= 0, sticky=NSEW, padx=(0,5))
        self.result_frame.grid_columnconfigure(0, weight=1)
        self.result_frame.update()
        self.list_translated_text_frame = ctk.CTkFrame(main, height= (self.main.winfo_height()), width=400)
        self.list_translated_text_frame.configure(fg_color = 'transparent')
        self.list_translated_text_frame.grid(column= 4, row= 0, sticky=NSEW, padx=5)
        self.list_translated_text_frame.grid_columnconfigure(2, weight=1)
        self.list_translated_text_frame.grid_rowconfigure(4, weight=1)
        self.list_translated_text_frame.update()

        #Combobox select translate language
        self.support_translate_lang = {'Tiếng Việt': 'vi', 'Tiếng Anh':'en'}
        self.default_lang = StringVar(value = 'Tiếng Việt')
        self.select_default_lang_ccb = translate_UI.tl_ccb(self.function_frame)
        self.select_default_lang_ccb.configure(values=list(self.support_translate_lang.keys()), justify="center", variable=self.default_lang, command = self.on_update_translate_lang)
        self.select_default_lang_ccb.place(x = 10, y = 500)
        self.select_default_lang_lb = translate_UI.tl_lb(self.function_frame)
        self.select_default_lang_lb.configure(text = "Ngôn ngữ bạn muốn dịch", wraplength=100, font=('Arial',13,'bold'))
        self.select_default_lang_lb.place(x = 10, y = 460)
        self.default_lang_val = self.support_translate_lang[self.default_lang.get()]

        # Internet Connection checking
        self.internet_checking_canvas = translate_UI.tl_canvas(self.function_frame)
        self.internet_checking_canvas.configure(width=20)
        self.internet_checking_canvas.configure(height=20)
        self.internet_checking_canvas.place(x = 10, y= 920)
        self.internet_checking_circle_state = self.internet_checking_canvas.create_oval(0,0,10,10, fill='green')
        self.internet_connection_lb = translate_UI.tl_lb(self.function_frame)
        self.internet_connection_lb.configure(text= self.internet_connection)
        self.internet_connection_lb.configure(text_color='#FFFFFF')
        self.internet_connection_lb.configure(width=100)
        self.internet_connection_lb.configure(width=20)
        self.internet_connection_lb.configure(font=('Arial',13))
        self.internet_connection_lb.place(x=25, y=720)
        self.internet_checking_lb = translate_UI.tl_lb(self.function_frame)
        self.internet_checking_lb.configure(text= "Tình trạng kết nối Internet:")
        self.internet_checking_lb.configure(font=('Arial',13,'bold'))
        self.internet_checking_lb.place(x=10, y = 690)

        #BUTTON
        # Get file button
        self.get_file_btn = translate_UI.tl_btn(self.function_frame)
        self.get_file_btn.configure(text="Tải ảnh lên")
        self.get_file_btn.configure(command=self.get_file_path)
        self.get_file_btn.place( x = 10, y = 20)
        # Get folder button
        self.get_folder_btn = translate_UI.tl_btn(self.function_frame)
        self.get_folder_btn.configure(text="Tải thư mục lên")
        self.get_folder_btn.configure(command=self.get_folder_path)    
        self.get_folder_btn.place( x = 10, y = 70)
        # Save file location button
        self.save_dir_btn = translate_UI.tl_btn(self.function_frame)
        self.save_dir_btn.configure(text="Lưu")
        self.save_dir_btn.configure(command=self.get_save_folder_path)   
        self.save_dir_btn.configure(state=DISABLED)
        self.save_dir_btn.place( x = 10, y = 120)
        # Run OCR on selected
        self.run_all_btn = translate_UI.tl_btn(self.translate_button_frame)
        self.run_all_btn.configure( text='Dịch tất cả ảnh',command=self.run_model, height = 30, width=140, state=DISABLED)
        self.run_all_btn.grid(row = 0, column= 0, sticky= S, pady=(0, 20), padx=10)
        self.run_one_btn = translate_UI.tl_btn(self.translate_button_frame)
        self.run_one_btn.configure( text='Dịch ảnh hiện tại',command=self.run_model_1_image, height = 30, width = 140, state=DISABLED)
        self.run_one_btn.grid(row = 1, column= 0, sticky= N, pady=(20, 0), padx=10)
        # next image on preview
        self.next_preview_image_btn = translate_UI.tl_btn(self.preview_frame)
        self.next_preview_image_btn.configure(text='Ảnh sau >>',state=DISABLED,command=self.next_preview_image, border_width = 0, anchor='e')
        self.next_preview_image_btn.grid(row = 2, column = 1, sticky=E)
        # previous image on preview
        self.prev_preview_image_btn = translate_UI.tl_btn(self.preview_frame)
        self.prev_preview_image_btn.configure(text='<< Ảnh trước', state=DISABLED,command=self.prev_preview_image, border_width = 0, anchor='w')
        self.prev_preview_image_btn.grid(row = 2, column = 0, sticky=W)
        # next image on result
        self.next_result_image_btn = translate_UI.tl_btn(self.result_frame)
        self.next_result_image_btn.configure( text='Ảnh sau >>',state=DISABLED,command=self.next_result_image, border_width = 0,anchor = 'e')
        self.next_result_image_btn.grid(row=2, column=1, sticky=E)
        # previous image on result
        self.prev_result_image_btn = translate_UI.tl_btn(self.result_frame)
        self.prev_result_image_btn.configure(text='<< Ảnh trước',state=DISABLED,command=self.prev_result_image, border_width = 0, anchor='w')
        self.prev_result_image_btn.grid(row=2, column=0, sticky=W)
        # Pick font button
        self.pick_font_btn = translate_UI.tl_btn(self.function_frame)
        self.pick_font_btn.configure(text='Chọn font chữ', command=self.get_font_path)
        self.pick_font_btn.configure(text_color='#ffffff', border_color='#ffffff', font=('Arial',13,'bold'), width=100, height=20)
        self.pick_font_btn.place(x=10, y = 320)
        # Add translated_text_frame
        self.add_translated_frame_btn = translate_UI.tl_btn(self.list_translated_text_frame, text='Thêm bản dịch', command=self.add_translated_frame)
        self.add_translated_frame_btn.grid(row=2, column=1, sticky=E)
        self.add_translated_frame_btn.configure( width=100, height=20,state=DISABLED)
        # Add translated_text_frame
        self.update_translated_btn = translate_UI.tl_btn(self.list_translated_text_frame, text='Cập nhật bản dịch', command=self.return_update_translated_image)
        self.update_translated_btn.grid(row=2, column=0, sticky=W)
        self.update_translated_btn.configure( width=100, height=20,state=DISABLED)

        # LABEL
        self.save_dir_lb = translate_UI.tl_lb(self.function_frame)
        self.save_dir_lb.configure(text=self.save_dir)
        self.save_dir_lb.place(x = 10,y = 160)
        self.pick_font_lb = translate_UI.tl_lb(self.function_frame)
        self.pick_font_lb.configure(text = self.font_path, wraplength=100)
        self.pick_font_lb.place(x = 10,y = 350)
        self.original_img_lb = translate_UI.tl_lb(self.preview_frame, text = "Ảnh gốc")
        self.original_img_lb.configure(font=("Arial", 15, 'bold'), width=400, wraplength=400, height = 30)
        self.original_img_lb.grid(row=0, columnspan=2, sticky= SW)
        self.translated_img_lb = translate_UI.tl_lb(self.result_frame, text = "Ảnh sau khi dịch")
        self.translated_img_lb.configure(font=("Arial", 15, 'bold'), width = 400, wraplength=400, height=30)
        self.translated_img_lb.grid(columnspan=2, row=0)

        # ENTRY
        # name using widget Label
        self.font_size_lb = translate_UI.tl_lb(self.function_frame)
        self.font_size_lb.configure(text="Kích thước chữ", font=('Arial',13,'bold'))
        self.font_size_lb.place(x = 10, y=250)
        self.default_font_size = IntVar(value=30)
        self.font_size_en = translate_UI.tl_entry(self.function_frame)
        self.font_size_en.configure(textvariable = self.default_font_size, font=('Arial',10))
        self.font_size_en.place(x = 10, y=280)
        self.default_font_size.trace_add('write', self.on_update_global_font_size)

        # CANVAS
        self.preview_canvas = translate_UI.tl_canvas(self.preview_frame)
        self.preview_canvas.configure(width = self.preview_frame.winfo_width(),  height = (self.preview_frame.winfo_height()*0.9)-60, highlightthickness=1)
        self.preview_canvas.grid(row=1, columnspan=2, sticky=NSEW) 
        self.result_canvas = translate_UI.tl_canvas(self.result_frame)
        self.result_canvas.configure(width = self.result_frame.winfo_width(),  height = (self.result_frame.winfo_height()*0.9)-60, highlightthickness=1)
        self.result_canvas.grid(row=1, columnspan=2, sticky=NSEW)

        # FRAMES
        self.main_translated_frame_lb = translate_UI.tl_lb(self.list_translated_text_frame, text = "Danh sách bản dịch")
        self.main_translated_frame_lb.configure(font=("Arial", 15, 'bold'), width=400, wraplength=400, height = 30)
        self.main_translated_frame_lb.grid(row=0, columnspan=2, sticky=W)
        self.main_translated_frame = ctk.CTkFrame(self.list_translated_text_frame,width=400, height=(self.list_translated_text_frame.winfo_height()*0.7)-60)
        self.main_translated_frame.grid(sticky=NSEW, row=1, columnspan=2)

        # Create a frame for the canvas with non-zero row&column weights
        self.frame_canvas = ctk.CTkFrame(self.main_translated_frame)
        self.frame_canvas.grid(row=1, column=0, sticky=NSEW)
        self.frame_canvas.grid_rowconfigure(0, weight=1)
        self.frame_canvas.grid_columnconfigure(0, weight=1)
        self.frame_canvas.grid_propagate(False)

        # Add a canvas in that frame
        self.translated_canvas = translate_UI.tl_canvas(self.frame_canvas)
        self.translated_canvas.grid(row=0, column=0, sticky=NSEW)

        # Link a scrollbar to the canvas
        vsb = ctk.CTkScrollbar(self.frame_canvas, orientation="vertical", command=self.translated_canvas.yview)
        vsb.grid(row=0, column=1, sticky=NS)
        self.translated_canvas.configure(yscrollcommand=vsb.set)

        self.translated_frame = ctk.CTkFrame(self.translated_canvas,width=400, height=(self.list_translated_text_frame.winfo_height()*0.7)-60)
        self.translated_canvas.create_window((0, 0), window=self.translated_frame, anchor='nw')
        rows = 0
        self.list_translated_frame = []
        # for i in range(0, rows):
        #         self.list_translated_frame.append(Modify_translated_text(self.translated_frame,uuid.uuid4().hex, 0,0,0,0, 'Roboto', 30, "a", "b"))
        #         self.list_translated_frame[-1].grid(row=i,column=1, pady=10)
        #         self.list_translated_frame[-1].configure(highlightthickness=1,highlightbackground="blue")

        # Update buttons frames idle tasks to let tkinter calculate buttons sizes

        # Resize the canvas frame to show exactly 5-by-5 buttons and the scrollbar
        # first5columns_width = sum([buttons[0][j].winfo_width() for j in range(0, 5)])
        # first5rows_height = sum([buttons[i][0].cget('height') for i in range(0, 5)])
        # self.frame_canvas.configure(width=first5columns_width + vsb.winfo_width(),
        #                     height=first5rows_height)
        self.frame_canvas.configure(width=400, height=(self.list_translated_text_frame.winfo_height()*0.7)-60)

        # Set the canvas scrolling region
        self.translated_canvas.configure(scrollregion=self.translated_canvas.bbox("all"))
        
        # Start_images
        self.img_preview = Image.open(resource_path(r"assets\start_img.jpg"))
        self.img_preview.thumbnail((self.preview_canvas.winfo_width(),self.preview_canvas.winfo_height()), resample = Image.Resampling.LANCZOS)
        self.img_preview = ImageTk.PhotoImage(self.img_preview)
        self.img_result = Image.open(resource_path(r"assets\start_img (1).jpg"))
        self.img_result.thumbnail((self.result_canvas.winfo_width(),self.result_canvas.winfo_height()), resample = Image.Resampling.LANCZOS)
        self.img_result = ImageTk.PhotoImage(self.img_result)
        
        # set first image on canvas
        self.on_preview_canvas = self.preview_canvas.create_image(self.preview_canvas.winfo_width()/2, self.preview_canvas.winfo_height()/2, anchor="center", image=self.img_preview)
        self.on_result_canvas = self.result_canvas.create_image(self.result_canvas.winfo_width()/2, self.result_canvas.winfo_height()/2, anchor="center", image=self.img_result)


        self.original_img_lb.lift(self.preview_canvas)
        self.translated_img_lb.lift(self.result_canvas)
        self.is_connected()
    #---------------

    def is_connected(self):
        try:
            request = requests.get("https://translate.google.com/m",timeout=10)
            self.internet_connection = "Connected"
            self.internet_checking_canvas.itemconfigure(self.internet_checking_circle_state, fill='green')
        except OSError:
            self.internet_connection = "Disconnected"
            self.internet_checking_canvas.itemconfigure(self.internet_checking_circle_state, fill='red')
        finally:
            self.internet_connection_lb.configure(text=self.internet_connection)
            self.main.after(1000, self.is_connected) # do checking again one second later

        

    #---------------

    def on_update_translate_lang(self, var):
        self.default_lang_val = self.support_translate_lang[self.default_lang.get()]

    #---------------

    def on_update_global_font_size(self, var, index, mode):
        self.font_size = self.font_size_en.get()

    #----------------

    def get_font_path(self):
        
        file = fd.askopenfilename(filetypes=[('True Type Font', '*.ttf'),('Web Open Format Font', '*.woff'),('OPen Type Font', '*.otf'),('All files', '*.*')]) 
        # change image
        if file is not None and file!='':
            self.font_path = file
            self.pick_font_lb.configure(text = file)
   
    #----------------

    def get_file_path(self):
        filetypes = (('JPG files', '*.jpg'), 
                 ('JPEG files', '*.jpeg'),
                 ('PNG files', '*.png'),
                 ('All files', '*.*')) 
        file = fd.askopenfilename(filetypes=filetypes) 
        # change image
        if file is not None and file!='':
            self.clear_translated_frame(self.translated_frame)
            self.add_translated_frame_btn.configure(state=DISABLED)
            self.update_translated_btn.configure(state=DISABLED)
            self.run_all_btn.configure(state=NORMAL)
            self.run_one_btn.configure(state=NORMAL)
            self.preview_image_number = 0
            self.result_image_number = 0
            self.list_preview_image.clear()
            self.list_result_image.clear()
            self.img_preview = Image.open(file)
            self.list_preview_image.append(file)
            self.img_preview.thumbnail((self.preview_canvas.winfo_width(),self.preview_canvas.winfo_height()), resample = Image.Resampling.LANCZOS)
            self.img_preview = ImageTk.PhotoImage(self.img_preview)
            self.preview_canvas.itemconfigure(self.on_preview_canvas, image=self.img_preview)
            self.result_canvas.itemconfigure(self.on_result_canvas, image=self.not_found_img)
            self.prev_preview_image_btn.configure(state=DISABLED)
            self.next_preview_image_btn.configure(state=DISABLED)
            self.prev_result_image_btn.configure(state=DISABLED)
            self.next_result_image_btn.configure(state=DISABLED)
            self.save_dir_btn.configure(state=DISABLED)

    #----------------

    def get_folder_path(self):
        folder_path = fd.askdirectory() 
        # change image
        if folder_path is not None and folder_path != '':
            self.clear_translated_frame(self.translated_frame)
            self.add_translated_frame_btn.configure(state=DISABLED)
            self.update_translated_btn.configure(state=DISABLED)
            self.run_all_btn.configure(state=NORMAL)
            self.run_one_btn.configure(state=NORMAL)
            valid_images = [".jpg",".jpeg",".png"]
            self.list_preview_image.clear()
            self.list_result_image.clear()
            self.preview_image_number = 0
            self.result_image_number = 0
            self.save_dir_btn.configure(state=DISABLED)
            for f in os.listdir(folder_path):
                ext = os.path.splitext(f)[-1]
                if ext.lower() in valid_images:
                    self.list_preview_image.append(os.path.join(folder_path,f))
            if self.list_preview_image:
                self.img_preview = Image.open(self.list_preview_image[0])
                self.img_preview.thumbnail((self.preview_canvas.winfo_width(),self.preview_canvas.winfo_height()), resample = Image.Resampling.LANCZOS)
                self.img_preview = ImageTk.PhotoImage(self.img_preview) 
                self.preview_canvas.itemconfigure(self.on_preview_canvas, image=self.img_preview)
                self.result_canvas.itemconfigure(self.on_result_canvas, image=self.not_found_img)
            else:
                self.preview_canvas.itemconfigure(self.on_preview_canvas, image=self.not_found_img)
                self.result_canvas.itemconfigure(self.on_preview_canvas, image=self.not_found_img)
            self.prev_preview_image_btn.configure(state=DISABLED)
            if len(self.list_preview_image) <= 1:
                self.next_preview_image_btn.configure(state=DISABLED)
            else:
                self.next_preview_image_btn.configure(state=NORMAL)

    #----------------

    def next_preview_image(self):
        self.preview_image_number += 1 
        if self.preview_image_number <= (len(self.list_preview_image)-1):
            self.prev_preview_image_btn.configure(state=NORMAL)
            self.img_preview = Image.open(self.list_preview_image[self.preview_image_number])
            self.img_preview.thumbnail((self.preview_canvas.winfo_width(), self.preview_canvas.winfo_height()), resample = Image.Resampling.LANCZOS)
            self.img_preview = ImageTk.PhotoImage(self.img_preview) 
            self.preview_canvas.itemconfigure(self.on_preview_canvas, image=self.img_preview)
        if self.preview_image_number == (len(self.list_preview_image)-1):
            self.next_preview_image_btn.configure(state=DISABLED)

    #----------------

    def prev_preview_image(self):
        self.preview_image_number -= 1 
        if self.preview_image_number == 0:
            self.prev_preview_image_btn.configure(state=DISABLED)
        self.next_preview_image_btn.configure(state=NORMAL)
        self.img_preview = Image.open(self.list_preview_image[self.preview_image_number])
        self.img_preview.thumbnail((self.preview_canvas.winfo_width(), self.preview_canvas.winfo_height()), resample = Image.Resampling.LANCZOS)
        self.img_preview = ImageTk.PhotoImage(self.img_preview) 
        self.preview_canvas.itemconfigure(self.on_preview_canvas, image=self.img_preview)
        
    #----------------

    def run_model_1_image(self):
        if len(self.list_preview_image) == 0:
            tkinter.messagebox.showinfo("Image file not found",  "HÌnh như thư mục bạn đã chọn không có tệp định dạng ảnh")
        else:
            if self.internet_connection == "Disconnected":
                if tkinter.messagebox.askquestion("Không có kết nối mạng", "Phần mềm sử dụng Google Dịch nên cần có kết nối mạng, nhưng tôi không thể kết nối đến Google Dịch, bạn có muốn tiếp với kết quả dịch bị bỏ trống?", icon='warning') == "no":
                    return
            self.main_lang_detect = None
            self.run_one_btn.configure(state=DISABLED)
            self.run_all_btn.configure(state=DISABLED)
            top_lv = ctk.CTkToplevel(self.main)
            top_lv.geometry('500x300')
            top_lv.title("Vui lòng chờ")
            top_lv.wm_iconbitmap()
            top_lv.iconphoto(True, ImageTk.PhotoImage(file=resource_path(r'assets\logo.png')))
            translate_progress_lb = translate_UI.tl_lb(top_lv, text="Vui lòng chờ trong lúc tôi dịch nhé")
            translate_progress_lb.configure(width=500, wraplength=500, anchor='center', font = ('Arial',15, 'bold'))
            translate_progress_lb.pack()
            current_progress = translate_UI.tl_lb(top_lv, text="Chờ một xíu thôi :>")
            current_progress.configure(width=500, wraplength=500, anchor='center', font = ('Arial',13))
            current_progress.pack()
            my_image = ctk.CTkImage(light_image=Image.open(resource_path(r"assets\translate_1_image.jpg")),
                                  dark_image=Image.open(resource_path(r"assets\translate_1_image.jpg")),
                                  size=(200, 200))

            image_label = ctk.CTkLabel(top_lv, width=500, height=200, image=my_image, text="")  # display image with a CTkLabel
            image_label.pack()

            top_lv.after(10, top_lv.lift)
            top_lv.update()
            k = 0

            if(self.font_size_en.get() != ''):
                self.font_size = int(self.font_size_en.get())
            else:
                self.font_size = 30
            self.font = ImageFont.truetype(self.font_path, self.font_size)
            self.clear_translated_frame(self.translated_frame)
            if len(self.list_result_image) == 0:
                for img in self.list_preview_image:
                    self.list_result_image.append([cv2.imread(img,0), None])
            for i in range(0,len(self.list_preview_image)):
                if i == self.preview_image_number:
                    self.list_result_image[self.preview_image_number] = translate_from_dir.get_translate_data(self.read_text_model,self.find_text_model_kr, cv2.imread(self.list_preview_image[self.preview_image_number],0), self.font, translate_from_dir.get_bboxes(cv2.imread(self.list_preview_image[self.preview_image_number],0),self.find_text_model_jp,0.01),self.internet_connection, self.default_lang_val)
                    break
                # self.list_result_image.append(translate_from_dir.get_translate_data(self.read_text_model, cv2.imread(img,0),""))
                k += 1
            top_lv.destroy()
            self.run_one_btn.configure(state=NORMAL)
            self.run_all_btn.configure(state=NORMAL)
            self.save_dir_btn.configure(state=NORMAL)
            
            self.result_image_number = self.preview_image_number
            self.img_result = Image.fromarray(self.list_result_image[self.preview_image_number][0])
            self.img_result.thumbnail((self.result_canvas.winfo_width(),self.result_canvas.winfo_height()), resample = Image.Resampling.LANCZOS)
            self.img_result = ImageTk.PhotoImage(self.img_result) 
            self.result_canvas.itemconfigure(self.on_result_canvas, image=self.img_result)
            if(self.list_result_image[self.result_image_number][1] is not None):
                for data in self.list_result_image[self.result_image_number][1]:
                    temp = Modify_translated_text(self.translated_frame,uuid.uuid4().hex, data[0],data[1],data[2],data[3], self.font_path, self.font_size, data[4],data[5], self.default_lang_val)
                    temp.pack(pady=10)
                    self.list_translated_frame.append(temp)
                    self.translated_frame.update_idletasks()
                    if(len(self.list_translated_frame) > 0 and sum([self.list_translated_frame[i].cget('height') for i in range(0, len(self.list_translated_frame))]) < 680):
                        frame_canvas_height = sum([self.list_translated_frame[i].cget('height') for i in range(0, len(self.list_translated_frame))])
                    else:
                        frame_canvas_height = (self.list_translated_text_frame.winfo_height()*0.7)-60
                    self.frame_canvas.configure(height=frame_canvas_height)
                    self.translated_canvas.configure(scrollregion=self.translated_canvas.bbox("all"))
            self.add_translated_frame_btn.configure(state=NORMAL)
            self.update_translated_btn.configure(state=NORMAL)
        if len(self.list_result_image) > 1:
            flag = True
            if self.result_image_number == 0: 
                self.prev_result_image_btn.configure(state = DISABLED)
                self.next_result_image_btn.configure(state = NORMAL)
                flag = False
            if self.result_image_number == len(self.list_result_image) - 1:
                self.next_result_image_btn.configure(state = DISABLED)
                self.prev_result_image_btn.configure(state = NORMAL)
                flag = False
            if flag:
                self.prev_result_image_btn.configure(state = NORMAL)
                self.next_result_image_btn.configure(state = NORMAL)
        else:
            self.prev_result_image_btn.configure(state = DISABLED)
            self.next_result_image_btn.configure(state = DISABLED)

    #----------------

    def run_model(self):
        if len(self.list_preview_image) == 0:
            tkinter.messagebox.showinfo("Image file not found",  "HÌnh như thư mục bạn đã chọn không có tệp định dạng ảnh")
        else:
            if self.internet_connection == "Disconnected":
                if tkinter.messagebox.askquestion("Không có kết nối mạng", "Phần mềm sử dụng Google Dịch nên cần có kết nối mạng, nhưng tôi không thể kết nối đến Google Dịch, bạn có muốn tiếp với kết quả dịch bị bỏ trống?", icon='warning') == "no":
                    return
            self.main_lang_detect = None
            self.run_one_btn.configure(state=DISABLED)
            self.run_all_btn.configure(state=DISABLED)
            top_lv = ctk.CTkToplevel(self.main)
            top_lv.geometry('500x100')
            top_lv.title("Vui lòng chờ")
            top_lv.wm_iconbitmap()
            top_lv.iconphoto(True, ImageTk.PhotoImage(file=resource_path(r'assets\logo.png')))
            translate_progress_lb = translate_UI.tl_lb(top_lv, text="Tiến độ dịch truyện của chương trình")
            translate_progress_lb.configure(width=500, wraplength=500, anchor='center', font = ('Arial',15, 'bold'))
            translate_progress_lb.pack()
            current_progress = translate_UI.tl_lb(top_lv, text="0/"+str(len(self.list_preview_image)))
            current_progress.configure(width=500, wraplength=500, anchor='center', font = ('Arial',13))
            current_progress.pack()
            progressbar = ctk.CTkProgressBar(top_lv, width=500, height=20, progress_color='#74E291', border_color='#000000')
            progressbar.pack()
            progressbar.start()
            top_lv.after(10, top_lv.lift)
            top_lv.update()
            k = 0

            if(self.font_size_en.get() != ''):
                self.font_size = int(self.font_size_en.get())
            else:
                self.font_size = 30
            self.font = ImageFont.truetype(self.font_path, self.font_size)
            self.clear_translated_frame(self.translated_frame)
            self.list_result_image.clear()

            for img in self.list_preview_image:
                progressbar.set(k/len(self.list_preview_image))
                current_progress.configure(text=str(k)+"/"+str(len(self.list_preview_image)))
                top_lv.update_idletasks()
                self.list_result_image.append(translate_from_dir.get_translate_data(self.read_text_model,self.find_text_model_kr, cv2.imread(img,0), self.font, translate_from_dir.get_bboxes(cv2.imread(img,0),self.find_text_model_jp,0.01),self.internet_connection, self.default_lang_val))
                # self.list_result_image.append(translate_from_dir.get_translate_data(self.read_text_model, cv2.imread(img,0),""))
                
                k += 1
            progressbar.stop()
            top_lv.destroy()
            self.run_one_btn.configure(state=NORMAL)
            self.run_all_btn.configure(state=NORMAL)
            self.save_dir_btn.configure(state=NORMAL)
            
            self.result_image_number = 0
            self.img_result = Image.fromarray(self.list_result_image[self.result_image_number][0])
            self.img_result.thumbnail((self.result_canvas.winfo_width(), self.result_canvas.winfo_height()), resample = Image.Resampling.LANCZOS)
            self.img_result = ImageTk.PhotoImage(self.img_result) 
            self.result_canvas.itemconfigure(self.on_result_canvas, image=self.img_result)
            self.prev_result_image_btn.configure(state=DISABLED)
            for data in self.list_result_image[self.result_image_number][1]:
                temp = Modify_translated_text(self.translated_frame,uuid.uuid4().hex, data[0],data[1],data[2],data[3], self.font_path, self.font_size, data[4],data[5], self.default_lang_val)
                temp.pack(pady=10)
                self.list_translated_frame.append(temp)
                self.translated_frame.update_idletasks()
                if(len(self.list_translated_frame) > 0 and sum([self.list_translated_frame[i].cget('height') for i in range(0, len(self.list_translated_frame))]) < 680):
                    frame_canvas_height = sum([self.list_translated_frame[i].cget('height') for i in range(0, len(self.list_translated_frame))])
                else:
                    frame_canvas_height = (self.list_translated_text_frame.winfo_height()*0.7)-60
                self.frame_canvas.configure(height=frame_canvas_height)
                self.translated_canvas.configure(scrollregion=self.translated_canvas.bbox("all"))
            self.add_translated_frame_btn.configure(state=NORMAL)
            self.update_translated_btn.configure(state=NORMAL)
        if len(self.list_preview_image) <= 1:
            self.next_result_image_btn.configure(state=DISABLED)
        else:
            self.next_result_image_btn.configure(state=NORMAL)
        

    #----------------

    def next_result_image(self):
        self.result_image_number += 1 
        if self.result_image_number <= (len(self.list_result_image)-1):
            self.prev_result_image_btn.configure(state=NORMAL)
            self.img_result = Image.fromarray(self.list_result_image[self.result_image_number][0])
            self.img_result.thumbnail((self.result_canvas.winfo_width(), self.result_canvas.winfo_height()), resample = Image.Resampling.LANCZOS)
            self.img_result = ImageTk.PhotoImage(self.img_result) 
            self.result_canvas.itemconfigure(self.on_result_canvas, image=self.img_result)
        if self.result_image_number == (len(self.list_result_image)-1):
            self.next_result_image_btn.configure(state=DISABLED)
        self.clear_translated_frame(self.translated_frame)
        if not (self.list_result_image[self.result_image_number][1] is None):
            for data in self.list_result_image[self.result_image_number][1]:
                    if len(data)>6:
                        temp = Modify_translated_text(self.translated_frame,uuid.uuid4().hex, data[0],data[1],data[2],data[3], data[4], data[5], data[6],data[7], self.default_lang_val)
                    else:
                        temp = Modify_translated_text(self.translated_frame,uuid.uuid4().hex, data[0],data[1],data[2],data[3],self.font_path, self.font_size, data[4], data[5], self.default_lang_val)
                    temp.pack(pady=10)
                    
                    self.list_translated_frame.append(temp)
                    self.translated_frame.update_idletasks()
                    if(len(self.list_translated_frame) > 0 and sum([self.list_translated_frame[i].cget('height') for i in range(0, len(self.list_translated_frame))]) < 680):
                        frame_canvas_height = sum([self.list_translated_frame[i].cget('height') for i in range(0, len(self.list_translated_frame))])
                    else:
                        frame_canvas_height = (self.list_translated_text_frame.winfo_height()*0.7)-60
                    self.frame_canvas.configure(height=frame_canvas_height)
                    self.translated_canvas.configure(scrollregion=self.translated_canvas.bbox("all"))

    #----------------

    def prev_result_image(self):
        self.result_image_number -= 1 
        if self.result_image_number == 0:
            self.prev_result_image_btn.configure(state=DISABLED)
        self.next_result_image_btn.configure(state=NORMAL)
        self.img_result = Image.fromarray(self.list_result_image[self.result_image_number][0])
        self.img_result.thumbnail((self.result_canvas.winfo_width(), self.result_canvas.winfo_height()), resample = Image.Resampling.LANCZOS)
        self.img_result = ImageTk.PhotoImage(self.img_result) 
        self.result_canvas.itemconfigure(self.on_result_canvas, image=self.img_result)
        self.clear_translated_frame(self.translated_frame)
        if(self.list_result_image[self.result_image_number][1] is not None):
            for data in self.list_result_image[self.result_image_number][1]:
                    if len(data)>6:
                        temp = Modify_translated_text(self.translated_frame,uuid.uuid4().hex, data[0],data[1],data[2],data[3], data[4], data[5], data[6],data[7], self.default_lang_val)
                    else:
                        temp = Modify_translated_text(self.translated_frame,uuid.uuid4().hex, data[0],data[1],data[2],data[3],self.font_path, self.font_size, data[4], data[5], self.default_lang_val)
                    temp.pack(pady=10)
                    
                    self.list_translated_frame.append(temp)
                    self.translated_frame.update_idletasks()
                    if(len(self.list_translated_frame) > 0 and sum([self.list_translated_frame[i].cget('height') for i in range(0, len(self.list_translated_frame))]) < 680):
                        frame_canvas_height = sum([self.list_translated_frame[i].cget('height') for i in range(0, len(self.list_translated_frame))])
                    else:
                        frame_canvas_height = (self.list_translated_text_frame.winfo_height()*0.7)-60
                    self.frame_canvas.configure(height=frame_canvas_height)
                    self.translated_canvas.configure(scrollregion=self.translated_canvas.bbox("all"))

    #----------------

    def get_save_folder_path(self):
        if len(self.list_result_image) != 0:
            save_folder_path = fd.askdirectory() 
            # change image
            if save_folder_path is not None and save_folder_path != '':
                self.save_dir = save_folder_path
                self.save_dir_lb.configure(text="Kết quả đã được lưu tại " +save_folder_path)  
                for file in self.list_result_image:
                    cv2.imwrite(save_folder_path+"/" + str(uuid.uuid4())+".jpg", file[0])
        else:
            tkinter.messagebox.showinfo("Không tìm thấy ảnh đã dịch",  "HÌnh như đã có lỗi trong quá trình dịch, phiền bạn kiểm tra lại kết nối Internet và tiến hành chạy lại chương trình")
            
    #----------------

    def add_translated_frame(self):
        temp = Modify_translated_text(self.translated_frame,uuid.uuid4().hex, 0,0,0,0, self.font_path, self.font_size, "a", "b", self.default_lang_val)
        temp.pack(pady=5, padx= 5, fill=BOTH, expand=True)
        self.list_translated_frame.append(temp)
        self.translated_frame.update_idletasks()
        # if(len(self.list_translated_frame) > 0 and sum([self.list_translated_frame[i].cget('height') for i in range(0, len(self.list_translated_frame))]) < (self.list_translated_text_frame.winfo_height()*0.7)-60):
        #     frame_canvas_height = sum([self.list_translated_frame[i].cget('height') for i in range(0, len(self.list_translated_frame))])
        # else:
        #     frame_canvas_height = (self.list_translated_text_frame.winfo_height()*0.7)-60
        # self.frame_canvas.configure(height=frame_canvas_height)
        self.translated_canvas.configure(scrollregion=self.translated_canvas.bbox("all"))

    #---------------

    def clear_translated_frame(self, wid):
        self.list_translated_frame.clear()
        _list = wid.winfo_children()
        for item in _list :
                _list.extend(item.winfo_children())
        for item in _list:
            item.destroy()

    #----------------

    def return_update_translated_image(self):
        print("_________________________________")
        self.update_translated_text(cv2.cvtColor(cv2.imread(self.list_preview_image[self.result_image_number], cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB))
        # self.img_result = Image.fromarray(self.list_result_image[0])
        self.img_result = Image.fromarray(self.list_result_image[self.result_image_number][0])
        self.img_result.thumbnail((self.result_canvas.winfo_width(), self.result_canvas.winfo_height()), resample = Image.Resampling.LANCZOS)
        self.img_result = ImageTk.PhotoImage(self.img_result) 
        self.result_canvas.itemconfigure(self.on_result_canvas, image=self.img_result)

    #----------------

    def update_translated_text(self,img, child = None, data=None):
        if child == None:
            children = self.translated_frame.winfo_children()
        else:
            children = child.winfo_children()
        list_data = data or []
        for item in children:
            if (type(item).__name__ == 'Modify_translated_text'):
                # temp_var = Modify_translated_text(self.translated_frame,item.id, item.x_min,item.y_min,item.x_max,item.y_max, item.font_type, item.font_size, item.original_text, item.translated_text)
                img = translate_from_dir.draw_text(img,ImageFont.truetype(item.font_type,int(item.font_size)), item.translated_text, int(item.x_min),int(item.y_min),int(item.x_max),int(item.y_max))
                list_data.append([int(item.x_min),int(item.y_min),int(item.x_max),int(item.y_max),item.font_type,int(item.font_size),item.original_text, item.translated_text])
            self.update_translated_text(img,item, list_data)    
        self.list_result_image[self.result_image_number][0] = img
        img = self.list_preview_image[self.result_image_number]
        self.list_result_image[self.result_image_number][1] = list_data

    #----------------

class Modify_translated_text(ctk.CTkFrame):
    def __init__(self,parent,id, x_min, y_min, x_max, y_max, font_type, font_size, original_text, translated_text, default_lang = 'en'):
        super().__init__(master=parent)
        self.id = id
        self.original_text = original_text
        self.translated_text =translated_text
        self.font_size = font_size
        self.font_type = font_type
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.default_lang = default_lang
        self.configure(fg_color=self.master['bg'], width=self.master['width']-120, height=490, border_width=10, border_color='#FFFFFF')
        self.pack(expand=True, fill=BOTH)
        self.grid_propagate(0)
        #widgets

        self.columnconfigure(0, weight=1)

        self.temp_font_size = IntVar(value = self.font_size)
        self.temp_x_min = IntVar(value = self.x_min)
        self.temp_y_min = IntVar(value = self.y_min)
        self.temp_x_max = IntVar(value = self.x_max)
        self.temp_y_max = IntVar(value = self.y_max)
        self.temp_ori_text = StringVar(value= self.original_text)
        self.temp_trans_text = StringVar(value = self.translated_text)


        # create all of the main containers
        self.top_frame = ctk.CTkFrame(self, width=self.cget('width'))
        self.center = ctk.CTkFrame(self, width=self.cget('width'))
        self.bottom_frame = ctk.CTkFrame(self, width=self.cget('width'))

        # for frame in [self.top_frame, self.center, self.bottom_frame]:
        #     # sticky='nswe' acts like fill='both'
        #     frame.grid(sticky='nswe')
        #     frame.grid_propagate(0)

        # layout all of the main containers

        self.top_frame.grid(row=0, sticky=NSEW,padx=2, pady=(2,0))
        self.center.grid(row=1, sticky=NSEW,padx=2)
        self.bottom_frame.grid(row=2, sticky=NSEW,padx=2, pady=(0,2))

        # create the widgets for the top frame
        # model_label = Label(top_frame, text='Model Dimensions')
        self.id_lb = translate_UI.tl_lb(self.top_frame, text="ID: "+self.id)
        self.id_lb.configure(wraplength=0)
        self.x_min_lb = translate_UI.tl_lb(self.top_frame, text='X_min:')
        self.x_min_lb.configure(width=self.cget('width')*0.2-50)
        self.y_min_lb = translate_UI.tl_lb(self.top_frame, text='Y_min:')
        self.y_min_lb.configure(width=self.cget('width')*0.2-50)
        self.x_max_lb = translate_UI.tl_lb(self.top_frame, text='X_max:')
        self.x_max_lb.configure(width=self.cget('width')*0.2-50)
        self.y_max_lb = translate_UI.tl_lb(self.top_frame, text='Y_max:')
        self.y_max_lb.configure(width=self.cget('width')*0.2-50)
        self.x_min_en = translate_UI.tl_entry(self.top_frame,textvariable= self.temp_x_min)
        self.x_min_en.configure(width=self.cget('width')*0.3)
        self.y_min_en = translate_UI.tl_entry(self.top_frame,textvariable= self.temp_y_min)
        self.y_min_en.configure(width=self.cget('width')*0.3)
        self.x_max_en = translate_UI.tl_entry(self.top_frame,textvariable= self.temp_x_max)
        self.x_max_en.configure(width=self.cget('width')*0.3)
        self.y_max_en = translate_UI.tl_entry(self.top_frame,textvariable= self.temp_y_max)
        self.y_max_en.configure(width=self.cget('width')*0.3)

        # layout the widgets in the top frame
        # model_label.grid(row=0, columnspan=4)
        self.id_lb.grid(row = 0, columnspan=4, sticky='w', padx = (5, 0))
        self.x_min_lb.grid(row=1, column=0, sticky='w', padx = (5, 0))
        self.y_min_lb.grid(row=1, column=2, sticky='w', padx = (5, 0))
        self.x_max_lb.grid(row=2, column=0, sticky='w', padx = (5, 0))
        self.y_max_lb.grid(row=2, column=2, sticky='w', padx = (5, 0))
        self.x_min_en.grid(row=1, column=1, padx=(10,0))
        self.y_min_en.grid(row=1, column=3, padx=(10,0))
        self.x_max_en.grid(row=2, column=1, padx=(10,0))
        self.y_max_en.grid(row=2, column=3, padx=(10,0))

        # create the center widgets
        self.original_txt_lb = translate_UI.tl_lb(self.center, text='Văn bản gốc:', justify=RIGHT)
        self.original_txt_lb.configure(font = ('Arial',15,'bold'))
        self.original_txt_en = ctk.CTkTextbox(self.center,height = 100, width=self.cget('width')*0.9)
        self.original_txt_en.insert(END, self.original_text)
        self.original_txt_en.bind('<KeyRelease>', self.on_update_original_text)
        self.original_txt_lb.grid(row=3, sticky='w',padx = 5, column = 0)
        self.original_txt_en.grid(row=4, sticky='w', padx = 5, columnspan=2)
        self.translated_txt_lb = translate_UI.tl_lb(self.center, text='Văn bản sau khi dịch:')
        self.translated_txt_lb.configure(wraplength = 200, width=200, font = ('Arial',15,'bold'))
        self.translated_txt_en = ctk.CTkTextbox(self.center, height = 100, width=self.cget('width')*0.9)
        self.translated_txt_en.insert(END, self.translated_text)
        self.translated_txt_en.bind('<KeyRelease>', self.on_update_translated_text)
        self.translated_txt_lb.grid(row=5,sticky='w',padx = 5, column=0)
        self.translated_txt_en.grid(row=6, sticky='w', padx = 5,columnspan=2)
        self.translate_btn = translate_UI.tl_btn(self.center, text="Dịch lại", command=self.translate_from_original_text)
        self.translate_btn.configure(height = 20, width=75, font=('Arial',13), border_color ='#FFFFFF', text_color = '#FFFFFF')
        self.translate_btn.grid(row=5, column=1, sticky='e', padx= (0,5))

        self.font_size_lb = translate_UI.tl_lb(self.bottom_frame, text='Kích cỡ font:')
        self.font_size_lb.configure(width =self.bottom_frame.winfo_width()*0.2-50, padx = 5)
        self.font_size_en = translate_UI.tl_entry(self.bottom_frame,textvariable= self.temp_font_size)
        self.font_size_en.configure(width=self.bottom_frame.winfo_width()*0.2)
        self.temp_font_size.trace_add('write', self.on_update_font_size)
        self.font_size_lb.grid(row=7, column=0)
        self.font_size_en.grid(row=7, column=1)
        self.font_type_lb = translate_UI.tl_lb(self.bottom_frame, text='Loại font:')
        self.font_type_lb.configure(width = self.bottom_frame.winfo_width()*0.2-50, padx = 5)
        self.font_type_lb.grid(row=7, column=2)
        self.font_type_btn = translate_UI.tl_btn(self.bottom_frame, text='Chọn font chữ', command=self.get_font_path)
        self.font_type_btn.configure(height = 20, width=self.bottom_frame.winfo_width()*0.3-10, font=('Arial',13), border_color ='#FFFFFF', text_color = '#FFFFFF')
        self.font_type_btn.grid(row=7, column=3, padx=5)
        self.font_type_path_lb = translate_UI.tl_lb(self.bottom_frame, text=self.font_type)
        self.font_type_path_lb.configure(wraplength=180)
        self.font_type_path_lb.grid(row=8, column=2, columnspan=2)

        self.del_translated_text = translate_UI.tl_btn(self.bottom_frame, text='Xóa bản dịch này', command=self.delete_translated_box)
        self.del_translated_text.grid(row=8, column=0, pady=10,padx=(5,0), columnspan=2, sticky='w')
        self.del_translated_text.configure(height = 20, width=40, font=('Arial',11, 'bold'), text_color = '#FF204E',border_width = 0)
        
        
        self.temp_x_min.trace_add('write', self.on_update_x_min)
        self.temp_y_min.trace_add('write', self.on_update_y_min)
        self.temp_x_max.trace_add('write', self.on_update_x_max)
        self.temp_y_max.trace_add('write', self.on_update_y_max)

    def get_font_path(self):
        file = fd.askopenfilename(filetypes=[('True Type Font', '*.ttf'),('Web Open Format Font', '*.woff'),('Open Type Font', '*.otf'),('All files', '*.*')]) 
        if file is not None and file!='':
            self.font_type = file
            self.font_type_path_lb.configure(text = file)

    def delete_translated_box(self):
        if tkinter.messagebox.askquestion("Xóa bản dịch?", "Bạn có chắc chắn rằng muốn xóa bản dịch này?") == 'yes':
            self.destroy()

    def translate_from_original_text(self):
        try:
            if(self.original_text == ""):
                tkinter.messagebox.showinfo("Văn bản cần dịch trống",  "Không tìm thấy văn bản cần dịch")
            else:
                self.translated_text = translate_from_dir.translate_text(self.original_text,self.default_lang)
                self.translated_txt_en.delete('1.0', END)
                self.translated_txt_en.insert(END, self.translated_text)
        except Exception as e:
            tkinter.messagebox.showinfo("Không thể dịch được văn bản",  "HÌnh như đã có lỗi trong quá trình dịch, phiền bạn kiểm tra lại kết nối Internet và tiến hành chạy lại chương trình")
    
    def on_update_font_size(self, var, index, mode):
        self.font_size = self.font_size_en.get()
    def on_update_x_min(self, var, index, mode):
        self.x_min = self.x_min_en.get()
    def on_update_y_min(self, var, index, mode):
        self.y_min = self.y_min_en.get()
    def on_update_x_max(self, var, index, mode):
        self.x_max = self.x_max_en.get()
    def on_update_y_max(self, var, index, mode):
        self.y_max = self.y_max_en.get()
    def on_update_original_text(self, event):
        self.original_text = self.original_txt_en.get("1.0", END)
    def on_update_translated_text(self, event):
        self.translated_text = self.translated_txt_en.get("1.0", END)

class Loading_screen(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        x, y = centerWindow(519, 400, self)
        # x, y = centerWindow(519, 300, self)
        self.geometry(f"519x400+{x}+{y}")
        self.image = ctk.CTkImage(light_image=Image.open(resource_path(r'assets\loading_screen.png')),
                                  dark_image=Image.open(resource_path(r'assets\loading_screen.png')),
                                  size=(519, 300))
        self.image_label = ctk.CTkLabel(self, image=self.image, text="")  # display image with a CTkLabel
        self.image_label.pack()
        self.label = ctk.CTkLabel(self, text="Cảm ơn bạn vì đã sử dụng phần mềm. Vui lòng chờ trong lúc chương trình khởi chạy nhé.", wraplength= 400, width=519, height=100, font=("Arial", 17))
        self.label.pack(padx=20, pady=20)
        self.overrideredirect(True)
        self.update()

#----------------------------------------------------------------------
def centerWindow(width, height, root):  # Return 4 values needed to center Window
    screen_width = root.winfo_screenwidth()  # Width of the screen
    screen_height = root.winfo_screenheight() # Height of the screen     
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    return int(x), int(y)
if __name__ == '__main__':
    ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
    ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
    r = ctk.CTk()
    
    r.title('Phần mềm dịch truyện được viết bằng Python')
    width = r.winfo_screenwidth()
    height = r.winfo_screenheight()
    geometry = str(width) + "x" + str(height) + "+0+0"
    r.geometry(geometry)
    r.update()
    r.wm_iconbitmap()
    r.iconphoto(True, ImageTk.PhotoImage(file=resource_path(r'assets\logo.png')))
    r.withdraw()
    
    splash_screen = Loading_screen()
    # MAIN WINDOW CODE + Other Processing
    main_screen = MainWindow(r)
    splash_screen.destroy()
    r.deiconify()
    
    
    
    
    r.mainloop()