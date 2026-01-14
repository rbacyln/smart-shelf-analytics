from ultralytics import YOLO

def main():
    # 1. Load the Model
    # 'yolov8n.pt' -> Nano model (Selected for real-time performance)
    model = YOLO('yolov8n.pt') 

    # 2. Train the Model
    # data: Path to the data.yaml file
    # epochs: Number of training iterations
    # imgsz: Image size (640 is standard for YOLO)
    results = model.train(
        data='/Users/rabiaceylan/Smart-Shelf-Analytics/datasets/Retail Shelf Detection.v4i.yolov8/data.yaml',
        epochs=10,
        imgsz=640,
        name='shelf_model', # Results will be saved in 'runs/detect/shelf_model'
        plots=True          # Generate training graphs
    )

    print("Training Completed Successfully! 🚀")

if __name__ == '__main__':
    main()