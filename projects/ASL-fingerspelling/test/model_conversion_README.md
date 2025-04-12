# Converting the Hugging Face ASL Model to TensorFlow.js

This guide explains how to convert the `TanmayNanda/ishara` ASL detection model from Hugging Face to a format that can be used directly in the browser with TensorFlow.js.

## Prerequisites

Make sure you have Python 3.7+ installed on your system. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

## Converting the Model

There are two conversion scripts available in this folder:

### Option 1: Generic Conversion Script

The `convert_huggingface_model.py` script can be used for any Hugging Face model:

```bash
python convert_huggingface_model.py --model_id TanmayNanda/ishara --output_dir ./models
```

### Option 2: Specialized Conversion Script for Ishara Model

The `convert_ishara_model.py` script is specifically tailored for the ASL detection model:

```bash
python convert_ishara_model.py
```

This will:

1. Download the model from Hugging Face
2. Convert it from PyTorch to TensorFlow format
3. Convert the TensorFlow model to TensorFlow.js format
4. Create a metadata.json file with label information
5. Save the converted model to `./models/ishara_tfjs`

## Integrating the Converted Model with the Web App

After conversion, the model will be available in the specified output directory. To use it in a web application:

1. Move the converted model files to a directory accessible by your web server
2. Update your JavaScript code to load the TensorFlow.js model:

```javascript
// Load the model
async function loadModel() {
  const model = await tf.loadGraphModel('path/to/model/model.json');
  return model;
}

// Process an image with the model
async function predictASLLetter(imageElement) {
  // Preprocess the image
  const tensor = tf.browser
    .fromPixels(imageElement)
    .resizeNearestNeighbor([224, 224]) // Resize to model's expected input
    .toFloat()
    .expandDims();

  // Make prediction
  const predictions = await model.predict(tensor);

  // Process results
  const scores = await predictions.data();
  tensor.dispose(); // Clean up memory

  return scores;
}
```

## Troubleshooting

If you encounter issues during conversion:

1. Check that your Python environment has all the required dependencies from requirements.txt
2. Make sure you have enough disk space for the model download and conversion
3. Check that you have an internet connection to access the Hugging Face Hub
4. For specific PyTorch to TensorFlow conversion issues, consult the Transformers library documentation

## Notes on the Ishara Model

The `TanmayNanda/ishara` model is designed for American Sign Language (ASL) fingerspelling detection. It takes an image as input and outputs probabilities for each letter of the alphabet. The model has been trained to recognize hand signs for letters A-Z.

When using this model in production:

- Consider resizing and normalizing input images appropriately
- Process input frames at a reasonable rate to avoid performance issues
- Use confidence thresholds to filter out uncertain predictions
