import pandas as pd
import PIL
from PIL import Image
from PIL import ImageDraw, ImageFont, ImageFilter
import easyocr
import cv2
from googletrans import Translator
import pytesseract
import numpy as np
translator = Translator(service_urls=['translate.google.com'])
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

#thresholding
def thresholding(image):
    return cv2.threshold(image, 160, 255, cv2.THRESH_BINARY)[1]

def sharpen(image):
    #kernel = np.array([[-2, -2, -2], [-2, 32, -2], [-2, -2, -2]]) 
    #return cv2.filter2D(image, -1, kernel)
    return np.array(Image.fromarray(image).filter(ImageFilter.EDGE_ENHANCE_MORE))

def blur(image):
    return cv2.GaussianBlur(image, (7, 7), 0) 

def contrast(image,brightness = 0, contrast=5):
    return (cv2.addWeighted(image, contrast, np.zeros(image.shape, image.dtype), 0, brightness))

def equalhist(image):
    return cv2.equalizeHist(image)

def bb_intersection_over_union(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[2], boxB[2])
    xB = min(boxA[1], boxB[1])
    yB = min(boxA[3], boxB[3])
    # compute the area of intersection rectangle
    interArea = max(0, xB - xA ) * max(0, yB - yA )
    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = (boxA[0] - boxA[1] ) * (boxA[2] - boxA[3] )
    boxBArea = (boxB[0] - boxB[1] ) * (boxB[2] - boxB[3] )
    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)
    # return the intersection over union value
    return iou, min(boxA[0], boxB[0]), min(boxA[2], boxB[2]), max(boxA[1], boxB[1]), max(boxA[3], boxB[3])

def gettxtsize(text):
    size, _ = cv2.getTextSize(text=text, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, thickness=1)
    return size

def text_wrap(text, max_width):
    lines = []
    # If the width of the text is smaller than image width
    # we don't need to split it, just add it to the lines array
    # and return
    if gettxtsize(text)[0] <= max_width:
        lines.append(text)
    else:
        # split the line by spaces to get words
        words = text.split(' ')  
        i = 0
        # append every word to a line while its width is shorter than image width
        while i < len(words):
            line = ''        
            while i < len(words) and gettxtsize(line + words[i])[0] <= max_width:                
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            # when the line gets longer than the max width do not append the word,
            # add the line to the lines array
            lines.append(line)    
    return lines
 
 
def draw_text(img, text, x, y, x_max, y_max):    
    
    # size() returns a tuple of (width, height)
    image_size = (y_max - y)/2 if y_max - y > 260 else y_max - y
    line_height = gettxtsize(text)[1] + 10
    # create the ImageFont instance
    #textSize = cv2.getTextSize(text=text, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, thickness=1)

    # get shorter lines
    lines = text_wrap(text, image_size)
    #print(lines) # ['This could be a single line text ', 'but its too long to fit in one. ']
    
    cv2.rectangle(img, (x, y), (x_max, y_max), (255, 255, 255), -1)
    for line in lines:
        # draw the line on the image
        cv2.putText(img,line, 
                    (x,y+30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1,
                    (0,0,0),
                    2,
                    2)
        
        # update the y position so that we can use it for next line
        y = y + line_height
    return img


img = cv2.imread(r"C:\Users\ACER\Pictures\Doujinshi\Ganqing fanbook\_10.jpg",0)
reader = easyocr.Reader(['ch_sim'], gpu=False)
bounds = reader.detect(img)
#im = PIL.Image.open(r"C:\Users\ACER\Pictures\Doujinshi\Ganqing fanbook\_01.jpg")
bboxes = []

for i in bounds[0][0]:
    try:
        x_min = i[0]
        y_min = i[2]
        x_max = i[1]
        y_max = i[3]
        flag_overlap = False
        for y in bounds[0][0]:
            overlap = bb_intersection_over_union([x_min, x_max, y_min, y_max], y)
            if(overlap[0]!=0.0):
                flag_overlap = True
                x_min, y_min, x_max, y_max = overlap[1:]
        bboxes.append([x_min, x_max, y_min, y_max])
    except Exception as e:
        print(e)

bboxes=list(set(tuple(element) for element in bboxes))
for bbox in bboxes:
    for temp_bbox in bboxes:
        print(bb_intersection_over_union(bbox, temp_bbox))
        if(bb_intersection_over_union(bbox, temp_bbox)[0]>=0.8):
            if(bbox[0] != temp_bbox[0] or bbox[1] != temp_bbox[1] or bbox[2] != temp_bbox[2] or bbox[3] != temp_bbox[3]):
                if ((bbox[0] - bbox[1] ) * (bbox[2] - bbox[3])>=(temp_bbox[0] - temp_bbox[1]) * (temp_bbox[2] - temp_bbox[3])):
                    bboxes.remove(temp_bbox)
                else:
                    bboxes.remove(bbox)
    print("__________________________")

for j in bboxes:
    try:
        temp_img = sharpen(thresholding(sharpen(thresholding(blur((img[j[2]:j[3], j[0]:j[1]]))))))
        translation = translator.translate(pytesseract.image_to_string(temp_img, lang = "chi_sim_vert+chi_sim").replace(" ", "").replace("\n", ""))
        print(f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})")
        img = draw_text(img, translation.text, j[0],j[2],j[1],j[3])
        #cv2.imshow("Image", temp_img)
    
        # Wait for the user to press a key
        #cv2.waitKey(0)
    except Exception as e:
        print(e)
    # finally:
        #cv2.rectangle(img, (j[0], j[2]), (j[1], j[3]), (0, 0, 255), 2)

img = cv2.resize(img, None, fx = 0.4, fy = 0.4)
cv2.imshow("Image", img)
    
        # Wait for the user to press a key
cv2.waitKey(0)