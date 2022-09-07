import sys, json

anno_file = sys.argv[1]
output_file = ''
if len(sys.argv) > 2:
  output_file = sys.argv[2]
else:
  output_file = "output_anno.json"

anno_js = json.load(open(anno_file, 'r'))

new_an = []
for an in anno_js['annotations']:
  n = {
    "id": an["id"],
    "image_id": an["image_id"],
    "category_id": an["category_id"],
    "bbox": an["bbox"],
    "area": an["area"],
    "iscrowd": an["iscrowd"]
  }
  new_an.append(n)
new_anno = {
  "licenses": anno_js["licenses"],
  "info": anno_js["info"],
  "categories": anno_js["categories"],
  "images": anno_js["images"],
  "annotations": new_an
}
json.dump(new_anno, open(output_file, 'w'))
