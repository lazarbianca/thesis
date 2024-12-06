import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# Step 1: Load your data
data = pd.read_csv('./datasets/ministry_forest_with_gfc_data.csv')
data = data[data['loss_year'].notnull()]  # Drop rows with missing loss_year

# Step 2: Select features and target
features = data[['tree_cover', 'Latitude', 'Longitude', 'S (ha)', 'Altitudine min', 'Altitudine max']]
target = data['loss_year']

# Step 3: Normalize/scale the features
scaler = MinMaxScaler()
features_scaled = scaler.fit_transform(features)

# Convert scaled features back to DataFrame with feature names
features_scaled_df = pd.DataFrame(features_scaled, columns=features.columns)

# Step 4: Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(features_scaled_df, target, test_size=0.1, random_state=42)

# Verify the split
print("Training set size:", len(X_train))
print("Testing set size:", len(X_test))

# Initialize the model
model = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the model on the training data
model.fit(X_train, y_train)

# Make predictions on the test data
y_pred = model.predict(X_test)

# Evaluate the model
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred, zero_division=1))

# Load Ministry data again to maintain the same context
ministry_data = pd.read_csv('./datasets/ministry_forest_with_gfc_data.csv')

# Select features and target from Ministry data
ministry_features = ministry_data[['tree_cover', 'Latitude', 'Longitude', 'S (ha)', 'Altitudine min', 'Altitudine max']]
ministry_target = ministry_data['loss_year']

# Normalize features
ministry_features_scaled = scaler.transform(ministry_features)

# Convert the normalized NumPy array to a DataFrame
ministry_features_scaled_df = pd.DataFrame(ministry_features_scaled, columns=features.columns)

# Predict using the baseline model
ministry_predictions = model.predict(ministry_features_scaled_df)

# Evaluate on Ministry data
print("Evaluation on Ministry Data")
print(classification_report(ministry_target, ministry_predictions, zero_division=1))

# Combine GFC and Ministry data for final training
combined_features = pd.concat([X_train, ministry_features_scaled_df], axis=0)
combined_target = pd.concat([y_train, ministry_target], axis=0)

# Train the model on combined data
model.fit(combined_features, combined_target)

# Evaluate on the test set
final_predictions = model.predict(X_test)

# Evaluate the refined model
print("Final Evaluation on Test Set")
print(classification_report(y_test, final_predictions, zero_division=1))
