from PIL import Image
from PIL import ImageTk
import tkinter as tk
from tkinter import filedialog
import cv2
import numpy as np
import glob
import pandas as pd
import os
import argparse
import copy

def skew_correction(path):
    image=cv2.imread(path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h),flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated
def cont_table(img):
    heights,widths=[],[]
    table_image=img
    table_imageforpro=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh_value = cv2.adaptiveThreshold(table_imageforpro,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,25,1)
    close_k=cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    close_img=cv2.morphologyEx(cv2.bitwise_not(thresh_value),cv2.MORPH_CLOSE,close_k)
    contours, hierarchy = cv2.findContours(close_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        heights.append(h)
        widths.append(w)
        table_image = cv2.rectangle(table_image, (x, y), (x + w, y + h), (0, 0, 255), 1)
    return table_image,heights,widths
import matplotlib.pyplot as plt
def disp(img):
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.imshow('image',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
def horizontal_lines(path,thresh_s,w_size,img2):
    hori=[]
    img=cv2.imread(path)
    img1=img2
    img=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ad_thresh=cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,thresh_s,1)
    open_k=cv2.getStructuringElement(cv2.MORPH_RECT,(w_size+4,1))
    open_img=cv2.morphologyEx(cv2.bitwise_not(ad_thresh),cv2.MORPH_OPEN,open_k)
    c_img=cv2.morphologyEx(open_img,cv2.MORPH_CLOSE,(1,1))
    minLineLength = 3*w_size
    maxLineGap = 100*w_size
    lines = cv2.HoughLinesP(c_img,1,np.pi/180,3*w_size,minLineLength,maxLineGap)
    if lines is None:
        return None
    count=0
    for line in lines:
        for x1,y1,x2,y2 in line:
            cv2.line(img1,(x1,y1),(x2,y2),(0,0,255),2)
            if(x1>x2):
                count=count+1
            hori.append((x1,y1,x2,y2))
    disp(img1)
    return hori
def vertical_lines(path,thresh_s,h_size):
    vert=[]
    img=cv2.imread(path)
    img1=cv2.imread(path)
    img=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ad_thresh=cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,thresh_s,1)
    open_k=cv2.getStructuringElement(cv2.MORPH_RECT,(1,h_size+4))
    open_img=cv2.morphologyEx(cv2.bitwise_not(ad_thresh),cv2.MORPH_OPEN,open_k)
    c_img=cv2.morphologyEx(open_img,cv2.MORPH_CLOSE,(1,1))
    minLineLength = 3*h_size
    maxLineGap = 4*h_size
    lines = cv2.HoughLinesP(c_img,1,np.pi/180,3*h_size,minLineLength,maxLineGap)
    if lines is None:
        return None
    count=0
    for line in lines:
        for x1,y1,x2,y2 in line:
            cv2.line(img1,(x1,y1),(x2,y2),(0,0,255),1)
            if(y1>y2):
                count=count+1
            vert.append((x1,y1,x2,y2))
    return vert,img1
from sys import maxsize
mi,ma=-maxsize,maxsize
from statistics import mean,mode,median
def lines(path):
    dic,vert,hori={},[],[]
    img,h,w=cont_table(skew_correction(path))
    dic[0],dic[1]=int(median(w)),int(median(h))
    dic[2]=max(dic[0],dic[1])+2
    for i in dic:
        if dic[i]%2==0:
            dic[i]=dic[i]+1
    try:
        vert,img2=vertical_lines(path,dic[2],dic[1])
    except:
        img2=cv2.imread(path)
    hori=horizontal_lines(path,dic[2],dic[0],img2)
    return hori,vert    

class SampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(StartPage)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

class StartPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Select image for editing", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", pady=5)
        tk.Button(self, text="Select image",command=lambda: master.switch_frame(PageOne)).pack()

