import torch
import cv2
import time

""" All possible things we can change
model.conf = 0.25  # NMS confidence threshold
      iou = 0.45  # NMS IoU threshold
      agnostic = False  # NMS class-agnostic
      multi_label = False  # NMS multiple labels per box
      classes = None  # (optional list) filter by class, i.e. = [0, 15, 16] for COCO persons, cats and dogs
      max_det = 1000  # maximum number of detections per image
      amp = False  # Automatic Mixed Precision (AMP) inference
"""

def get_model(path='best.pt',conf = 0.65, max_det=100):
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=path)
    # setting model parameters
    model.conf = conf # confidence threshold
    model.max_det = max_det # maximum detectionss

    return model

def infer(model,img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = model(img)
    return results

# Draw bounding boxes and labels
def draw_bounding_box(img, model, results):
    copy = img.copy()
    for *xyxy, conf, cls in results.xyxy[0]:
        x1, y1, x2, y2 = map(int, xyxy)
        label = model.names[int(cls)]  # Get the label for the class
        #print("label: ", label)
        color = (255, 0, 0)  # Blue color in BGR
        cv2.rectangle(copy, (x1, y1), (x2, y2), color, 2)
        cv2.putText(copy, f'{label} {conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return copy

def show_image(img):
    # Display the image
    cv2.imshow('YOLOv5 Detection', img)
    cv2.waitKey(0)  # Wait for a key press to close the window
    cv2.destroyAllWindows()

def write_image(img):
    # Display the image
    cv2.imwrite('YOLOv5-Detection', img.copy())
