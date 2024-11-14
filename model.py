import numpy as np
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
from transform_dataset import apply_features

# Function to evaluate model performance on test data
def evaluate_model(model, X_val, y_val, X_test, y_test):
    y_val_pred = model.predict(X_val)
    y_test_pred = model.predict(X_test)
    
    val_mse = mean_squared_error(y_val, y_val_pred)
    test_mse = mean_squared_error(y_test, y_test_pred)
    
    val_r2 = r2_score(y_val, y_val_pred)
    test_r2 = r2_score(y_test, y_test_pred)
    
    print(f'Validation MSE: {val_mse:.4f}, R2: {val_r2:.4f}')
    print(f'Test MSE: {test_mse:.4f}, R2: {test_r2:.4f}')
    
    return y_test_pred

# fetech, train, val, test data from the dataset folder
X_train = np.load('dataset/train_features.npy')
y_train = np.load('dataset/train_label.npy')
X_val = np.load('dataset/validation_features.npy')
y_val = np.load('dataset/validation_label.npy')
X_test = np.load('dataset/test_features.npy')
y_test = np.load('dataset/test_label.npy')

# replace NaN values with 0 in X
X_train = np.nan_to_num(X_train)
X_val = np.nan_to_num(X_val)
X_test = np.nan_to_num(X_test)

# Ridge Regression
ridge = Ridge(alpha=1.0)  # Default alpha parameter
ridge.fit(X_train, y_train)

print("Ridge Regression Performance:")
evaluate_model(ridge, X_val, y_val, X_test, y_test)

# Random Forest Regressor
rf = RandomForestRegressor(n_estimators=100, max_depth=None, random_state=42)
rf.fit(X_train, y_train)

print("Random Forest Performance:")
evaluate_model(rf, X_val, y_val, X_test, y_test)

# XGBoost Regressor
xgb = XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
xgb.fit(X_train, y_train)

print("XGBoost Performance:")
evaluate_model(xgb, X_val, y_val, X_test, y_test)

# Load glove embeddings
glove_embeddings = {}
print("Loading glove embeddings")
with open('glove.6B.100d.txt', 'r') as f:
    for line in f:
        values = line.split(' ')
        word = values[0]
        vector = np.asarray(values[1:], "float32")
        glove_embeddings[word] = vector

# Test models on a new statement
statement = "THEY ARE EATING THE DOGS, THEY ARE EATING THE CATS IN SPRINGFIELD"
statement_features = apply_features([statement], glove_embeddings)
statement_features = np.nan_to_num(statement_features)
# Predict using all models
ridge_pred = ridge.predict(statement_features)
rf_pred = rf.predict(statement_features)
xgb_pred = xgb.predict(statement_features)

print(f'Ridge Prediction: {ridge_pred[0]:.4f}')
print(f'Random Forest Prediction: {rf_pred[0]:.4f}')
print(f'XGBoost Prediction: {xgb_pred[0]:.4f}')
