from tkinter.ttk import *
from tkinter import *
from PIL import ImageTk, Image, ImageFont
from tkinter import filedialog as fd
import tkinter.messagebox 
import translate_from_dir
import os
import easyocr
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

class MainWindow():

    #----------------
    
    def __init__(self, main):

        # Temp var
        self.find_text_model_cn = easyocr.Reader(['ch_tra'], gpu=False)
        self.find_text_model_kr = easyocr.Reader(['ko'], gpu=False)
        self.find_text_model_jp = easyocr.Reader(['ja'], gpu=False)
        self.main_lang_detect = None
        self.read_text_model = translate_from_dir.init_model(pretrained_model = resource_path('lib/manga_ocr/manga-ocr-base'),gpu = False)
        # self.find_text_model = ""
        # self.read_text_model =""

        self.main = main
        self.font_path = resource_path(r"font\Roboto\Roboto-Regular.ttf")
        self.font_size = 30
        self.font = ImageFont.truetype(self.font_path,self.font_size)
        self.temp_pixel = PhotoImage(width=1, height=1)
        self.list_preview_image = []
        self.list_result_image = []
        self.preview_image_number = 0
        self.result_image_number = 0
        self.not_found_img = Image.open(resource_path(r"assets\not_found_img (1).jpg"))
        self.not_found_img.thumbnail((400,680), resample = Image.Resampling.LANCZOS)
        self.not_found_img = ImageTk.PhotoImage(self.not_found_img)
        self.save_dir = "None"
        self.internet_connection = "Connected"

        #Combobox select translate language
        self.support_translate_lang = {'Tiếng Việt': 'vi', 'Tiếng Anh':'en'}
        self.default_lang = StringVar(value = 'Tiếng Việt')
        self.select_default_lang_ccb = Combobox(main,width=15, height=20, values=list(self.support_translate_lang.keys()), justify="center", textvariable=self.default_lang)
        self.select_default_lang_ccb.bind('<<ComboboxSelected>>',self.on_update_translate_lang)
        self.select_default_lang_ccb.place(x = 10, y = 460)
        self.select_default_lang_lb = Label(main, text = "Ngôn ngữ bạn muốn dịch", wraplength=130)
        self.select_default_lang_lb.place(x = 10, y = 420)
        self.default_lang_val = self.support_translate_lang[self.default_lang.get()]

        # Internet Connection checking
        self.internet_checking_canvas = Canvas(main, width=100, height=20, borderwidth=0, highlightthickness=0)
        self.internet_checking_canvas.pack()
        self.internet_checking_canvas.place(x = 10, y= 730)
        self.internet_checking_circle_state = self.internet_checking_canvas.create_oval(5,5,15,15, fill='green')
        self.internet_connection_lb = Label(self.internet_checking_canvas, text= self.internet_connection)
        self.internet_connection_lb.pack()
        self.internet_connection_lb.place(x=20, y=0)
        self.internet_checking_lb = Label(main, text= "Tình trạng kết nối Internet:", wraplength=130, justify=LEFT)
        self.internet_checking_lb.pack()
        self.internet_checking_lb.place(x=10, y = 690)

        #BUTTON
        # Get file button
        self.get_file_btn = Button(main, text='Get file', image=self.temp_pixel, compound='c', width=100, height=20, command=self.get_file_path)
        self.get_file_btn.place( x = 10, y = 20)
        # Get folder button
        self.get_folder_btn = Button(main, text='Get folder', image=self.temp_pixel, compound='c', width=100, height=20, command=self.get_folder_path)
        self.get_folder_btn.place( x = 10, y = 60)
        # Save file location button
        self.save_dir_btn = Button(main, text='Save file', image=self.temp_pixel, compound='c',state=DISABLED, width=100, height=20, command=self.get_save_folder_path)
        self.save_dir_btn.place( x = 10, y = 100)
        # Run OCR on selected
        self.run_btn = Button(main, text='Run model', image=self.temp_pixel, compound='c', width=100, height=20, command=self.run_model)
        self.run_btn.place(x=590, rely=0.5, anchor=CENTER)
        # next image on preview
        self.next_preview_image_btn = Button(main, text='Next image', image=self.temp_pixel, compound='c', state=DISABLED, width=100, height=20, command=self.next_preview_image)
        self.next_preview_image_btn.place(x=440, y = 720)
        # previous image on preview
        self.prev_preview_image_btn = Button(main, text='Prev image', image=self.temp_pixel, compound='c', state=DISABLED, width=100, height=20, command=self.prev_preview_image)
        self.prev_preview_image_btn.place(x=140, y = 720)
        # next image on preview
        self.next_result_image_btn = Button(main, text='Next image', image=self.temp_pixel, compound='c', state=DISABLED, width=100, height=20, command=self.next_result_image)
        self.next_result_image_btn.place(x=940, y = 720)
        # previous image on preview
        self.prev_result_image_btn = Button(main, text='Prev image', image=self.temp_pixel, compound='c', state=DISABLED, width=100, height=20, command=self.prev_result_image)
        self.prev_result_image_btn.place(x=640, y = 720)
        # Pick font button
        self.pick_font_btn = Button(main, text='Pick my font', image=self.temp_pixel, compound='c', width=100, height=20, command=self.get_font_path)
        self.pick_font_btn.place(x=10, y = 320)
        # Add translated_text_frame
        self.add_translated_frame_btn = Button(main, text='Thêm bản dịch', image=self.temp_pixel, compound='c', width=100, height=20,state=DISABLED, command=self.add_translated_frame)
        self.add_translated_frame_btn.place(x=1310, y = 720)
        # Add translated_text_frame
        self.update_translated_btn = Button(main, text='Cập nhật bản dịch', image=self.temp_pixel, compound='c', width=100, height=20,state=DISABLED, command=self.return_update_translated_image)
        self.update_translated_btn.place(x=1060, y = 720)

        # LABEL
        self.save_dir_lb = Label(main, text = self.save_dir, wraplength=100)
        self.save_dir_lb.place(x = 10,y = 130)
        self.pick_font_lb = Label(main, text = self.font_path, wraplength=100)
        self.pick_font_lb.place(x = 10,y = 350)
        self.original_img_lb = Label(main, text = "Ảnh gốc",  bd=0)
        self.original_img_lb.configure(font=("Arial", 15))
        self.original_img_lb.place(y = 10,x = 180)
        self.translated_img_lb = Label(main, text = "Ảnh sau khi dịch",  bd=0)
        self.translated_img_lb.configure(font=("Arial", 15))
        self.translated_img_lb.place(y = 10,x = 680)

        # ENTRY
        # name using widget Label
        self.font_size_lb = Label(main, text = 'Font size', font=('Arial',10))
        self.font_size_lb.place(x = 10, y=250)
        self.default_font_size = IntVar(value=30)
        self.font_size_en = Entry(main, textvariable = self.default_font_size, font=('Arial',10))
        self.font_size_en.place(x = 10, y=280)
        self.default_font_size.trace_add('write', self.on_update_global_font_size)

        # CANVAS
        self.preview_canvas = Canvas(main, width = 400,  height = 680)
        self.preview_canvas.place(x=140, y=20) 
        self.result_canvas = Canvas(main, width = 400,  height = 680)
        self.result_canvas.place(x=640, y=20)

        # FRAMES
        self.main_translated_frame = Frame(main,width=360, height=680, background="bisque")
        self.main_translated_frame.grid(sticky='nw')
        self.main_translated_frame.place(x=1060, y = 20)
        self.main_translated_frame.grid_propagate(False)

        # Create a frame for the canvas with non-zero row&column weights
        self.frame_canvas = Frame(self.main_translated_frame)
        self.frame_canvas.grid(row=1, column=0, sticky='nw')
        self.frame_canvas.grid_rowconfigure(0, weight=1)
        self.frame_canvas.grid_columnconfigure(0, weight=1)
        self.frame_canvas.grid_propagate(False)

        # Add a canvas in that frame
        self.translated_canvas = Canvas(self.frame_canvas)
        self.translated_canvas.grid(row=0, column=0, sticky="ns")

        # Link a scrollbar to the canvas
        vsb = Scrollbar(self.frame_canvas, orient="vertical", command=self.translated_canvas.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        self.translated_canvas.configure(yscrollcommand=vsb.set)

        self.translated_frame = Frame(self.translated_canvas,width=360, height=680)
        self.translated_canvas.create_window((0, 0), window=self.translated_frame, anchor='nw')
        rows = 0
        self.list_translated_frame = []
        # for i in range(0, rows):
        #         self.list_translated_frame.append(Modify_translated_text(self.translated_frame,uuid.uuid4().hex, 0,0,0,0, 'Roboto', 30, "a", "b"))
        #         self.list_translated_frame[-1].grid(row=i,column=1, pady=10)
        #         self.list_translated_frame[-1].config(highlightthickness=1,highlightbackground="blue")

        # Update buttons frames idle tasks to let tkinter calculate buttons sizes

        # Resize the canvas frame to show exactly 5-by-5 buttons and the scrollbar
        # first5columns_width = sum([buttons[0][j].winfo_width() for j in range(0, 5)])
        # first5rows_height = sum([buttons[i][0].winfo_height() for i in range(0, 5)])
        # self.frame_canvas.config(width=first5columns_width + vsb.winfo_width(),
        #                     height=first5rows_height)
        self.frame_canvas.config(width=360, height=680)

        # Set the canvas scrolling region
        self.translated_canvas.config(scrollregion=self.translated_canvas.bbox("all"))
        
        # Start_images
        self.img_preview = Image.open(resource_path(r"assets\start_img.jpg"))
        self.img_preview.thumbnail((400,680), resample = Image.Resampling.LANCZOS)
        self.img_preview = ImageTk.PhotoImage(self.img_preview)
        self.img_result = Image.open(resource_path(r"assets\start_img (1).jpg"))
        self.img_result.thumbnail((400,680), resample = Image.Resampling.LANCZOS)
        self.img_result = ImageTk.PhotoImage(self.img_result)
        
        # set first image on canvas
        self.on_preview_canvas = self.preview_canvas.create_image(400/2, 680/2, anchor="center", image=self.img_preview)
        self.on_result_canvas = self.result_canvas.create_image(400/2, 680/2, anchor="center", image=self.img_result)


        self.original_img_lb.lift(self.preview_canvas)
        self.translated_img_lb.lift(self.result_canvas)
        self.is_connected()
    #---------------

    def is_connected(self):
        try:
            request = requests.get("https://translate.google.com/m",timeout=10)
            self.internet_connection = "Connected"
            self.internet_checking_canvas.itemconfig(self.internet_checking_circle_state, fill='green')
        except OSError:
            self.internet_connection = "Disconnected"
            self.internet_checking_canvas.itemconfig(self.internet_checking_circle_state, fill='red')
        finally:
            self.internet_connection_lb.config(text=self.internet_connection)
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
            self.add_translated_frame_btn.config(state=DISABLED)
            self.update_translated_btn.config(state=DISABLED)
            self.preview_image_number = 0
            self.result_image_number = 0
            self.list_preview_image.clear()
            self.list_result_image.clear()
            self.img_preview = Image.open(file)
            self.list_preview_image.append(file)
            self.img_preview.thumbnail((400,680), resample = Image.Resampling.LANCZOS)
            self.img_preview = ImageTk.PhotoImage(self.img_preview)
            self.preview_canvas.itemconfig(self.on_preview_canvas, image=self.img_preview)
            self.result_canvas.itemconfig(self.on_result_canvas, image=self.not_found_img)
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
            self.add_translated_frame_btn.config(state=DISABLED)
            self.update_translated_btn.config(state=DISABLED)
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
                self.img_preview.thumbnail((400,680), resample = Image.Resampling.LANCZOS)
                self.img_preview = ImageTk.PhotoImage(self.img_preview) 
                self.preview_canvas.itemconfig(self.on_preview_canvas, image=self.img_preview)
                self.result_canvas.itemconfig(self.on_result_canvas, image=self.not_found_img)
            else:
                self.preview_canvas.itemconfig(self.on_preview_canvas, image=self.not_found_img)
                self.result_canvas.itemconfig(self.on_preview_canvas, image=self.not_found_img)
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
            self.img_preview.thumbnail((400,680), resample = Image.Resampling.LANCZOS)
            self.img_preview = ImageTk.PhotoImage(self.img_preview) 
            self.preview_canvas.itemconfig(self.on_preview_canvas, image=self.img_preview)
        if self.preview_image_number == (len(self.list_preview_image)-1):
            self.next_preview_image_btn.configure(state=DISABLED)

    #----------------

    def prev_preview_image(self):
        self.preview_image_number -= 1 
        if self.preview_image_number == 0:
            self.prev_preview_image_btn.configure(state=DISABLED)
        self.next_preview_image_btn.configure(state=NORMAL)
        self.img_preview = Image.open(self.list_preview_image[self.preview_image_number])
        self.img_preview.thumbnail((400,680), resample = Image.Resampling.LANCZOS)
        self.img_preview = ImageTk.PhotoImage(self.img_preview) 
        self.preview_canvas.itemconfig(self.on_preview_canvas, image=self.img_preview)
        

    #----------------

    def run_model(self):
        if len(self.list_preview_image) == 0:
            tkinter.messagebox.showinfo("Image file not found",  "HÌnh như thư mục bạn đã chọn không có tệp định dạng ảnh")
        else:
            if self.internet_connection == "Disconnected":
                if tkinter.messagebox.askquestion("Không có kết nối mạng", "Phần mềm sử dụng Google Dịch nên cần có kết nối mạng, nhưng tôi không thể kết nối đến Google Dịch, bạn có muốn tiếp với kết quả dịch bị bỏ trống?", icon='warning') == "no":
                    return
            self.main_lang_detect = None
            self.run_btn.configure(state=DISABLED)
            top_lv = Toplevel(self.main)
            top_lv.geometry('500x100')
            top_lv.title("Vui lòng chờ")
            Label(top_lv, text="Tiến độ dịch truyện của chương trình").pack()
            current_progress = Label(top_lv, text="0/"+str(len(self.list_preview_image)))
            current_progress.pack()
            progress_var = StringVar()
            progressbar = Progressbar(top_lv, variable=progress_var, maximum=len(self.list_preview_image))
            progressbar.pack(fill=X, expand=1)
            k = 0
            progress_var.set(k)
            current_progress.configure(text="Đang xác định ngôn ngữ của truyện")
            top_lv.update()

            if(self.font_size_en.get() != ''):
                self.font_size = int(self.font_size_en.get())
            else:
                self.font_size = 30
            self.font = ImageFont.truetype(self.font_path, self.font_size)
            self.clear_translated_frame(self.translated_frame)
            self.list_result_image.clear()
            get_first_5_img = 5 if len(self.list_preview_image) > 5 else len(self.list_preview_image)
            self.main_lang_detect = translate_from_dir.detect_lang_in_image(self.find_text_model_jp,self.find_text_model_kr,self.find_text_model_cn, self.list_preview_image[0:get_first_5_img])

            for img in self.list_preview_image:
                progress_var.set(k)
                current_progress.configure(text=str(k)+"/"+str(len(self.list_preview_image)))
                top_lv.update()
                if self.main_lang_detect == 'jp' or self.main_lang_detect=='cn':
                    self.list_result_image.append(translate_from_dir.get_translate_data(self.read_text_model,"", cv2.imread(img,0), self.font, translate_from_dir.get_bboxes(cv2.imread(img,0),self.find_text_model_jp,0.01),self.internet_connection, self.default_lang_val))
                else:
                    self.list_result_image.append(translate_from_dir.get_translate_data("",self.find_text_model_kr, cv2.imread(img,0), self.font, translate_from_dir.get_bboxes(cv2.imread(img,0),self.find_text_model_jp,0.01),self.internet_connection, self.default_lang_val))
                # self.list_result_image.append(translate_from_dir.get_translate_data(self.read_text_model, cv2.imread(img,0),""))
                k += 1
            top_lv.destroy()
            self.run_btn.configure(state=NORMAL)
            self.save_dir_btn.configure(state=NORMAL)
            
            self.result_image_number = 0
            self.img_result = Image.fromarray(self.list_result_image[self.result_image_number][0])
            self.img_result.thumbnail((400,680), resample = Image.Resampling.LANCZOS)
            self.img_result = ImageTk.PhotoImage(self.img_result) 
            self.result_canvas.itemconfig(self.on_result_canvas, image=self.img_result)
            self.prev_result_image_btn.configure(state=DISABLED)
            for data in self.list_result_image[self.result_image_number][1]:
                temp = Modify_translated_text(self.translated_frame,uuid.uuid4().hex, data[0],data[1],data[2],data[3], self.font_path, self.font_size, data[4],data[5], self.default_lang_val)
                temp.pack(pady=10)
                temp.config(highlightthickness=1,highlightbackground="blue")
                self.list_translated_frame.append(temp)
                self.translated_frame.update_idletasks()
                if(len(self.list_translated_frame) > 0 and sum([self.list_translated_frame[i].winfo_height() for i in range(0, len(self.list_translated_frame))]) < 680):
                    frame_canvas_height = sum([self.list_translated_frame[i].winfo_height() for i in range(0, len(self.list_translated_frame))])
                else:
                    frame_canvas_height = 680
                self.frame_canvas.config(width=360, height=frame_canvas_height)
                self.translated_canvas.config(scrollregion=self.translated_canvas.bbox("all"))
            self.add_translated_frame_btn.config(state=NORMAL)
            self.update_translated_btn.config(state=NORMAL)
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
            self.img_result.thumbnail((400,680), resample = Image.Resampling.LANCZOS)
            self.img_result = ImageTk.PhotoImage(self.img_result) 
            self.result_canvas.itemconfig(self.on_result_canvas, image=self.img_result)
        if self.result_image_number == (len(self.list_result_image)-1):
            self.next_result_image_btn.configure(state=DISABLED)
        self.clear_translated_frame(self.translated_frame)
        for data in self.list_result_image[self.result_image_number][1]:
                if len(data)>6:
                    temp = Modify_translated_text(self.translated_frame,uuid.uuid4().hex, data[0],data[1],data[2],data[3], data[4], data[5], data[6],data[7], self.default_lang_val)
                else:
                    temp = Modify_translated_text(self.translated_frame,uuid.uuid4().hex, data[0],data[1],data[2],data[3],self.font_path, self.font_size, data[4], data[5], self.default_lang_val)
                temp.pack(pady=10)
                temp.config(highlightthickness=1,highlightbackground="blue")
                self.list_translated_frame.append(temp)
                self.translated_frame.update_idletasks()
                if(len(self.list_translated_frame) > 0 and sum([self.list_translated_frame[i].winfo_height() for i in range(0, len(self.list_translated_frame))]) < 680):
                    frame_canvas_height = sum([self.list_translated_frame[i].winfo_height() for i in range(0, len(self.list_translated_frame))])
                else:
                    frame_canvas_height = 680
                self.frame_canvas.config(width=360, height=frame_canvas_height)
                self.translated_canvas.config(scrollregion=self.translated_canvas.bbox("all"))

    #----------------

    def prev_result_image(self):
        self.result_image_number -= 1 
        if self.result_image_number == 0:
            self.prev_result_image_btn.configure(state=DISABLED)
        self.next_result_image_btn.configure(state=NORMAL)
        self.img_result = Image.fromarray(self.list_result_image[self.result_image_number][0])
        self.img_result.thumbnail((400,680), resample = Image.Resampling.LANCZOS)
        self.img_result = ImageTk.PhotoImage(self.img_result) 
        self.result_canvas.itemconfig(self.on_result_canvas, image=self.img_result)
        self.clear_translated_frame(self.translated_frame)
        for data in self.list_result_image[self.result_image_number][1]:
                if len(data)>6:
                    temp = Modify_translated_text(self.translated_frame,uuid.uuid4().hex, data[0],data[1],data[2],data[3], data[4], data[5], data[6],data[7], self.default_lang_val)
                else:
                    temp = Modify_translated_text(self.translated_frame,uuid.uuid4().hex, data[0],data[1],data[2],data[3],self.font_path, self.font_size, data[4], data[5], self.default_lang_val)
                temp.pack(pady=10)
                temp.config(highlightthickness=1,highlightbackground="blue")
                self.list_translated_frame.append(temp)
                self.translated_frame.update_idletasks()
                if(len(self.list_translated_frame) > 0 and sum([self.list_translated_frame[i].winfo_height() for i in range(0, len(self.list_translated_frame))]) < 680):
                    frame_canvas_height = sum([self.list_translated_frame[i].winfo_height() for i in range(0, len(self.list_translated_frame))])
                else:
                    frame_canvas_height = 680
                self.frame_canvas.config(width=360, height=frame_canvas_height)
                self.translated_canvas.config(scrollregion=self.translated_canvas.bbox("all"))

    #----------------

    def get_save_folder_path(self):
        if len(self.list_result_image) != 0:
            save_folder_path = fd.askdirectory() 
            # change image
            if save_folder_path is not None and save_folder_path != '':
                self.save_dir = save_folder_path
                self.save_dir_lb.config(text=save_folder_path)  
                for file in self.list_result_image:
                    cv2.imwrite(save_folder_path+"/" + str(uuid.uuid4())+".jpg", file[0])
        else:
            tkinter.messagebox.showinfo("Không tìm thấy ảnh đã dịch",  "HÌnh như đã có lỗi trong quá trình dịch, phiền bạn kiểm tra lại kết nối Internet và tiến hành chạy lại chương trình")
            
    #----------------

    def add_translated_frame(self):
        temp = Modify_translated_text(self.translated_frame,uuid.uuid4().hex, 0,0,0,0, self.font_path, self.font_size, "a", "b", self.default_lang_val)
        temp.pack(pady=10)
        temp.config(highlightthickness=1,highlightbackground="blue")
        self.list_translated_frame.append(temp)
        self.translated_frame.update_idletasks()
        if(len(self.list_translated_frame) > 0 and sum([self.list_translated_frame[i].winfo_height() for i in range(0, len(self.list_translated_frame))]) < 680):
            frame_canvas_height = sum([self.list_translated_frame[i].winfo_height() for i in range(0, len(self.list_translated_frame))])
        else:
            frame_canvas_height = 680
        self.frame_canvas.config(width=360, height=frame_canvas_height)
        self.translated_canvas.config(scrollregion=self.translated_canvas.bbox("all"))

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
        self.img_result.thumbnail((400,680), resample = Image.Resampling.LANCZOS)
        self.img_result = ImageTk.PhotoImage(self.img_result) 
        self.result_canvas.itemconfig(self.on_result_canvas, image=self.img_result)

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

class Modify_translated_text(Frame):
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
        self.config(pady=10, padx=10)
        #widgets

        self.temp_font_size = IntVar(value = self.font_size)
        self.temp_x_min = IntVar(value = self.x_min)
        self.temp_y_min = IntVar(value = self.y_min)
        self.temp_x_max = IntVar(value = self.x_max)
        self.temp_y_max = IntVar(value = self.y_max)
        self.temp_ori_text = StringVar(value= self.original_text)
        self.temp_trans_text = StringVar(value = self.translated_text)


        # create all of the main containers
        self.top_frame = Frame(self, width=200, pady=3)
        self.center = Frame(self, width=200, pady=3)
        self.bottom_frame = Frame(self, width=200, pady=3)

        # layout all of the main containers
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.top_frame.grid(row=0, sticky="ew")
        self.center.grid(row=1, sticky="w")
        self.bottom_frame.grid(row=2, sticky="w")

        # create the widgets for the top frame
        # model_label = Label(top_frame, text='Model Dimensions')
        self.id_lb = Label(self.top_frame, text="ID: "+self.id)
        self.x_min_lb = Label(self.top_frame, text='X_min:')
        self.y_min_lb = Label(self.top_frame, text='Y_min:')
        self.x_max_lb = Label(self.top_frame, text='X_max:')
        self.y_max_lb = Label(self.top_frame, text='Y_max:')
        self.x_min_en = Entry(self.top_frame,textvariable= self.temp_x_min, width=18)
        self.y_min_en = Entry(self.top_frame,textvariable= self.temp_y_min, width=18)
        self.x_max_en = Entry(self.top_frame,textvariable= self.temp_x_max, width=18)
        self.y_max_en = Entry(self.top_frame,textvariable= self.temp_y_max, width=18)

        # layout the widgets in the top frame
        # model_label.grid(row=0, columnspan=4)
        self.id_lb.grid(row = 0, columnspan=4, sticky='w')
        self.x_min_lb.grid(row=1, column=0)
        self.y_min_lb.grid(row=1, column=2)
        self.x_max_lb.grid(row=2, column=0)
        self.y_max_lb.grid(row=2, column=2)
        self.x_min_en.grid(row=1, column=1)
        self.y_min_en.grid(row=1, column=3)
        self.x_max_en.grid(row=2, column=1)
        self.y_max_en.grid(row=2, column=3)

        # create the center widgets
        self.original_txt_lb = Label(self.center, text='Văn bản gốc:', justify=RIGHT)
        self.original_txt_en = Text(self.center,width=39,height = 5)
        self.original_txt_en.insert(END, self.original_text)
        self.original_txt_en.bind('<KeyRelease>', self.on_update_original_text)
        self.original_txt_lb.grid(row=3, sticky='w')
        self.original_txt_en.grid(row=4, sticky='w', columnspan=2)
        self.translated_txt_lb = Label(self.center, text='Văn bản sau khi dịch:', justify=LEFT)
        self.translated_txt_en = Text(self.center, width=39, height = 5)
        self.translated_txt_en.insert(END, self.translated_text)
        self.translated_txt_en.bind('<KeyRelease>', self.on_update_translated_text)
        self.translated_txt_lb.grid(row=5,sticky='w', column=0)
        self.translated_txt_en.grid(row=6,sticky='w',columnspan=2)
        self.translate_btn = Button(self.center, text="Dịch lại", command=self.translate_from_original_text)
        self.translate_btn.grid(row=5, column=1, sticky='e')

        self.font_size_lb = Label(self.bottom_frame, text='Font size:', width=10)
        self.font_size_en = Entry(self.bottom_frame,textvariable= self.temp_font_size, width=10)
        self.temp_font_size.trace_add('write', self.on_update_font_size)
        self.font_size_lb.grid(row=7, column=0)
        self.font_size_en.grid(row=7, column=1)
        self.font_type_lb = Label(self.bottom_frame, text='Font type:')
        self.font_type_lb.grid(row=7, column=2)
        self.font_type_btn = Button(self.bottom_frame, text='Pick my font', command=self.get_font_path)
        self.font_type_btn.grid(row=7, column=3)
        self.font_type_path_lb = Label(self.bottom_frame, text=self.font_type,wraplength=140)
        self.font_type_path_lb.grid(row=8, column=2, columnspan=2)

        self.del_translated_text = Button(self.bottom_frame, text='Xóa bản dịch này', command=self.delete_translated_box)
        self.del_translated_text.grid(row=8, column=0, pady=10)

        
        
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

#----------------------------------------------------------------------
def centerWindow(width, height, root):  # Return 4 values needed to center Window
    screen_width = root.winfo_screenwidth()  # Width of the screen
    screen_height = root.winfo_screenheight() # Height of the screen     
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    return int(x), int(y)

if __name__ == '__main__':
    r = Tk()
    r.title('Phần mềm dịch truyện được viết bằng Python')
    r.config(bg='white')
    r.geometry('1440x900')
    photo = PhotoImage(file = resource_path(r'assets\logo.png'))
    r.wm_iconphoto(False, photo)
    r.withdraw()

    # SPLASH SCREEN CODE
    splash_screen = Toplevel(background="white")
    splash_screen.overrideredirect(True)
    splash_screen.title("Splash Screen")
    temp_pixel = PhotoImage(width=1, height=1)
    temp_lb = Label(splash_screen, text="Cảm ơn bạn vì đã sử dụng phần mềm. Vui lòng chờ trong lúc chương trình khởi chạy nhé.", font=("Arial", 20), wraplength= 519,image=temp_pixel, compound='c', width=519, height=100)
    temp_lb.pack()
    temp_lb.place(x= 0 , y = 300)
    x, y = centerWindow(519, 400, r)
    splash_screen.geometry(f"519x400+{x}+{y}")
    
    image = tkinter.PhotoImage(file=resource_path(r'assets/loading_screen.png')) 
    label = Label(splash_screen, image = image)
    label.pack()
    splash_screen.update()
    
    # MAIN WINDOW CODE + Other Processing
    MainWindow(r)
    
    # Start the event loop
    r.deiconify()
    splash_screen.destroy()
    
    
    
    r.mainloop()