import matplotlib
matplotlib.use('Agg') # Run in headless mode (no window)
from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt
import os
import glob
import datetime
import random
from database_manager import ShelfDatabase # <--- NEW: Import our DB manager

def analyze_shelf():
    # 0. Initialize Database
    db = ShelfDatabase()

    # 1. Load the Model
    model_path = 'runs/detect/shelf_model/weights/best.pt'
    try:
        model = YOLO(model_path)
    except Exception as e:
        print(f"Error: Could not load the model! Details: {e}")
        return

    # 2. Automatically Select a RANDOM Test Image
    test_dir = 'datasets/Retail Shelf Detection.v4i.yolov8/test/images'
    image_files = glob.glob(os.path.join(test_dir, '*.jpg'))
    
    if not image_files:
        print(f"ERROR: No images found in directory: '{test_dir}'")
        return

    test_image_path = random.choice(image_files)
    image_name = os.path.basename(test_image_path)
    print(f"📸 Selected Random Image: {image_name}")

    # 3. Run Inference
    print("Running analysis...")
    results = model.predict(test_image_path, conf=0.25, verbose=False) # verbose=False to clean terminal
    result = results[0]

    # 4. Business Logic
    product_count = 0
    empty_count = 0

    for box in result.boxes:
        class_id = int(box.cls[0])
        class_name = result.names[class_id]
        
        if class_name == 'Empty':
            empty_count += 1
        else:
            product_count += 1

    # 5. Reporting
    print("\n" + "=" * 40)
    print(f"📊 SHELF ANALYSIS REPORT")
    print("=" * 40)
    print(f"📦 Total Products Detected : {product_count}")
    print(f"⚠️  Empty Spots Detected   : {empty_count}")
    print("-" * 40)

    status = "OK"
    if empty_count > 0:
        print("🚨 ALERT: Restocking required! Gaps detected.")
        status = "RESTOCK_NEEDED"
    else:
        print("✅ STATUS: Shelf is fully stocked.")
    print("=" * 40 + "\n")

    # 6. Save Evidence Image
    output_dir = "runs/analysis_results"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    output_filename = f"analysis_{timestamp}.jpg"
    save_path = os.path.join(output_dir, output_filename)

    annotated_frame = result.plot()
    resim_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

    plt.figure(figsize=(12, 8))
    plt.imshow(resim_rgb)
    plt.axis('off')
    plt.title(f"Status: {status} | Empty: {empty_count} | Products: {product_count}")
    
    plt.savefig(save_path)
    plt.close()
    print(f"📸 Evidence saved to: {save_path}")

    # 7. SAVE TO DATABASE (THE NEW PART)
    print("💾 Saving to database...")
    db.log_analysis(image_name, product_count, empty_count, status)

    # 8. Verify Data (Show last 3 logs)
    print("\n🔍 RECENT DATABASE LOGS:")
    recent_logs = db.fetch_recent_logs(3)
    for log in recent_logs:
        print(log)

if __name__ == '__main__':
    analyze_shelf()