# Models

Place the exported ONNX files in this folder (they are not stored in Git; use the download link / script):

| File | Task | Input | Output |
|---|---|---|---|
| `task1_universal.onnx` | 1 | `input` float32 [B,3,128,128] in [0,1] | `output` [B,3,128,128] in [0,1] |
| `task2_classifier.onnx` | 2 | `input` (as above) | `output` logits [B,4] — order: clean, salt_pepper, blur, occlusion |
| `task2_specialist_salt_pepper.onnx` | 2 | `input` | `output` |
| `task2_specialist_gaussian_blur.onnx` | 2 | `input` | `output` |
| `task2_specialist_occlusion.onnx` | 2 | `input` | `output` |
| `task3_soft_moe.onnx` | 3 | `input` | `output` image, `weights` [B,4] (same branch order) |
| `task4_generator.onnx` | 4 | `photo` float32 [B,3,128,128] in **[-1,1]**, `style` int64 [B] in {0,1,2} | `sketch` [B,3,128,128] in [-1,1] |

Download: `python scripts/download_models.py` (fill in the Google Drive file IDs inside the script first).
