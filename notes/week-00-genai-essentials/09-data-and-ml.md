# Data and Machine Learning

## Introduction

Data is the **foundation** of machine learning (ML) and large language models (LLMs). High-quality data ensures **better accuracy, reliability, and fairness**.

## Data Lifecycle in ML

``` mermaid
graph LR;
    A[Data Collection] --> B[Data Mining]
    B --> C[Knowledge Mining]
    C --> D[Data Wrangling]
    D --> E[Data Cleaning]
    E --> F[Data Labeling]
    F --> G[Feature Engineering]
    G --> H[Model Training]
    H --> I[Model Evaluation]
    I --> J[Deployment & Monitoring]
```

## Key Data Processing Steps

- **Collection**: Sources include web scraping, enterprise data, and user interactions.
- **Data Mining**: Extracting patterns and useful information from raw data.
- **Knowledge Mining**: Identifying insights and trends within large datasets.
- **Data Wrangling**: Converting raw data into a structured and usable format.
- **Cleaning**: Handling missing values, duplicates, and inconsistencies.
- **Labeling**: Manual annotation or weak supervision for supervised learning.
- **Feature Engineering**: Selecting and transforming relevant data attributes.

## Training vs. Validation vs. Test Data

| **Dataset** | **Purpose** |
|------------|------------|
| **Training** | Model learns patterns |
| **Validation** | Fine-tuning and hyperparameter selection |
| **Test** | Final performance evaluation |

## ML Pipeline

``` mermaid
graph LR;
    A[Raw Data] -->|Preprocessing| B[Clean Data]
    B -->|Feature Engineering| C[Feature Set]
    C -->|Model Training| D[Trained Model]
    D -->|Evaluation| E[Final Model]
    E -->|Deployment| F[Production]
```

## Model Evaluation Metrics

- **Accuracy**: Correct predictions / total predictions.
- **Precision & Recall**: Measures false positives and false negatives.
- **F1-Score**: Balances precision and recall.
- **ROC-AUC**: Evaluates classification performance.

## Applications

🔹 **Healthcare** – Disease prediction, diagnostics.  
🔹 **Finance** – Fraud detection, risk assessment.  
🔹 **E-commerce** – Recommendation systems.  
🔹 **Manufacturing** – Predictive maintenance.  

## Conclusion

A well-structured **data pipeline** ensures reliable ML models by focusing on **quality, preprocessing, and evaluation**.
