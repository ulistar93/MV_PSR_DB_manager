#https://github.com/Tony607/voc2coco/blob/master/COCO_Image_Viewer.ipynb
# https://blog.paperspace.com/train-yolov5-custom-data/

from distutils.log import info
#import webview
#import IPython
import os
import json
import random
import numpy as np
import requests
from io import BytesIO
from math import trunc
from PIL import Image as PILImage
from PIL import ImageDraw as PILImageDraw
import cv2
import glob
import pdb

# Dictionary that maps class names to IDs
#class_name_to_id_mapping = {"Cigarette": 0,
#                           "E_Cigarette": 1,
#                           }
#class_name_to_id_mapping = {"bottle": 0,
#                            "cup": 1,
#                            "cell phone": 2,
#                            }
class_name_to_id_mapping = {"cell phone": 0}


# Load the dataset json
class CocoDataset():
    def __init__(self, annotation_path, image_dir, loadOption = 'r'):
        self.annotation_path = annotation_path
        self.image_dir = image_dir
        self.colors = ['blue', 'purple', 'red', 'green', 'orange', 'salmon', 'pink', 'gold',
                       'orchid', 'slateblue', 'limegreen', 'seagreen', 'darkgreen', 'olive',
                       'teal', 'aquamarine', 'steelblue', 'powderblue', 'dodgerblue', 'navy',
                       'magenta', 'sienna', 'maroon']
        if loadOption == 'r':
            # print(self.annotation_path)
            json_file = open(self.annotation_path)
            self.json_dict = json.load(json_file)
            json_file.close()

            self.process_info()
            self.process_licenses()
            self.process_categories()
            self.process_images()
            self.process_segmentations()

        elif loadOption == 'w':
            pass
    def rm_json_dict(self, image_id):
        for idx, dict in enumerate(self.json_dict['images']):
            if self.json_dict['images'][idx]['id'] == image_id:
                print("dict {} will be deleted".format(self.json_dict['images'][idx]))
                del(self.json_dict['images'][idx])

        for idx, dict in enumerate(self.json_dict['annotations']):
            if self.json_dict['annotations'][idx]['image_id'] == image_id:
                print("dict {} will be deleted".format(self.json_dict['annotations'][idx]))
                del(self.json_dict['annotations'][idx])


    def get_image_format(self, image_id):
        image = self.images[image_id]
        image_path = os.path.join(self.image_dir, image['file_name'])
        if not os.path.isfile(image_path):
            return -1
        image = PILImage.open(image_path)
        fmt = image.format
        return fmt

    def display_info(self):
        print('Dataset Info:')
        print('=============')
        if self.info is None:
            return
        for key, item in self.info.items():
            print('  {}: {}'.format(key, item))

        requirements = [['description', str],
                        ['url', str],
                        ['version', str],
                        ['year', str],
                        ['contributor', str],
                        ['date_created', int]]
        for req, req_type in requirements:
            if req not in self.info:
                print('ERROR: {} is missing'.format(req))
            elif type(self.info[req]) != req_type:
                print('ERROR: {} should be type {}'.format(req, str(req_type)))
        print('')

    def display_licenses(self):
        print('Licenses:')
        print('=========')

        if self.licenses is None:
            return
        requirements = [['id', int],
                        ['url', str],
                        ['name', str]]
        for license in self.licenses:
            for key, item in license.items():
                print('  {}: {}'.format(key, item))
            for req, req_type in requirements:
                if req not in license:
                    print('ERROR: {} is missing'.format(req))
                elif type(license[req]) != req_type:
                    print('ERROR: {} should be type {}'.format(
                        req, str(req_type)))
            print('')
        print('')

    def display_categories(self):
        print('Categories:')
        print('=========')
        for sc_key, sc_val in self.super_categories.items():
            print('  super_category: {}'.format(sc_key))
            for cat_id in sc_val:
                print('    id {}: {}'.format(
                    cat_id, self.categories[cat_id]['name']))
            print('')

    def display_image_cv2(self, image_id, show_polys=True, show_bbox=True, show_crowds=True, use_url=False):
        print('Image:')
        print('======')

        if image_id == 'random':
            image_id = random.choice(list(self.images.keys()))

        # Print the image info
        image = self.images[image_id]
        for key, val in image.items():
            print('  {}: {}'.format(key, val))

        # Open the image
        if use_url:
            image_path = image['coco_url']
            # response = requests.get(image_path)
            # image = PILImage.open(BytesIO(response.content))

        else:
            image_path = os.path.join(self.image_dir, image['file_name'])
            # image = PILImage.open(image_path)


        # Calculate the size and adjusted display size
        # print('  segmentations ({}):'.format(
        #     len(self.segmentations[image_id])))
        # print(self.segmentations[1])

        mat = cv2.imread(image_path)

        if show_polys:
            pass
        if show_crowds:
            pass

        if show_bbox:
            if image_id in self.segmentations:
                for i, segm in enumerate(self.segmentations[image_id]):
                    bbox = list(map(int, segm['bbox']))
                    color = (255, 0, 255)
                    category_id = segm['category_id']

                    category = self.categories[category_id]

                    text = "%s" % (category['name'])
                    cv2.rectangle(mat, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), color, 4)
                    cv2.putText(mat, text, (bbox[0], bbox[1] - 5), cv2.FONT_HERSHEY_SIMPLEX,
                                0.25, color, 1)

        cv2.namedWindow('image', flags=cv2.WINDOW_NORMAL)
        cv2.imshow('image', mat)

        cv2.waitKey(0)

    def display_image(self, image_id, show_polys=True, show_bbox=True, show_crowds=True, use_url=False):
        print('Image:')
        print('======')
        if image_id == 'random':
            image_id = random.choice(list(self.images.keys()))

        # Print the image info
        image = self.images[image_id]
        for key, val in image.items():
            print('  {}: {}'.format(key, val))

        # Open the image
        if use_url:
            image_path = image['coco_url']
            response = requests.get(image_path)
            image = PILImage.open(BytesIO(response.content))

        else:
            image_path = os.path.join(self.image_dir, image['file_name'])
            # print("DEBUG image_path : ",image_path)
            image = PILImage.open(image_path)
            fileName = image_path.split('/')[-1]
            print("image file name : ", fileName)
            # image.show()

        # Calculate the size and adjusted display size
        max_width = 600
        image_width, image_height = image.size
        adjusted_width = min(image_width, max_width)
        adjusted_ratio = adjusted_width / image_width
        adjusted_height = adjusted_ratio * image_height

        # Create list of polygons to be drawn
        polygons = {}
        bbox_polygons = {}
        rle_regions = {}
        poly_colors = {}
        bbox_categories = {}
        print('  segmentations ({}):'.format(
            len(self.segmentations[image_id])))
        for i, segm in enumerate(self.segmentations[image_id]):
            polygons_list = []
            if segm['iscrowd'] != 0:
                # Gotta decode the RLE
                px = 0
                x, y = 0, 0
                rle_list = []
                for j, counts in enumerate(segm['segmentation']['counts']):
                    if j % 2 == 0:
                        # Empty pixels
                        px += counts
                    else:
                        # Need to draw on these pixels, since we are drawing in vector form,
                        # we need to draw horizontal lines on the image
                        x_start = trunc(
                            trunc(px / image_height) * adjusted_ratio)
                        y_start = trunc(px % image_height * adjusted_ratio)
                        px += counts
                        x_end = trunc(trunc(px / image_height)
                                      * adjusted_ratio)
                        y_end = trunc(px % image_height * adjusted_ratio)
                        if x_end == x_start:
                            # This is only on one line
                            rle_list.append(
                                {'x': x_start, 'y': y_start, 'width': 1, 'height': (y_end - y_start)})
                        if x_end > x_start:
                            # This spans more than one line
                            # Insert top line first
                            rle_list.append(
                                {'x': x_start, 'y': y_start, 'width': 1, 'height': (image_height - y_start)})

                            # Insert middle lines if needed
                            lines_spanned = x_end - x_start + 1  # total number of lines spanned
                            full_lines_to_insert = lines_spanned - 2
                            if full_lines_to_insert > 0:
                                full_lines_to_insert = trunc(
                                    full_lines_to_insert * adjusted_ratio)
                                rle_list.append(
                                    {'x': (x_start + 1), 'y': 0, 'width': full_lines_to_insert, 'height': image_height})

                            # Insert bottom line
                            rle_list.append(
                                {'x': x_end, 'y': 0, 'width': 1, 'height': y_end})
                if len(rle_list) > 0:
                    rle_regions[segm['id']] = rle_list
            else:
                # Add the polygon segmentation
                for segmentation_points in segm['segmentation']:
                    segmentation_points = np.multiply(
                        segmentation_points, adjusted_ratio).astype(int)
                    polygons_list.append(
                        str(segmentation_points).lstrip('[').rstrip(']'))
            polygons[segm['id']] = polygons_list
            if i < len(self.colors):
                poly_colors[segm['id']] = self.colors[i]
            else:
                poly_colors[segm['id']] = 'white'

            bbox = segm['bbox']
            bbox_points = [bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1],
                           bbox[0] + bbox[2], bbox[1] +
                           bbox[3], bbox[0], bbox[1] + bbox[3],
                           bbox[0], bbox[1]]
            bbox_points = np.multiply(bbox_points, adjusted_ratio).astype(int)
            bbox_polygons[segm['id']] = str(
                bbox_points).lstrip('[').rstrip(']')
            bbox_categories[segm['id']] = self.categories[segm['category_id']]
            # Print details
            print('    {}:{}:{}'.format(
                segm['id'], poly_colors[segm['id']], self.categories[segm['category_id']]))
        # print("DEBUG image_path: ", image_path)
        # Draw segmentation polygons on image
        # html = "<h1>ga<h1>"
        html = '<div class="container" style="position:relative;">'
        html += '<img src="{}" style="position:relative;top:0px;left:0px;width:{}px;">'.format(
            image_path, adjusted_width)
        html += '<div class="svgclass"><svg width="{}" height="{}">'.format(
            adjusted_width, adjusted_height)

        if show_polys:
            for seg_id, points_list in polygons.items():
                fill_color = poly_colors[seg_id]
                stroke_color = poly_colors[seg_id]
                for points in points_list:
                    html += '<polygon points="{}" style="fill:{}; stroke:{}; stroke-width:1; fill-opacity:0.5" />'.format(
                        points, fill_color, stroke_color)

        if show_crowds:
            for seg_id, rect_list in rle_regions.items():
                fill_color = poly_colors[seg_id]
                stroke_color = poly_colors[seg_id]
                for rect_def in rect_list:
                    x, y = rect_def['x'], rect_def['y']
                    w, h = rect_def['width'], rect_def['height']
                    html += '<rect x="{}" y="{}" width="{}" height="{}" style="fill:{}; stroke:{}; stroke-width:1; fill-opacity:0.5; stroke-opacity:0.5" />'.format(
                        x, y, w, h, fill_color, stroke_color)

        if show_bbox:
            for seg_id, points in bbox_polygons.items():
                x, y = [int(i) for i in points.split()[:2]]
                html += '<text x="{}" y="{}" fill="yellow">{}</text>'.format(
                    x, y, bbox_categories[seg_id]["name"])
                fill_color = poly_colors[seg_id]
                stroke_color = poly_colors[seg_id]
                html += '<polygon points="{}" style="fill:{}; stroke:{}; stroke-width:1; fill-opacity:0" />'.format(
                    points, fill_color, stroke_color)

        html += '</svg></div>'
        html += '</div>'
        html += '<style>'
        html += '.svgclass { position:absolute; top:0px; left:0px;}'
        html += '</style>'
        return html



    def process_info(self):
        self.info = self.json_dict.get('info')

    def process_licenses(self):
        self.licenses = self.json_dict.get('licenses')

    def process_categories(self):
        self.categories = {}
        self.super_categories = {}
        for category in self.json_dict['categories']:
            cat_id = category['id']
            super_category = category['supercategory']

            # Add category to the categories dict
            if cat_id not in self.categories:
                self.categories[cat_id] = category
            else:
                print("ERROR: Skipping duplicate category id: {}".format(category))

            # Add category to super_categories dict
            if super_category not in self.super_categories:
                # Create a new set with the category id
                self.super_categories[super_category] = {cat_id}
            else:
                self.super_categories[super_category] |= {
                    cat_id}  # Add category id to the set

    def process_images(self):
        self.images = {}
        for image in self.json_dict['images']:
            image_id = image['id']
            if image_id in self.images:
                print("ERROR: Skipping duplicate image id: {}".format(image))
            else:
                self.images[image_id] = image

    def printSelfDict(self):
        print("selfCOCO\n",type(self.json_dict))

    def process_segmentations(self):
        self.segmentations = {}
        for segmentation in self.json_dict['annotations']:
            image_id = segmentation['image_id']
            if image_id not in self.segmentations:
                self.segmentations[image_id] = []
            self.segmentations[image_id].append(segmentation)

        # print("process_segmentations")
        # print(self.segmentations[0])

    def find_image_id(self, fileName):
        for image_id in list(self.images.keys()):
            if fileName == self.images[image_id]["file_name"]:
                print("image_id of {} is {}".format(fileName, image_id))


    def extract_COCO_to_info_dict(self, image_id):
        print('extract_COCO:')
        print('======')
        info_dict = {}
        info_dict['bboxes'] = []

        image = self.images[image_id]
        for key, val in image.items():
            print('  {}: {}'.format(key, val))

        info_dict['filename'] = image["file_name"]
        info_dict['image_size'] = (image["width"], image["height"], 3)
        # print("asf", self.segmentations[image_id])
        for i, segm in enumerate(self.segmentations[image_id]):
            bbox = segm['bbox']
            bbox_dict = {}
            #pdb.set_trace()
            bbox_dict["class"] = self.categories[segm['category_id']]['name']
            bbox_dict["xmin"] = bbox[0]
            bbox_dict["ymin"] = bbox[1]
            bbox_dict["width"] = bbox[2]
            bbox_dict["height"] = bbox[3]
            info_dict['bboxes'].append(bbox_dict)

        return info_dict

    def rm_file(self, image_id):
        image = self.images[image_id]
        image_path = os.path.join(self.image_dir, image['file_name'])

        if os.path.isfile(image_path):
            os.remove(image_path)
            print("removed the file {}", image_path)
        # print(self.segmentations[image_id])
        # if image_id in self.images:
        #     del(self.images[image_id])
        # if image_id in self.segmentations:
        #     del(self.segmentations[image_id])

    def convert_to_yolov5(self, info_dict, annotation_path):
        print_buffer = []

        # For each bounding box
        for b in info_dict["bboxes"]:
            try:
                class_id = class_name_to_id_mapping[b["class"]]
            except KeyError:
                print("Invalid Class. Must be one from ", class_name_to_id_mapping.keys())

            # Transform the bbox co-ordinates as per the format required by YOLO v5
            # b_center_x = (b["xmin"] + b["xmax"]) / 2 
            # b_center_y = (b["ymin"] + b["ymax"]) / 2
            # b_width    = (b["xmax"] - b["xmin"])
            # b_height   = (b["ymax"] - b["ymin"])

            b_center_x = b["xmin"] + b["width"] / 2
            b_center_y = b["ymin"] + b["height"] / 2
            b_width    = b["width"]
            b_height   = b["height"]

            # Normalise the co-ordinates by the dimensions of the image
            image_w, image_h, image_c = info_dict["image_size"]
            b_center_x /= image_w
            b_center_y /= image_h
            b_width    /= image_w
            b_height   /= image_h

            #Write the bbox details to the file 
            print_buffer.append("{} {:.3f} {:.3f} {:.3f} {:.3f}".format(class_id, b_center_x, b_center_y, b_width, b_height))

        # Name of the file which we have to save 
        fileName = info_dict["filename"]
        extension = fileName.split('.')[-1]
        # print(extension)
        save_file_name = os.path.join(annotation_path, info_dict["filename"].replace(extension, "txt"))

        # Save the annotation to disk
        print("\n".join(print_buffer), file= open(save_file_name, "w"))
    def save_json_dict(self, annotation_dir, file_name):
        os.makedirs(annotation_dir, exist_ok = True)


        with open(annotation_dir + file_name, "w") as json_fp:
            json_str = json.dumps(self.json_dict)
            json_fp.write(json_str)

