import customtkinter as ctk

from PIL import ImageTk, Image, ImageFont

class tl_btn(ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(width=120)
        self.configure(height=40 )
        self.configure(fg_color = 'transparent')
        self.configure(border_color ='#BBE1FA')
        self.configure(text_color = '#BBE1FA')
        self.configure(font = ('Arial',15))
        self.configure(hover_color = '#0F4C75')
        self.configure(border_width = 1)

class tl_lb(ctk.CTkLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(width=120)
        self.configure(wraplength=100)
        self.configure(height=40 )
        self.configure(font = ('Arial',11))
        self.configure(compound = 'left')
        self.configure(justify='left')
        self.configure(text_color='#F9F7F7')
        self.configure(fg_color = 'transparent')
        self.configure(anchor = 'w')

class tl_canvas(ctk.CTkCanvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(background=self.master['bg'])
        self.configure(borderwidth=0)
        self.configure(highlightthickness=0)

class tl_entry(ctk.CTkEntry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(width=120)

class tl_ccb(ctk.CTkComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(width=120)
        