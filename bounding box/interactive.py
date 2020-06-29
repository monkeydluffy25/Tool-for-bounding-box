import cv2
import numpy as np
import glob
import pandas as pd
import os
import argparse

drawing = False 
mode = True
ix,iy = -1,-1
local_array=[]

def draw_rect(event,x,y,flags,param):
    global ix,iy,drawing,local_array,mode
    if event == cv2.EVENT_LBUTTONDOWN and mode==True:
        drawing = True
        ix,iy = x,y
#     elif event == cv2.EVENT_MOUSEMOVE:
#         if drawing == True:
#             cv2.rectangle(img,(ix,iy),(x,y),(0,0,255),3)
    elif event == cv2.EVENT_LBUTTONUP and mode==True:
        drawing = False
        cv2.rectangle(img,(ix,iy),(x,y),(0,0,255),3)
        local_array.append((ix,iy,x,y))
    
parser = argparse.ArgumentParser(description='Creating bounding box for Table returns csv')
parser.add_argument("-i", "--path", required=True,help="path to input folder")
args = vars(parser.parse_args())
path=args['path']
#path='/home/dhanush/images1/'
if not os.path.exists(path):
    print('enter proper file path')
else:
    if not os.path.isdir('%scsv/'%(path)):
        os.mkdir('%scsv/'%(path))
    images=glob.glob('%s*.jpg'%(path))
    ex=False
    for image in images:
        local_array=[]
        img=cv2.imread(image)
        cv2.namedWindow('image',cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('image',draw_rect)
        while(1):
            cv2.imshow('image',img)
            k = cv2.waitKey(1) & 0xFF
            if k == ord('r'): #reload
                img=cv2.imread(image)
                local_array=[]
            if k == ord('e'):
                mode = not mode
            if k == ord('q'): # quit
                #np.savetxt('/home/dhanush/images1/csv/%s.csv'%((image.split('/')[-1]).split('.')[0]),local_array,delimiter=',')
                pd.DataFrame(data=local_array,columns=['top_left-x','top_left-y','bottom_right-x','bottom_right-y']).to_csv('/home/dhanush/images1/csv/%s.csv'%((image.split('/')[-1]).split('.')[0]))
                break
            if k == ord('c'):
                ex=True
                break
        if ex:
            break
        cv2.destroyAllWindows()
