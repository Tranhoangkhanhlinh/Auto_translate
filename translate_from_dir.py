from PIL import Image
from PIL import ImageDraw, ImageFont, ImageFilter, ImageEnhance
import easyocr
import cv2
# from googletrans import Translator
# translator = Translator(service_urls=['translate.google.com'])
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from deep_translator import GoogleTranslator
import numpy as np
import re
from lib.manga_ocr import MangaOcr
import os


def sharpen(image):
    return np.array(ImageEnhance.Sharpness(Image.fromarray(image)).enhance(5.0))

def contrast(image):
    return np.array(ImageEnhance.Contrast(Image.fromarray(image)).enhance(3.0))

def preprocess(image):
    dilated_img = cv2.dilate((image), np.ones((7, 7), np.uint8))
    bg_img = cv2.medianBlur(dilated_img, 17)
    #--- finding absolute difference to preserve edges ---
    diff_img = 255 - cv2.absdiff(image, bg_img)
    #--- normalizing between 0 to 255 ---
    norm_img = cv2.normalize((diff_img), None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    return cv2.threshold((norm_img), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def bb_intersection_over_union(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[2], boxB[2])
    xB = min(boxA[1], boxB[1])
    yB = min(boxA[3], boxB[3])
    interArea = max(0, xB - xA ) * max(0, yB - yA )
    boxAArea = (boxA[0] - boxA[1] ) * (boxA[2] - boxA[3] )
    boxBArea = (boxB[0] - boxB[1] ) * (boxB[2] - boxB[3] )
    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou, min(boxA[0], boxB[0]), min(boxA[2], boxB[2]), max(boxA[1], boxB[1]), max(boxA[3], boxB[3])

def gettxtsize(text, font):
    left, top, right, bottom = font.getbbox(text)
    width = right - left
    height = bottom - top
    return width, height

def text_wrap(text, font, max_width):
    lines = []
    if gettxtsize(text, font)[0] <= max_width:
        lines.append(text) 
    else:
        words = re.split(r'\W+', text)
        i = 0
        while i < len(words):
            line = ''         
            while i < len(words) and gettxtsize(line + words[i] + " ", font)[0] <= max_width:                
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            lines.append(line)    
    return lines
 
 
def draw_text(img,font, text, x, y, x_max, y_max):    
    image_size = x_max - x
    line_height = gettxtsize(text, font)[1] + 10
    lines = text_wrap(text,font, image_size)
    cv2.rectangle(img, (x, y), (x_max, y_max), (255, 255, 255), -1)
    cv2.rectangle(img, (x, y), (x_max, y + (line_height*len(lines))), (255, 255, 255), -1)
    add_text_img = Image.fromarray(img)
    for line in lines:
        ImageDraw.Draw(add_text_img).text((x+5,y),line,font=font,fill=0)
        y = y + line_height
    return np.array(add_text_img)

def translate_img(model, img):
    return model(Image.fromarray(img))

def init_model(pretrained_model, gpu = False):
    return MangaOcr(pretrained_model, gpu)

def get_bboxes(image, model, bbox_min_score = 0.01):
    bboxes = []
    for i in model.detect(sharpen(image), bbox_min_score = bbox_min_score)[0][0]:
        try:
            x_min = min(i[0],i[1])
            y_min = min(i[2],i[3])
            x_max = max(i[0],i[1])
            y_max = max(i[2],i[3])
            for y in bboxes:
                overlap = bb_intersection_over_union([x_min, x_max, y_min, y_max], y)
                if(overlap[0]>0):
                    x_min, y_min, x_max, y_max = overlap[1:]
                    bboxes.remove(y)
            bboxes.append([x_min, x_max, y_min, y_max])
        except Exception as e:
            print(e)
    bboxes=list(set(tuple(element) for element in bboxes))
    for bbox in bboxes:
        for temp_bbox in bboxes:
            #print(bb_intersection_over_union(bbox, temp_bbox)[0])
            iou = bb_intersection_over_union(bbox, temp_bbox)
            if(iou[0]>0 and iou[0]!=1.0):
                if ((bbox[0] - bbox[1] ) * (bbox[2] - bbox[3])>=(temp_bbox[0] - temp_bbox[1]) * (temp_bbox[2] - temp_bbox[3])):
                    bboxes.remove(temp_bbox)
                else:
                    bboxes.remove(bbox)
    return bboxes

def translate_and_add_text_image(model,img, font, bboxes):
    for j in bboxes:
        try:
            #translation = translator.translate(translate_img(model, (((preprocess(img[j[2]:j[3], j[0]:j[1]]))))),dest='en')
            #translation = translator.translate(pytesseract.image_to_string(preprocess(sharpen(((img[j[2]:j[3], j[0]:j[1]])))), lang = "chi_sim_vert+chi_sim").replace(" ", "").replace("\n", ""))
            get_text = (translate_img(model, ((preprocess((img[j[2]:j[3], j[0]:j[1]]))))))
            if get_text:
                translation = GoogleTranslator(source='auto', target='en').translate(get_text)
                if translation:
                    print(get_text + " --> "+ translation)
                    img = draw_text(img,font, translation, j[0],j[2],j[1],j[3])
        except Exception as e:
            print(e)
    return img

def load_images_from_folder(folder):
    file_info = []
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder,filename),0)
        if img is not None:
            print(filename)
            file_info.append([img, filename])
    return file_info

# path = r"C:\Users\ACER\Pictures\Doujinshi\Ganqing fanbook"
# mocr = init_model()
# ezocr = easyocr.Reader(['ja'], gpu=False)
# font = ImageFont.truetype(r"C:\Users\ACER\AI\translate\font\Roboto\Roboto-Regular.ttf",20)
# for file in load_images_from_folder(path):
#     cv2.imwrite('result/'+file[1],translate_and_add_text_image(mocr, file[0], font, get_bboxes(file[0],ezocr,0.01)))
#     print("saved "+ file[1])
