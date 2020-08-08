import pandas as pd
import numpy as np
from lxml import etree
import xml.etree.ElementTree as ET
import glob
import cv2
import argparse

parser = argparse.ArgumentParser(description='convert csv to Voc XML')
parser.add_argument("-i", "--path", required=True,help="path to input folder")
args = vars(parser.parse_args())
path=args['path']+'*.csv'
files=glob.glob(path)
for file in files:
    df = pd.read_csv(file)
    if (df.shape[0]==0):
        continue
    df = df[(df['border_type']=='bordered') | (df['border_type']=='unbordered')]
    img=cv2.imread(('/'.join(path.split('/')[:-2]))+'/images/'+(file.split('/')[-1]).split('.')[0]+'.jpg')
    height=img.shape[0]
    width=img.shape[1]
    depth = img.shape[2]

    annotation = ET.Element('annotation')
    ET.SubElement(annotation, 'folder').text = file.split('/')[-3]
    ET.SubElement(annotation, 'filename').text = (file.split('/')[-1]).split('.')[0]+'.jpg'
    ET.SubElement(annotation, 'segmented').text = '0'
    ET.SubElement(annotation, 'path').text = ('/'.join(path.split('/')[:-2]))+'/'+(file.split('/')[-1]).split('.')[0]+'.jpg'
    size = ET.SubElement(annotation, 'size')
    ET.SubElement(size, 'width').text = str(width)
    ET.SubElement(size, 'height').text = str(height)
    ET.SubElement(size, 'depth').text = str(depth)
    for i in range(df.shape[0]):
        ob = ET.SubElement(annotation, 'object')
        ET.SubElement(ob, 'name').text = str(df.iloc[i,5])
        ET.SubElement(ob, 'pose').text = 'Unspecified'
        ET.SubElement(ob, 'truncated').text = '0'
        ET.SubElement(ob, 'difficult').text = '0'
        bbox = ET.SubElement(ob, 'bndbox')
        ET.SubElement(bbox, 'xmin').text = str(df.iloc[i,1])
        ET.SubElement(bbox, 'ymin').text = str(df.iloc[i,2])
        ET.SubElement(bbox, 'xmax').text = str(df.iloc[i,3])
        ET.SubElement(bbox, 'ymax').text = str(df.iloc[i,4])

    fileName = (file.split('/')[-1]).split('.')[0]
    tree = ET.ElementTree(annotation)
    tree.write('%s'%('/'.join(file.split('/')[:-2]))+'/xml/'+fileName + ".xml", encoding='utf8')
