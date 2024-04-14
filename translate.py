# import pandas as pd
# from PIL import Image
# from PIL import ImageDraw, ImageFont, ImageFilter, ImageEnhance
# import easyocr
# import cv2
# from googletrans import Translator
# from deep_translator import GoogleTranslator,LingueeTranslator
# import pytesseract
# import numpy as np
# import re
# import jaconv
# from lib.manga_ocr import MangaOcr

# translator = Translator(service_urls=['translate.google.com'])
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# #thresholding
# def thresholding(image):
#     #return cv2.threshold(image, 80, 255, cv2.THRESH_BINARY)[1]
#     #return cv2.adaptiveThreshold(image, 255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 4)
#     return np.array(Image.fromarray(image).filter(ImageFilter.UnsharpMask(radius = 4, percent = 500, threshold = 8)))

# def sharpen(image):
#     # kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]]) 
#     # return cv2.filter2D(image, -1, kernel)
#     #return np.array(Image.fromarray(image).filter(ImageFilter.SHARPEN))
#     #return np.array(Image.fromarray(image).filter(ImageFilter.EDGE_ENHANCE_MORE))
#     return np.array(ImageEnhance.Sharpness(Image.fromarray(image)).enhance(5.0))

# def enhance_edge(image):
#     return np.array(Image.fromarray(image).filter(ImageFilter.EDGE_ENHANCE_MORE))

# def blur(image):
#     return cv2.GaussianBlur(image, (7, 7), 0) 

# def contrast(image):
#     return np.array(ImageEnhance.Contrast(Image.fromarray(image)).enhance(5.0))

# def equalhist(image):
#     return cv2.equalizeHist(image)

# def bilateral_filtering(image):
#     return cv2.bilateralFilter(image,9,75,75)

# def preprocess(image):
#     dilated_img = cv2.dilate(sharpen(image), np.ones((7, 7), np.uint8))
#     bg_img = cv2.medianBlur(dilated_img, 17)
#     #--- finding absolute difference to preserve edges ---
#     diff_img = 255 - cv2.absdiff(image, bg_img)
#     #--- normalizing between 0 to 255 ---
#     norm_img = cv2.normalize(diff_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
#     return cv2.threshold(norm_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

# def bb_intersection_over_union(boxA, boxB):
#     # determine the (x, y)-coordinates of the intersection rectangle
#     xA = max(boxA[0], boxB[0])
#     yA = max(boxA[2], boxB[2])
#     xB = min(boxA[1], boxB[1])
#     yB = min(boxA[3], boxB[3])
#     # compute the area of intersection rectangle
#     interArea = max(0, xB - xA ) * max(0, yB - yA )
#     # compute the area of both the prediction and ground-truth
#     # rectangles
#     boxAArea = (boxA[0] - boxA[1] ) * (boxA[2] - boxA[3] )
#     boxBArea = (boxB[0] - boxB[1] ) * (boxB[2] - boxB[3] )
#     # compute the intersection over union by taking the intersection
#     # area and dividing it by the sum of prediction + ground-truth
#     # areas - the interesection area
#     iou = interArea / float(boxAArea + boxBArea - interArea)
#     # return the intersection over union value
#     return iou, min(boxA[0], boxB[0]), min(boxA[2], boxB[2]), max(boxA[1], boxB[1]), max(boxA[3], boxB[3])

# def gettxtsize(text, font):
#     left, top, right, bottom = font.getbbox(text)
#     width = right - left
#     height = bottom - top
#     return width, height

# def text_wrap(text, font, max_width):
#     lines = []
#     # If the width of the text is smaller than image width
#     # we don't need to split it, just add it to the lines array
#     # and return
#     if gettxtsize(text, font)[0] <= max_width:
#         lines.append(text) 
#     else:
#         # split the line by spaces to get words
#         words = re.split(r'\W+', text)
#         i = 0
#         # append every word to a line while its width is shorter than image width
#         while i < len(words):
#             line = ''         
#             while i < len(words) and gettxtsize(line + words[i] + " ", font)[0] <= max_width:                
#                 line = line + words[i] + " "
#                 i += 1
#             if not line:
#                 line = words[i]
#                 i += 1
#             # when the line gets longer than the max width do not append the word, 
#             # add the line to the lines array
#             lines.append(line)    
#     return lines
 
 
# def draw_text(img,font, text, x, y, x_max, y_max):    
    
#     # size() returns a tuple of (width, height)
#     image_size = x_max - x
#     line_height = gettxtsize(text, font)[1] + 10
#     # create the ImageFont instance
#     #textSize = cv2.getTextSize(text=text, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, thickness=1)

#     # get shorter lines
#     lines = text_wrap(text,font, image_size)
#     #print(lines) # ['This could be a single line text ', 'but its too long to fit in one. ']
#     cv2.rectangle(img, (x, y), (x_max, y_max), (255, 255, 255), -1)
#     cv2.rectangle(img, (x, y), (x_max, y + (line_height*len(lines))), (255, 255, 255), -1)
#     add_text_img = Image.fromarray(img)
#     for line in lines:
#         # draw the line on the image
#         # cv2.putText(img,                        #image
#         #             line,                       #text
#         #             (x,y+(font*30)),                   #coordinates
#         #             cv2.FONT_HERSHEY_SIMPLEX,   #font
#         #             font,                          #font scale
#         #             (0,0,0),                    #font color
#         #             2                           #thickness
#         #             )
#         ImageDraw.Draw(add_text_img).text((x+5,y),line,font=font,fill=0)
        
