# MV_PSR_DB_manager

* MOVON PSR(Passenger State Recognition) Database manager Code & Script git
    - Repacking the several dataset dirs into a single coco-formatting dataset

## HOW TO USE
    - run manifest.py in each dataset dir -> made dataset_info.meta
    - run manager.py with target dataset dirs

## Process Flow

```mermaid
graph LR
A[DB1]-->|meta| C{filter}
B[DB2]-->|meta| D{filter}
C -->|meta| E{merge}
D -->|meta| E
E -->|real migrate| F[New DB]
```

## Reference
    - cocoapi: [https://github.com/cocodataset/cocoapi](https://github.com/cocodataset/cocoapi)
