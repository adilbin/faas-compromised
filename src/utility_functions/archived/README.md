## Why these functions are archived at the moment.
1. [image_classifer](./image_classifier.py) file is archived for the moment due to high volume of syscalls made due to heavy libraries involved. Its making ~70K syscalls per invocation and the traceloop is unable to handle such large number of syscalls. 
<p align="center"><img src="./Screenshot 2025-11-20 at 10.28.38.png" width=50%></p>

* Image Classifier

  **Endpoint:** `POST /function/image-classifier`

  **Request:**
  ```bash
  curl -X POST http://localhost:8080/function/image-classifier \
    -H "Content-Type: application/json" \
    -d '{
      "image": "base64_encoded_image_data",
      "top_k": 5
    }'
  ```
  An example with red dot as image.
  ```bash
  curl -X POST http://localhost:8080/function/image-classifier \
    -H "Content-Type: application/json" \
    -d '{
      "image": "<iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==",
      "top_k": 5
    }'
  ```

  **Request Body:**
  ```json
  {
    "image": "base64_encoded_image_data",
    "top_k": 5
  }