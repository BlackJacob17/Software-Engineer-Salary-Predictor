# Software-Engineer-Salary-Predictor

# Salary Predictor Using Machine Learning

## Project Overview
This repository contains a Machine Learning-based **Salary Predictor** application. The system predicts the annual salary of software developers based on various features such as years of experience, education level, and employment status. The project achieves a prediction accuracy of up to **95%**, leveraging advanced regression models and deep neural networks.

---

## Features
1. **Data Processing:**
   - Cleans raw data to remove inconsistencies such as missing or extreme values.
   - Handles categorical and numerical data effectively.
2. **Model Training:**
   - Implements both Linear Regression and Deep Neural Networks.
   - Achieves robust model evaluation with metrics like RMSE and R² scores.
3. **Hyperparameter Tuning:**
   - Utilizes Keras Tuner for optimizing neural network parameters.
4. **Retrainable Model:**
   - Supports retraining with new data to ensure up-to-date predictions.

---

## Dataset
The project is based on **32,000 entries** sourced from the [Stack Overflow Developer Survey](https://insights.stackoverflow.com/survey). Features extracted include:
- **ConvertedCompYearly (Target):** Annual compensation of developers.
- **YearsCode:** Total years of coding experience.
- **YearsCodePro:** Professional coding experience.
- **Employment:** Employment type.

---

## Getting Started

### Prerequisites
To run this project, ensure the following dependencies are installed:

- Python >= 3.8
- TensorFlow
- Keras
- Scikit-learn
- Pandas
- NumPy
- Seaborn

Install dependencies using:
```bash
pip install -r requirements.txt
```

### Installation
Clone the repository and navigate to the project directory:
```bash
git clone https://github.com/your_username/salary-predictor.git
cd salary-predictor
```

### Running the Project
1. **Data Preparation:** Place the `survey_results_public.csv` file in the root directory.
2. **Run the script:** Execute the main Python file:
   ```bash
   python mlproject.py
   ```

---

## Model Details

### Linear Regression
- **Features:** Years of experience, employment type, and compensation data.
- **Performance:** Provides baseline accuracy for salary predictions.

### Deep Neural Network
- **Architecture:**
  - Input layer with feature normalization.
  - Two hidden layers with ReLU activation.
  - Output layer for salary prediction.
- **Training:**
  - Optimizer: Adam
  - Loss Function: Mean Absolute Error (MAE)
  - Accuracy: Achieved 95% accuracy within a 10% tolerance range.

---

## Results
### Evaluation Metrics
- **Root Mean Square Error (RMSE):** Measures the average error magnitude.
- **R² Score:** Assesses the proportion of variance explained by the model.

Sample prediction:
- **Input:** 30 years of coding and 32 years of professional experience.
- **Output:** Predicted annual salary within 10% of the actual value.

---

## Future Improvements
1. **Expand Feature Set:** Incorporate additional survey features for better predictions.
2. **Model Deployment:** Host the model on a cloud platform for real-time predictions.
3. **Explainability:** Integrate tools like SHAP to explain model predictions.



---

Feel free to explore the code and contribute! Let us know if you have any questions or feature requests!