def displayCOCOimage():
    annotation_path = '../datasets/COCO17_PCB/'
    annotation_fileName = "coco_pho_cup_bottle.json"
    image_dir = '../datasets/COCO17_PCB'

    #annotation_path = '../../Datasets/Smoking/'
    #annotation_fileName = "out.json"
    #image_dir = '../../Datasets/Smoking/images'


    # annotation_path = './annotation_out/'
    # annotation_fileName = "out.json"
    # image_dir = './images/'

    # annotation_path = '../../Datasets/Smoking/annotations/'
    # annotation_fileName = "instances_smoking_training.json"
    # image_dir = '../../Datasets/Smoking/training_data/images'

    data_type = "training"
    coco_dataset = CocoDataset(annotation_path + annotation_fileName, image_dir)

    coco_dataset.display_info()
    coco_dataset.display_licenses()
    coco_dataset.display_categories()
    coco_dataset.printSelfDict()

    for image_id in list(coco_dataset.images.keys()):

        coco_dataset.display_image_cv2(image_id, use_url=False, show_polys=False, show_bbox = True, show_crowds = False)

def gif_filter_main():
    annotation_path = '../../Datasets/Smoking/annotations/'
    annotation_fileName = "instances_smoking_test.json"
    image_dir = '../../Datasets/Smoking/testing_data'
    data_type = "training"
    coco_dataset = CocoDataset(annotation_path + annotation_fileName, image_dir)

    coco_dataset.display_info()
    coco_dataset.display_licenses()
    coco_dataset.display_categories()
    coco_dataset.printSelfDict()

    for image_id in list(coco_dataset.images.keys()):
        fmt = coco_dataset.get_image_format(image_id)
        if fmt == "GIF" or fmt == -1:
            print(fmt, image_id)
            coco_dataset.rm_file(image_id)
            coco_dataset.rm_json_dict(image_id)

    coco_dataset.save_json_dict(annotation_path, annotation_fileName)

