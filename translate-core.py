import easyocr
from googletrans import Translator, constants
import cv2 
import pytesseract
import numpy as np
#Calling API
reader = easyocr.Reader(['ch_sim'], gpu=False) # this needs to run only once to load the model into memory
# init the Google API translator
translator = Translator(service_urls=['translate.google.com'])
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

#thresholding
def thresholding(image):
    return cv2.threshold(image, 160, 255, cv2.THRESH_BINARY)[1]

def sharpen(image):
    kernel = np.array([[0, -1, 0], [-1, 7, -1], [0, -1, 0]]) 
    return cv2.filter2D(image, -1, kernel)

def blur(image):
    return cv2.GaussianBlur(image, (7, 7), 0) 

def contrast(image,brightness = 3, contrast=3):
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


root_image = cv2.imread(r"C:\Users\ACER\Pictures\Doujinshi\Ganqing fanbook\_01.jpg",0)
img = root_image
result = reader.detect(r"C:\Users\ACER\Pictures\Doujinshi\Ganqing fanbook\_01.jpg")
bboxes = []
for i in result[0][0]:
    try:
        x_min = i[0]
        y_min = i[2]
        x_max = i[1]
        y_max = i[3]
        flag_overlap = False
        for y in result[0][0]:
            overlap = bb_intersection_over_union([x_min, x_max, y_min, y_max], y)
            if(overlap[0]!=0.0):
                flag_overlap = True
                x_min, y_min, x_max, y_max = overlap[1:]
        bboxes.append([x_min, x_max, y_min, y_max])
        # overlap = [bb_intersection_over_union([x_min, x_max, y_min, y_max], y) for y in result[0][0]]
        # for iou_conf in overlap:
        #     if(iou_conf[0]>0.0 and iou_conf[0]<1.0):
        #         if(iou_conf[0] < min_iou_conf and iou_conf[0]!=0.0):
        #             min_iou_conf = iou_conf[0]
        #             print(iou_conf[1:])
        #             x_min, y_min, x_max, y_max = iou_conf[1:]
        # if(x_min<x_max and y_min<y_max):
            
        #     temp_img = img[y_min:y_max, x_min:x_max]
        #     #for y in reader.readtext(temp_img):
        #     #translation = translator.translate(pytesseract.image_to_string(temp_img, lang = "chi_sim_vert"))
        #     #print(f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})")
        #     cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)
            # cv2.imshow("Image", temp_img)
 
            # # Wait for the user to press a key
            # cv2.waitKey(0)
    except Exception as e:
        print(e)

for bbox in bboxes:
    for temp_bbox in  bboxes:
        if(bb_intersection_over_union(bbox, temp_bbox)[0] >= 1.0):
            bboxes.remove(temp_bbox)

for j in bboxes:
    try:
        temp_img = sharpen(thresholding(blur(root_image[j[2]:j[3], j[0]:j[1]])))
        translation = translator.translate(pytesseract.image_to_string(temp_img, lang = "chi_sim_vert+chi_sim").replace(" ", "").replace("\n", ""))
        print(f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})")
        cv2.rectangle(img, (j[0], j[2]), (j[1], j[3]), (0, 0, 255), 2)
        #cv2.imshow("Image", temp_img)
    
        # Wait for the user to press a key
        #cv2.waitKey(0)
    except Exception as e:
        print(e)

img = cv2.resize(img, None, fx = 0.4, fy = 0.4)
# Display the image
cv2.imshow("Image", img)
 
# Wait for the user to press a key
cv2.waitKey(0)
 
# Close all windows
cv2.destroyAllWindows()