class PageOne(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        global v1,v,v2,bounding_done,drawing,editing,mode,ix,iy,border_type,dic,undo,redo,img,path,e_hori,e_vert
        v1,v,v2=tk.BooleanVar(),tk.StringVar(),tk.StringVar()
        path = tk.filedialog.askopenfilename()
        bounding_done,drawing,editing,mode,ix,iy,dic,undo,redo=False,False,False,'rect',-1,-1,\
        {'pics':[],'vert':[],'hori':[],'bounding_box':[]},[],[]
        img=cv2.imread(path)
        tk.Radiobutton(self, text='rect', variable=v, value='rect',command=self.g).pack(side=tk.LEFT) 
        tk.Radiobutton(self, text='drag_vertical', variable=v, value='vertical',command=self.g).pack(side=tk.LEFT)
        tk.Radiobutton(self, text='drag_horizontal', variable=v, value='horizontal',command=self.g).pack(side=tk.LEFT)
        tk.Radiobutton(self, text='click_horizontal', variable=v, value='s_horizontal',command=self.g).pack(side=tk.LEFT)
        tk.Radiobutton(self, text='click_vertical', variable=v, value='s_vertical',command=self.g).pack(side=tk.LEFT)
        tk.Checkbutton(self, text='editing', variable=v1,command=self.edit).pack(side=tk.LEFT)
        tk.Radiobutton(self, text='bordered', variable=v2, value="bordered",command=self.g).pack(side=tk.LEFT)
        tk.Radiobutton(self, text='unbordered', variable=v2, value="unbordered",command=self.g).pack(side=tk.LEFT)
        e_hori,e_vert=lines(path)
        tk.Button(self, text="export",command=self.export_csv).pack()
        tk.Button(self, text="undo",command=self.undo_fun).pack()
        tk.Button(self, text="redo",command=self.redo_fun).pack()
        tk.Button(self, text="edit",command=self.function).pack()
        tk.Button(self, text="next",command=lambda: master.switch_frame(StartPage)).pack()
    def export_csv(self):
        global e_hori,e_vert,path
        if(len(e_hori)==0 or len(e_vert)==0):
            print('nothing to save')
        else:
            df1=pd.DataFrame(data=e_vert,columns=['x1','y1','x2','y2'])
            df1['type']='vert'
            df2=pd.DataFrame(data=e_hori,columns=['x1','y1','x2','y2'])
            df2['type']='hori'
            df=df1.append(df2,ignore_index = True)
            df.to_csv('%s/exported_csv/%s.csv'%('/'.join(path.split('/')[:-1]),(path.split('/')[-1]).split('.')[0]))
    def edit(self):
        global editing,v1
        editing=v1.get()
    def g(self):
        global v,mode,v2,border_type
        mode=v.get()
        border_type=v2.get()
    def draw(self,event,x,y,flags,param):
        global ix,iy,drawing,dic,mode,editing,bounding_done,img,border,border_type,undo
        if mode=='rect':
            if event == cv2.EVENT_LBUTTONDOWN and editing==True:
                drawing = True
                ix,iy = x,y

            elif event == cv2.EVENT_LBUTTONUP and editing==True:
                drawing = False
                dic['pics'].append(cv2.rectangle(img,(ix,iy),(x,y),(0,0,255),3))
                dic['bounding_box'].append((ix,iy,x,y,border_type))
                undo.append(copy.deepcopy(dic))
                bounding_done=True

        if mode=='horizontal' and bounding_done==True:
            if event == cv2.EVENT_LBUTTONDOWN and editing==True:
                drawing = True
                #ix,iy = x,y
                if(abs(x-dic['bounding_box'][-1][0])<=20):
                    ix,iy=dic['bounding_box'][-1][0],y
                else:
                    ix,iy=x,y

            elif event == cv2.EVENT_LBUTTONUP and editing==True:
                drawing = False
                if(abs(x-dic['bounding_box'][-1][2])<=20):
                    dic['pics'].append(cv2.line(img,(ix,iy),(dic['bounding_box'][-1][2],iy),(0,0,255),2))
                    dic['hori'].append((ix,iy,dic['bounding_box'][-1][2],iy,'hori'))
                else:
                    dic['pics'].append(cv2.line(img,(ix,iy),(x,iy),(0,0,255),3))
                    dic['hori'].append((ix,iy,x,iy,'hori'))
                undo.append(copy.deepcopy(dic))
                
        if mode=='s_horizontal' and bounding_done==True:
            if event == cv2.EVENT_LBUTTONUP and editing==True:
                dic['pics'].append(cv2.line(img,(dic['bounding_box'][-1][0],y),(dic['bounding_box'][-1][2],y),(0,0,255),2))
                dic['hori'].append((dic['bounding_box'][-1][0],y,dic['bounding_box'][-1][2],y,'hori'))
                undo.append(copy.deepcopy(dic))
                
        if mode=='s_vertical' and bounding_done==True:
            if event == cv2.EVENT_LBUTTONUP and editing==True:
                dic['pics'].append(cv2.line(img,(x,dic['bounding_box'][-1][1]),(x,dic['bounding_box'][-1][3]),(0,0,255),2))
                dic['vert'].append((x,dic['bounding_box'][-1][1],x,dic['bounding_box'][-1][3],'vert'))
                undo.append(copy.deepcopy(dic))

        if mode=='vertical' and bounding_done==True:
            if event == cv2.EVENT_LBUTTONDOWN and editing==True:
                drawing = True
                #ix,iy = x,y
                if(abs(y-dic['bounding_box'][-1][1])<=20):
                    ix,iy=x,dic['bounding_box'][-1][1]
                else:
                    ix,iy=x,y

            elif event == cv2.EVENT_LBUTTONUP and editing==True:
                drawing = False
                #img = cv2.line(img,(0,0),(511,511),(255,0,0),5)
                if(abs(y-dic['bounding_box'][0][3])<=20):
                    dic['pics'].append(cv2.line(img,(ix,iy),(ix,dic['bounding_box'][0][3]),(0,0,255),2))
                    dic['vert'].append((ix,iy,ix,dic['bounding_box'][0][3],'vert'))
                else:
                    dic['pics'].append(cv2.line(img,(ix,iy),(x,y),(0,0,255),3))
                    dic['vert'].append((ix,iy,ix,y,'vert'))
                undo.append(copy.deepcopy(dic))
        
    def function(self):
        global drawing,dic,mode,editing,bounding_done,img,border_type,path,undo,redo
        cv2.namedWindow('%s'%(path.split('/')[-1]),cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('%s'%(path.split('/')[-1]),self.draw)             
        while(1):
            cv2.imshow('%s'%(path.split('/')[-1]),img)
            k = cv2.waitKey(1) & 0xFF
            if k == ord('r'): #reload
                img=cv2.imread(path)
            if k == ord('n'):
                self.save_csv()
            if k == ord('e'):
                editing = not editing
            if k == ord('h'):
                if bounding_done:
                    mode='horizontal'
            if k == ord('v'):
                if bounding_done:
                    mode='vertical'
            if k == ord('k'):
                if bounding_done:
                    mode='s_horizontal'
            if k == ord('l'):
                if bounding_done:
                    mode='s_vertical'
            if k == ord('z'):
                try:
                    redo.append(undo.pop())
                    img=undo[-1]['pics'][-1]
                    dic=undo[-1]
                except:
                    img=cv2.imread(path)
                    dic={'pics':[],'vert':[],'hori':[],'bounding_box':[]}
            if k == ord('x'):
                try:
                    undo.append(redo.pop())
                    img=undo[-1]['pics'][-1]
                    dic=undo[-1]
                except:
                    img=undo[-1]['pics'][-1]
                    dic=undo[-1]
            if k == 27:
                print('edit: %s , border: %s, Type: %s'%(str(editing),border_type,mode))
            if k == ord('c'):
                break
            if k == ord('b'):
                mode='rect'
        cv2.destroyAllWindows()
    def undo_fun(self):
        global undo,redo,img
        try:
            redo.append(undo.pop())
            img=undo[-1]['pics'][-1]
            dic=undo[-1]
        except:
            img=cv2.imread(path)
            dic={'pics':[],'vert':[],'hori':[],'bounding_box':[]}
            
    def redo_fun(self):
        global undo,redo,img
        try:
            undo.append(redo.pop())
            img=undo[-1]['pics'][-1]
            dic=undo[-1]
        except:
            img=undo[-1]['pics'][-1]
            dic=undo[-1]
    def save_csv(self):
        global undo,path
        if(len(undo)==0):
            print('nothing to save')
        else:
            df=pd.DataFrame(data=undo[-1]['bounding_box'],columns=['top_left-x','top_left-y','bottom_right-x','bottom_right-y','border_type'])
            df1=pd.DataFrame(data=undo[-1]['hori'],columns=['top_left-x','top_left-y','bottom_right-x','bottom_right-y','border_type'])
            df2=pd.DataFrame(data=undo[-1]['vert'],columns=['top_left-x','top_left-y','bottom_right-x','bottom_right-y','border_type'])
            df=df.append(df1,ignore_index = True)
            df=df.append(df2,ignore_index = True)
            df.to_csv('%s/csv/%s.csv'%('/'.join(path.split('/')[:-1]),(path.split('/')[-1]).split('.')[0]))
    
if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