def coco2yolo_main():
    annotation_path = '../datasets/COCO2017_PHONE/annotations/'
    #annotation_fileName = "instances_train.json"
    annotation_fileName = "instances_val.json"
    #image_dir = '../datasets/COCO2017_PHONE/images/train'
    image_dir = '../datasets/COCO2017_PHONE/images/val'
    data_type = "training"

    coco_dataset = CocoDataset(annotation_path + annotation_fileName, image_dir)

    coco_dataset.display_info()
    coco_dataset.display_licenses()
    coco_dataset.display_categories()
    #coco_dataset.printSelfDict()

    for image_id in list(coco_dataset.images.keys()):

        info_dict = coco_dataset.extract_COCO_to_info_dict(image_id)
        coco_dataset.convert_to_yolov5(info_dict, annotation_path)

    html_ = coco_dataset.display_image(1, use_url=False, show_polys=False, show_bbox = True, show_crowds = False)

def gif_filter_only_delete_file():

    file_path = "../../Datasets/Smoking/"

    files = sorted(glob.glob("%s/**/*.jpg" % file_path, recursive=True))
    for file in files:
        image = PILImage.open(file)
        fmt = image.format
        if fmt == "GIF":
            print(fmt)
            if os.path.isfile(file):
                os.remove(file)
                print("removed the file {}", file)


if __name__ == '__main__':
    coco2yolo_main()
    #displayCOCOimage()
    # gif_filter_main()
    # gif_filter_only_delete_file()
