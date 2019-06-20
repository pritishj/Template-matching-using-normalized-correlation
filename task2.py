"""
Character Detection
(Due date: March 8th, 11: 59 P.M.)

The goal of this task is to experiment with template matching techniques. Specifically, the task is to find ALL of
the coordinates where a specific character appears using template matching.

There are 3 sub tasks:
1. Detect character 'a'.
2. Detect character 'b'.
3. Detect character 'c'.

You need to customize your own templates. The templates containing character 'a', 'b' and 'c' should be named as
'a.jpg', 'b.jpg', 'c.jpg' and stored in './data/' folder.

Please complete all the functions that are labelled with '# TODO'. Whem implementing the functions,
comment the lines 'raise NotImplementedError' instead of deleting them. The functions defined in utils.py
and the functions you implement in task1.py are of great help.

Hints: You might want to try using the edge detectors to detect edges in both the image and the template image,
and perform template matching using the outputs of edge detectors. Edges preserve shapes and sizes of characters,
which are important for template matching. Edges also eliminate the influence of colors and noises.

Do NOT modify the code provided.
Do NOT use any API provided by opencv (cv2) and numpy (np) in your code.
Do NOT import any library (function, module, etc.).
"""


import argparse
import json
import os


import utils
from task1 import read_image,convolve2d,edge_magnitude,prewitt_x,prewitt_y   # you could modify this line

char = ""

# Only downscales image s < 1
def resize(img,s):
    w = int(len(img[0])*s)
    h = int(len(img)*s)
    re= []
    for i in range(h):
        l=[]
        for j in range(w):
            l.append(img[int(i/s)][int(j/s)])
        re.append(l)
    return re

def parse_args():
    parser = argparse.ArgumentParser(description="cse 473/573 project 1.")
    parser.add_argument(
        "--img_path", type=str, default="./data/characters.jpg",
        help="path to the image used for character detection (do not change this arg)")
    parser.add_argument(
        "--template_path", type=str, default="",
        choices=["./data/a.jpg", "./data/b.jpg", "./data/c.jpg"],
        help="path to the template image")
    parser.add_argument(
        "--result_saving_directory", dest="rs_directory", type=str, default="./results/",
        help="directory to which results are saved (do not change this arg)")
    args = parser.parse_args()
    return args

def edges(img):
    img_x = convolve2d(img,prewitt_x)
    img_y = convolve2d(img,prewitt_y)
    return edge_magnitude(img_x,img_y)


def total(a):
    total =0
    for r in a:
        for c in r:
            total+=c
    return total

def mean(a):
    return  total(a)/(len(a)*len(a[0]))

def invert(img):
    for i in range(len(img)):
        for j in range(len(img[0])):
            img[i][j]=255-img[i][j]
    return img

def trans_img(img):
    for i in range(len(img)):
        for j in range(len(img[0])):
            img[i][j]=img[i][j]/255*127
    return img

def trans_template(img):
    for i in range(len(img)):
        for j in range(len(img[0])):
            img[i][j]=img[i][j]-127
    return img

def correlate(img, kernel):
    height = len(img)
    width= len(img[0])
    k_height = len(kernel)
    k_width = len(kernel[0])
    img_corr = []
    temp_mean = mean(kernel)
    temp_total = 0 
    for p in range(k_height):
        for q in range(k_width):
            temp_total += (kernel[p][q]-temp_mean)**2
    
    for i in range(height-k_height+1):
        row = []
        for j in range(width-k_width+1):
            c = utils.crop(img,i,i+k_height,j,j+k_width)
            c_mean = mean(c)
            c_total  = total = 0
            for p in range(k_height):
                for q in range(k_width):
                    c_total += (c[p][q]-c_mean)**2
                    total += (c[p][q]-c_mean)*(kernel[p][q]-temp_mean)
            if c_total == 0 or temp_total ==0:
                total = 0
            else:
                total = total/((c_total**0.5)*(temp_total**0.5))
            row.append(total)
        img_corr.append(row)
    #raise NotImplementedError
    return img_corr

    
def detect(img, template):
    """Detect a given character, i.e., the character in the template image.

    Args:s
        img: nested list (int), image that contains character to be detected.
        template: nested list (int), template image.

    Returns:
        coordinates: list (tuple), a list whose elements are coordinates where the character appears.
            format of the tuple: (x (int), y (int)), x and y are integers.
            x: row that the character appears (starts from 0).
            y: column that the character appears (starts from 0).
    """
    # TODO: implement this function.
    global char
    threshold = 0
    if char == 'a':
        threshold = 0.64
    elif char == 'b':
        threshold = 0.815
    elif char == 'c':
        threshold = 0.77
    img = trans_img(invert(img))
    template = trans_template(template)
    h=len(template)
    w=len(template[0])
    coordinates = []
    coor = correlate(img,template)
    for i in range(len(coor)):
        for j in range(len(coor[0])):
            if coor[i][j]>=threshold :
                is_rect = False
                for x,y in coordinates:
                    if (i>x and j>y) and (i<x+h and j<y+w):
                        is_rect = True
                if not is_rect:
                    coordinates.append((i,j))
    #raise NotImplementedError
    return coordinates


def save_results(coordinates, template, template_name, rs_directory):
    results = {}
    results["coordinates"] = sorted(coordinates, key=lambda x: x[0])
    results["templat_size"] = (len(template), len(template[0]))
    with open(os.path.join(rs_directory, template_name), "w") as file:
        json.dump(results, file)


def main():
    args = parse_args()

    img = read_image(args.img_path)
    template = read_image(args.template_path)
    global char
    char = args.template_path[::-1][4]

    coordinates = detect(img, template)
    
    template_name = "{}.json".format(os.path.splitext(os.path.split(args.template_path)[1])[0])
    save_results(coordinates, template, template_name, args.rs_directory)


if __name__ == "__main__":
    main()
    
