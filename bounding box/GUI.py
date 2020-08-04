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
        tk.Button(self, text="cancel",command=lambda: master.switch_frame(PageTwo)).pack()

class PageOne(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        global v1,v,v2,bounding_done,drawing,editing,mode,ix,iy,border_type,dic,undo,redo,img,path
        v1,v,v2=tk.BooleanVar(),tk.StringVar(),tk.StringVar()
        path = tk.filedialog.askopenfilename()
        bounding_done,drawing,editing,mode,ix,iy,border_type,dic,undo,redo=False,False,True,'rect',-1,-1,'bordered',\
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
        tk.Button(self, text="undo",command=self.undo_fun).pack()
        tk.Button(self, text="redo",command=self.redo_fun).pack()
        tk.Button(self, text="edit",command=self.function).pack()
        tk.Button(self, text="next",command=lambda: master.switch_frame(StartPage)).pack()
    def edit(self):
        global editing,v1
        editing=v1.get()
    def g(self):
        global v,mode,v2
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
                #img = cv2.line(img,(0,0),(511,511),(255,0,0),5)
                if(abs(x-dic['bounding_box'][-1][2])<=20):
                    dic['pics'].append(cv2.line(img,(ix,iy),(dic['bounding_box'][-1][2],iy),(0,0,255),3))
                    dic['hori'].append((ix,iy,dic['bounding_box'][-1][2],iy,'hori'))
                else:
                    dic['pics'].append(cv2.line(img,(ix,iy),(x,iy),(0,0,255),3))
                    dic['hori'].append((ix,iy,x,iy,'hori'))
                undo.append(copy.deepcopy(dic))
                
        if mode=='s_horizontal' and bounding_done==True:
            if event == cv2.EVENT_LBUTTONUP and editing==True:
                #drawing = False
                dic['pics'].append(cv2.line(img,(dic['bounding_box'][-1][0],y),(dic['bounding_box'][-1][2],y),(0,0,255),3))
                dic['hori'].append((dic['bounding_box'][-1][0],y,dic['bounding_box'][-1][2],y,'hori'))
                undo.append(copy.deepcopy(dic))
                
        if mode=='s_vertical' and bounding_done==True:
            if event == cv2.EVENT_LBUTTONUP and editing==True:
                #drawing = False
                dic['pics'].append(cv2.line(img,(x,dic['bounding_box'][-1][1]),(x,dic['bounding_box'][-1][3]),(0,0,255),3))
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
                    dic['pics'].append(cv2.line(img,(ix,iy),(ix,dic['bounding_box'][0][3]),(0,0,255),3))
                    dic['vert'].append((ix,iy,ix,dic['bounding_box'][0][3],'vert'))
                else:
                    dic['pics'].append(cv2.line(img,(ix,iy),(x,y),(0,0,255),3))
                    dic['vert'].append((ix,iy,ix,y,'vert'))
                undo.append(copy.deepcopy(dic))
        
    def function(self):
        global drawing,dic,mode,editing,bounding_done,img,border_type,path,undo,redo
        #dic['pics'].append(copy.deepcopy(img))
        cv2.namedWindow('image',cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('image',self.draw)             
        while(1):
            cv2.imshow('image',img)
            k = cv2.waitKey(1) & 0xFF
            if k == ord('r'): #reload
                img=cv2.imread(path)
            if k == ord('n'):
                self.save_csv()
            if k == ord('h'):
                if bounding_done:
                    mode='horizontal'
                #img=undo[-1]['pics'][-1]
            if k == ord('v'):
                if bounding_done:
                    mode='vertical'
            if k == ord('k'):
                if bounding_done:
                    mode='s_horizontal'
                #img=undo[-1]['pics'][-1]
            if k == ord('l'):
                if bounding_done:
                    mode='s_vertical'
            if k == ord('z'):
                try:
                    redo.append(undo.pop())
                    img=undo[-1]['pics'][-1]
                except:
                    img=cv2.imread(path)
            if k == ord('x'):
                try:
                    undo.append(redo.pop())
                    img=undo[-1]['pics'][-1]
                except:
                    img=undo[-1]['pics'][-1]
            if k == 27:
                print('edit: %s , border: %s, Type: %s'%(str(editing),border_type,mode))
            if k == ord('c'):
                break
        cv2.destroyAllWindows()
    def undo_fun(self):
        global undo,redo,img
        try:
            redo.append(undo.pop())
            img=undo[-1]['pics'][-1]
        except:
            img=cv2.imread(path)
    def redo_fun(self):
        global undo,redo,img
        try:
            undo.append(redo.pop())
            img=undo[-1]['pics'][-1]
        except:
            img=undo[-1]['pics'][-1]
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
    
class PageTwo(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Frame.configure(self,bg='red')
        tk.Label(self, text="Page two", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", pady=5)
        tk.Button(self, text="Go back to start page",command=lambda: master.switch_frame(StartPage)).pack()

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
