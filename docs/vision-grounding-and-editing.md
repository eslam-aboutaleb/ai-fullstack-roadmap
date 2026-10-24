# Computer vision, grounding and image editing (issue #39)

Introduction: classification, detection, segmentation, OCR and visual
question answering answer different questions. A **visual language model**
(VLM) can describe image content but does not guarantee that its claims are
bound to correct regions. A diffusion image-generation model has a separate
training objective and editing semantics.

Run: `python3 -B labs/vision_grounding_geometry.py`.

The offline lab uses hand-authored 2D boxes and pixel arrays to test IoU,
per-class non-maximum suppression, one-to-one matching and a binary mask edit.
It does **not** load a pretrained ViT/CNN/VLM, image generator, or hosted
vision service; these tests establish geometry invariants only.

Learning sequence: image tensor dimensions and coordinate frames → CNN
receptive fields / ViT patch tokens → detection vs segmentation → region
grounding → contrastive joint text/image embeddings → conditional diffusion
and masked inpainting → privacy and metric limitations.

Optional real-model experiments should follow official PyTorch tutorials
and pin torchvision/model revisions, gold box annotations, grouped train/test
splits and image preprocessing. Evaluate exact category/slice IoU and mAP
configuration, hallucinations, citation-to-region and authorizations before
claiming measurable quality. Do not claim CLIP score or a single IoU measures
editing quality.

Primary reference: https://docs.pytorch.org/tutorials/domains.html
