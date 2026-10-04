"""Create tiny placeholder ONNX models with the SAME input/output contract as the real ones.
Lets you develop/test the UI and API before the trained models are copied into ./models.
   python tools/make_dummy_models.py models_dummy
"""
import sys
from pathlib import Path

import numpy as np
import onnx
from onnx import TensorProto as T, helper as h, numpy_helper as nh

out = Path(sys.argv[1] if len(sys.argv) > 1 else "models_dummy"); out.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(0)
IMG = ["batch", 3, 128, 128]


def save(nodes, name, ins, outs, inits=()):
    g = h.make_graph(nodes, name, ins, outs, list(inits))
    m = h.make_model(g, opset_imports=[h.make_opsetid("", 17)]); m.ir_version = 8
    onnx.checker.check_model(m); onnx.save(m, out / f"{name}.onnx")


vi = lambda n, t, s: h.make_tensor_value_info(n, t, s)
W = nh.from_array(rng.normal(size=(3, 4)).astype(np.float32) * 20, "W")

for n in ["task1_universal", "task2_specialist_salt_pepper", "task2_specialist_gaussian_blur", "task2_specialist_occlusion"]:
    save([h.make_node("Identity", ["input"], ["output"])], n, [vi("input", T.FLOAT, IMG)], [vi("output", T.FLOAT, IMG)])

save([h.make_node("ReduceMean", ["input"], ["m"], axes=[2, 3], keepdims=0), h.make_node("MatMul", ["m", "W"], ["output"])],
     "task2_classifier", [vi("input", T.FLOAT, IMG)], [vi("output", T.FLOAT, ["batch", 4])], [W])

save([h.make_node("Identity", ["input"], ["output"]), h.make_node("ReduceMean", ["input"], ["m"], axes=[2, 3], keepdims=0),
      h.make_node("MatMul", ["m", "W"], ["lg"]), h.make_node("Softmax", ["lg"], ["weights"], axis=1)],
     "task3_soft_moe", [vi("input", T.FLOAT, IMG)], [vi("output", T.FLOAT, IMG), vi("weights", T.FLOAT, ["batch", 4])], [W])

save([h.make_node("Cast", ["style"], ["sf"], to=T.FLOAT), h.make_node("Reshape", ["sf", "shp"], ["s4"]),
      h.make_node("Mul", ["s4", "k"], ["sm"]), h.make_node("Add", ["photo", "sm"], ["a"]), h.make_node("Tanh", ["a"], ["sketch"])],
     "task4_generator", [vi("photo", T.FLOAT, IMG), vi("style", T.INT64, ["batch"])], [vi("sketch", T.FLOAT, IMG)],
     [nh.from_array(np.array([-1, 1, 1, 1], np.int64), "shp"), nh.from_array(np.array([0.3], np.float32), "k")])
print("wrote", sorted(p.name for p in out.glob("*.onnx")))
