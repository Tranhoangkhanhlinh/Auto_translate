from tkinter.ttk import *
from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog as fd
import tkinter.messagebox 
import translate_from_dir
import os
import easyocr
from PIL import ImageFont
import cv2
import uuid
#----------------------------------------------------------------------

class MainWindow():

    #----------------
    
    def __init__(self, main):
        # Temp var
        self.find_text_model = easyocr.Reader(['ja'], gpu=False)
        self.read_text_model = translate_from_dir.init_model()
        self.main = main
        self.font_path = r"font\Roboto\Roboto-Regular.ttf"
        self.font_size = 30
        self.font = ImageFont.truetype(self.font_path,self.font_size)
        self.temp_pixel = PhotoImage(width=1, height=1)
        self.list_preview_image = []
        self.list_result_image = []
        self.preview_image_number = 0
        self.result_image_number = 0
        self.not_found_img = Image.open(r"assets\not_found_img (1).jpg")
        self.not_found_img.thumbnail((400,680), resample = Image.Resampling.LANCZOS)
        self.not_found_img = ImageTk.PhotoImage(self.not_found_img)
        self.save_dir = "None"

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
        self.run_btn.place(x=50, relx=0.5, rely=0.5, anchor=CENTER)
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

        # CANVAS
        self.preview_canvas = Canvas(main, width = 400,  height = 680)
        self.preview_canvas.place(x=140, y=20) 
        self.result_canvas = Canvas(main, width = 400,  height = 680)
        self.result_canvas.place(x=640, y=20)
        
        # Start_images
        self.img_preview = Image.open(r"assets\start_img.jpg")
        self.img_preview.thumbnail((400,680), resample = Image.Resampling.LANCZOS)
        self.img_preview = ImageTk.PhotoImage(self.img_preview)
        self.img_result = Image.open(r"assets\start_img (1).jpg")
        self.img_result.thumbnail((400,680), resample = Image.Resampling.LANCZOS)
        self.img_result = ImageTk.PhotoImage(self.img_result)
        
        # set first image on canvas
        self.on_preview_canvas = self.preview_canvas.create_image(400/2, 680/2, anchor="center", image=self.img_preview)
        self.on_result_canvas = self.result_canvas.create_image(400/2, 680/2, anchor="center", image=self.img_result)


        self.original_img_lb.lift(self.preview_canvas)
        self.translated_img_lb.lift(self.result_canvas)

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
            if(self.font_size_en.get() != ''):
                print(self.font_size_en.get())
                self.font_size = int(self.font_size_en.get())
            else:
                self.font_size = 30
            self.font = ImageFont.truetype(self.font_path, self.font_size)
            for img in self.list_preview_image:
                print(k)
                progress_var.set(k)
                current_progress.configure(text=str(k)+"/"+str(len(self.list_preview_image)))
                top_lv.update()
                self.list_result_image.append(translate_from_dir.translate_and_add_text_image(self.read_text_model, cv2.imread(img,0), self.font, translate_from_dir.get_bboxes(cv2.imread(img,0),self.find_text_model,0.01)))
                k += 1
            top_lv.destroy()
            self.run_btn.configure(state=NORMAL)
            self.save_dir_btn.configure(state=NORMAL)
            
            
            self.img_result = Image.fromarray(self.list_result_image[0])
            self.img_result.thumbnail((400,680), resample = Image.Resampling.LANCZOS)
            self.img_result = ImageTk.PhotoImage(self.img_result) 
            self.result_canvas.itemconfig(self.on_result_canvas, image=self.img_result)
            self.prev_result_image_btn.configure(state=DISABLED)
        if len(self.list_preview_image) <= 1:
            self.next_result_image_btn.configure(state=DISABLED)
        else:
            self.next_result_image_btn.configure(state=NORMAL)
        

    #----------------

    def next_result_image(self):
        self.result_image_number += 1 
        if self.result_image_number <= (len(self.list_result_image)-1):
            self.prev_result_image_btn.configure(state=NORMAL)
            self.img_result = Image.fromarray(self.list_result_image[self.result_image_number])
            self.img_result.thumbnail((400,680), resample = Image.Resampling.LANCZOS)
            self.img_result = ImageTk.PhotoImage(self.img_result) 
            self.result_canvas.itemconfig(self.on_result_canvas, image=self.img_result)
        if self.result_image_number == (len(self.list_result_image)-1):
            self.next_result_image_btn.configure(state=DISABLED)

    #----------------

    def prev_result_image(self):
        self.result_image_number -= 1 
        if self.result_image_number == 0:
            self.prev_result_image_btn.configure(state=DISABLED)
        self.next_result_image_btn.configure(state=NORMAL)
        self.img_result = Image.fromarray(self.list_result_image[self.result_image_number])
        self.img_result.thumbnail((400,680), resample = Image.Resampling.LANCZOS)
        self.img_result = ImageTk.PhotoImage(self.img_result) 
        self.result_canvas.itemconfig(self.on_result_canvas, image=self.img_result)

    #----------------

    def get_save_folder_path(self):
        if len(self.list_result_image) != 0:
            save_folder_path = fd.askdirectory() 
            # change image
            if save_folder_path is not None and save_folder_path != '':
                self.save_dir = save_folder_path
                self.save_dir_lb.config(text=save_folder_path)  
                for translated_img in self.list_result_image:
                    cv2.imwrite(save_folder_path+"/" + str(uuid.uuid4())+".jpg", translated_img)
        else:
            tkinter.messagebox.showinfo("Không tìm thấy ảnh đã dịch",  "HÌnh như đã có lỗi trong quá trình dịch, phiền bạn kiểm tra lại kết nối Internet và tiến hành chạy lại chương trình")
            
            

#----------------------------------------------------------------------
if __name__ == '__main__':
    r = Tk()
    r.title('Phần mềm dịch truyện được viết bằng Python')
    r.config(bg='white')
    r.geometry('1080x900')
    photo = PhotoImage(file = 'assets\logo.png')
    r.wm_iconphoto(False, photo)
    MainWindow(r)
    r.mainloop()