#         # update the y position so that we can use it for next line
#         y = y + line_height
#     return np.array(add_text_img)

# def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
#     dim = None
#     (h, w) = image.shape[:2]

#     if width is None and height is None:
#         return image
#     if width is None:
#         r = height / float(h)
#         dim = (int(w * r), height)
#     else:
#         r = width / float(w)
#         dim = (width, int(h * r))

#     return cv2.resize(image, dim, interpolation=inter)

# def translate_jp(mocr, img):
#     return mocr(Image.fromarray(img))

# def init_jp_model(pretrained_model = 'lib\manga_ocr\manga-ocr-base', gpu = False):
#     return MangaOcr(pretrained_model, gpu)

# img = cv2.imread(r"C:\Users\ACER\Pictures\Doujinshi\Ganqing fanbook\_03.jpg",0)
# reader = easyocr.Reader(['ja'], gpu=False)
# bounds = reader.detect(sharpen(img), bbox_min_score = 0.01)
# #im = PIL.Image.open(r"C:\Users\ACER\Pictures\Doujinshi\Ganqing fanbook\_01.jpg")
# bboxes = []

# for i in bounds[0][0]:
#     try:
#         x_min = min(i[0],i[1])
#         y_min = min(i[2],i[3])
#         x_max = max(i[0],i[1])
#         y_max = max(i[2],i[3])
#         flag_overlap = False
#         for y in bboxes:
#             overlap = bb_intersection_over_union([x_min, x_max, y_min, y_max], y)
#             if(overlap[0]>0):
#                 flag_overlap = True
#                 x_min, y_min, x_max, y_max = overlap[1:]
#                 bboxes.remove(y)
#         bboxes.append([x_min, x_max, y_min, y_max])
#     except Exception as e:
#         print(e)

# bboxes=list(set(tuple(element) for element in bboxes))
# for bbox in bboxes:
#     for temp_bbox in bboxes:
#         print(bb_intersection_over_union(bbox, temp_bbox)[0])
#         iou = bb_intersection_over_union(bbox, temp_bbox)
#         if(iou[0]>=0.1 and iou[0]!=1.0):
#             if ((bbox[0] - bbox[1] ) * (bbox[2] - bbox[3])>=(temp_bbox[0] - temp_bbox[1]) * (temp_bbox[2] - temp_bbox[3])):
#                 bboxes.remove(temp_bbox)
#             else:
#                 bboxes.remove(bbox)
#     print("__________________________")

# #init MangaOCR
# mocr = init_jp_model()
# font = ImageFont.truetype(r"C:\Users\ACER\AI\translate\font\Roboto\Roboto-Regular.ttf",30)

# for j in bboxes:
#     try:
#         # print("pytesseract: \t\t"+pytesseract.image_to_string(preprocess(sharpen(((img[j[2]:j[3], j[0]:j[1]])))), lang = "chi_sim_vert+chi_sim").replace(" ", "").replace("\n", ""))
#         #print("mangaocr: \t\t"+ translate_jp(mocr, (preprocess(sharpen((img[j[2]:j[3], j[0]:j[1]]))))))
#         # print("translated pytesseract: "+translator.translate(pytesseract.image_to_string(preprocess(sharpen(((img[j[2]:j[3], j[0]:j[1]])))), lang = "chi_sim_vert+chi_sim").replace(" ", "").replace("\n", "")).text)
#         #print("translated mangaocr: "+ translator.translate(translate_jp(mocr, (preprocess(sharpen((img[j[2]:j[3], j[0]:j[1]])))))).text)
#         #print("_______________________________________________________________________________________")
        
#         #pytesseract
#         #print(j)
#         # translation = translator.translate(pytesseract.image_to_string(preprocess((((img[j[2]:j[3], j[0]:j[1]])))), lang = "chi_sim_vert+chi_sim").replace(" ", "").replace("\n", ""))
#         cv2.rectangle(img, (j[0], j[2]), (j[1], j[3]), (0, 0, 0), 2)
#         # print(f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})")
#         # img = draw_text(img,font, translation.text, j[0],j[2],j[1],j[3])
#         # cv2.imshow("Image", bilateral_filtering(img[j[2]:j[3], j[0]:j[1]]))
#         # # Wait for the user to press a key
#         # cv2.waitKey(0)

#         #MangaOCR
#         # get_text = (translate_jp(mocr, (preprocess(((img[j[2]:j[3], j[0]:j[1]])))))).replace(' ','').replace(';','...').replace(':',"...")
#         # translation = GoogleTranslator(source='auto', target='en').translate(get_text)
#         # print(get_text + "-->" + translation)
#         # #translation = translator.translate(get_text,dest='en')
#         # #print(f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})")
#         # img = draw_text(img,font, translation, j[0],j[2],j[1],j[3])
        
#     except Exception as e:
#         print(e)
#     # finally:
#         #cv2.rectangle(img, (j[0], j[2]), (j[1], j[3]), (0, 0, 255), 2)

# img = ResizeWithAspectRatio(img, height=700)
# cv2.imshow("Image", img)
    
#         # Wait for the user to press a key
# cv2.waitKey(0)