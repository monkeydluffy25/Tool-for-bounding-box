import cv2
import numpy as np
import glob
import pandas as pd
import os
import argparse
import copy

bounding_done=False
drawing = False 
editing= True
mode = 'rect'
ix,iy = -1,-1
dic={}
global img

def draw(event,x,y,flags,param):
    global ix,iy,drawing,dic,mode,editing,bounding_done,img
    if mode=='rect':
        if event == cv2.EVENT_LBUTTONDOWN and editing==True:
            drawing = True
            ix,iy = x,y
    #     elif event == cv2.EVENT_MOUSEMOVE:
    #         if drawing == True:
    #             cv2.rectangle(img,(ix,iy),(x,y),(0,0,255),3)
        elif event == cv2.EVENT_LBUTTONUP and editing==True:
            drawing = False
            dic['pics'].append(cv2.rectangle(img,(ix,iy),(x,y),(0,0,255),3))
            dic['bounding_box'].append((ix,iy,x,y))
            
    if mode=='horizontal' and bounding_done==True:
        if event == cv2.EVENT_LBUTTONDOWN and editing==True:
            drawing = True
            #ix,iy = x,y
            if(abs(x-dic['bounding_box'][-1][0])<=20):
                ix,iy=dic['bounding_box'][-1][0],y
            else:
                ix,iy=x,y
    #     elif event == cv2.EVENT_MOUSEMOVE:
    #         if drawing == True:
    #             cv2.rectangle(img,(ix,iy),(x,y),(0,0,255),3)
        elif event == cv2.EVENT_LBUTTONUP and editing==True:
            drawing = False
            #img = cv2.line(img,(0,0),(511,511),(255,0,0),5)
            if(abs(x-dic['bounding_box'][-1][2])<=20):
                dic['pics'].append(cv2.line(img,(ix,iy),(dic['bounding_box'][-1][2],iy),(0,0,255),3))
                dic['hori'].append((ix,iy,dic['bounding_box'][-1][2],iy))
            else:
                dic['pics'].append(cv2.line(img,(ix,iy),(x,iy),(0,0,255),3))
                dic['hori'].append((ix,iy,x,iy))
                
    if mode=='vertical' and bounding_done==True:
        if event == cv2.EVENT_LBUTTONDOWN and editing==True:
            drawing = True
            #ix,iy = x,y
            if(abs(y-dic['bounding_box'][-1][1])<=20):
                ix,iy=x,dic['bounding_box'][-1][1]
            else:
                ix,iy=x,y
    #     elif event == cv2.EVENT_MOUSEMOVE:
    #         if drawing == True:
    #             cv2.rectangle(img,(ix,iy),(x,y),(0,0,255),3)
        elif event == cv2.EVENT_LBUTTONUP and editing==True:
            drawing = False
            #img = cv2.line(img,(0,0),(511,511),(255,0,0),5)
            if(abs(y-dic['bounding_box'][0][3])<=20):
                dic['pics'].append(cv2.line(img,(ix,iy),(ix,dic['bounding_box'][0][3]),(0,0,255),3))
                dic['vert'].append((ix,iy,ix,dic['bounding_box'][0][3]))
            else:
                dic['pics'].append(cv2.line(img,(ix,iy),(x,y),(0,0,255),3))
                dic['vert'].append((ix,iy,ix,y))
    
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
        bounding_done=False
        undo,redo=[],[]
        dic={'pics':[],'vert':[],'hori':[],'bounding_box':[]}
        img=cv2.imread(image)
        dic['pics'].append(copy.deepcopy(img))
        cv2.namedWindow('image',cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('image',draw)
        while(1):
            cv2.imshow('image',img)
            k = cv2.waitKey(1) & 0xFF
            if k == ord('r'): #reload
                img=cv2.imread(image)
                dic={'pics':[],'vert':[],'hori':[],'bounding_box':[]}
            if k == ord('e'):
                editing = not editing 
            if k == ord('s'): # quit
                #np.savetxt('/home/dhanush/images1/csv/%s.csv'%((image.split('/')[-1]).split('.')[0]),local_array,delimiter=',')
                if not bounding_done:
                    pd.DataFrame(data=dic['bounding_box'],columns=['top_left-x','top_left-y','bottom_right-x','bottom_right-y']).to_csv('/home/dhanush/images1/csv/%s.csv'%((image.split('/')[-1]).split('.')[0]))
                    undo.append(copy.deepcopy(dic))
                    bounding_done=True
                else:
                    if ((undo[-1]['pics'][-1]-dic['pics'][-1]).any()):
                        undo.append(copy.deepcopy(dic))
            if k == ord('h'):
                if bounding_done:
                    mode='horizontal'
            if k == ord('v'):
                if bounding_done:
                    mode='vertical'
            if k == ord('z'):
                try:
                    redo.append(undo.pop())
                    img=undo[-1]['pics'][-1]
                except:
                    img=cv2.imread(image)
            if k == ord('x'):
                try:
                    undo.append(redo.pop())
                    img=undo[-1]['pics'][-1]
                except:
                    img=undo[-1]['pics'][-1]
            if k == ord('c'):
                ex=True
                break
            if k == ord('n'):
                break
        if ex:
            break
        cv2.destroyAllWindows()
