import cv2
import os
import random
import matplotlib.pyplot as plt

# 1. Define Data Paths
# Update this path according to your local directory structure
IMAGE_DIR = 'datasets/Retail Shelf Detection.v4i.yolov8/train/images'
LABEL_DIR = 'datasets/Retail Shelf Detection.v4i.yolov8/train/labels'

# 2. Select a Random File for Verification
try:
    image_files = os.listdir(IMAGE_DIR)
    random_file = random.choice(image_files)
except FileNotFoundError:
    print(f"Error: Directory not found at {IMAGE_DIR}")
    exit()

# Extract file names
file_name = os.path.splitext(random_file)[0]
image_path = os.path.join(IMAGE_DIR, random_file)
label_path = os.path.join(LABEL_DIR, file_name + ".txt")

print(f"Selected Image: {image_path}")
print(f"Label File: {label_path}")

# 3. Read the Image
image = cv2.imread(image_path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # OpenCV uses BGR, convert to RGB
h, w, _ = image.shape

# 4. Read Labels and Draw Bounding Boxes
# YOLO Format: class_id x_center y_center width height (Normalized 0-1)
if os.path.exists(label_path):
    with open(label_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            parts = line.strip().split()
            class_id = int(parts[0])
            x_center, y_center, width, height = map(float, parts[1:])

            # Denormalize coordinates (Pixel values)
            x_min = int((x_center - width/2) * w)
            y_min = int((y_center - height/2) * h)
            x_max = int((x_center + width/2) * w)
            y_max = int((y_center + height/2) * h)

            # Draw Rectangle
            cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)
            
            # Add Label Text
            label_text = "Empty" if class_id == 2 else "Product"
            cv2.putText(image, label_text, (x_min, y_min - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
else:
    print("Warning: Label file not found for this image.")

# 5. Display the Image
plt.figure(figsize=(10, 10))
plt.imshow(image)
plt.axis('off')
plt.title("Data Verification Sample")
plt.show()