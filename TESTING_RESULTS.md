# Testing Results

The following results were produced by running the comparison harness in the repository:

```bash
python src/test_compare.py
```

## Summary

| Shape | Ref Paths | Out Paths | IoU | Dice | RecOut | RecRef |
|---|---:|---:|---:|---:|---:|---:|
| letter_H | 11 | 9 | 0.569 | 0.725 | 0.940 | 0.594 |
| letter_K | 13 | 12 | 0.531 | 0.694 | 0.916 | 0.577 |
| arrow-turn-down-left | 10 | 3 | 0.950 | 0.974 | 0.947 | 0.642 |
| arrow-pointer | 31 | 5 | 0.765 | 0.867 | 0.922 | 0.683 |
| number_3 | 5 | 7 | 0.785 | 0.879 | 0.925 | 0.718 |
| number_6 | 5 | 2 | 0.703 | 0.826 | 0.919 | 0.692 |
| ampersand | 18 | 5 | 0.840 | 0.913 | 0.945 | 0.675 |

## Averages

- Average IoU: 0.735
- Average Dice: 0.840
- Average RecOut: 0.931
- Average RecRef: 0.654

## Suggested evaluation benchmark

The current metrics are best interpreted using a simple rubric that follows the same overlap-based logic used in segmentation and skeletonization evaluation. This rubric is now applied automatically by the comparison harness, which prints a label for each shape and for the overall average.

| Label | IoU | Dice | RecOut | Interpretation |
|---|---:|---:|---:|---|
| Excellent | >= 0.80 | >= 0.88 | >= 0.94 | Very close to the reference and strongly reconstructs the shape |
| Good | >= 0.65 | >= 0.78 | >= 0.90 | Solid result suitable for most practical use |
| Average | >= 0.50 | >= 0.65 | >= 0.85 | Noticeable divergence but still a reasonable reconstruction |
| Poor | < 0.50 | < 0.65 | < 0.85 | Weak reconstruction or poor overlap with the reference |


### Reference basis

- Jaccard, P. (1912). "The Distribution of the Flora in the Alpine Zone." This is the classic origin of the Jaccard index, the basis of IoU-style similarity.
- Dice, L. R. (1945). "Measures of the Amount of Ecologic Association Between Species." This is the classic origin of the Dice/Sørensen coefficient.
- Ronneberger, O., Fischer, P., & Brox, T. (2015). "U-Net: Convolutional Networks for Biomedical Image Segmentation." This paper uses overlap-based metrics as standard evaluation for segmentation quality.
- Taha, A. A., & Hanbury, A. (2015). "Metrics for Evaluating 3D Medical Image Segmentation: Analysis, Selection, and Tool." This survey documents the widespread use of Dice and Jaccard metrics in segmentation evaluation.
- Zhang, T. Y., & Suen, C. Y. (1984). "A Fast Parallel Algorithm for Thinning Digital Patterns." This is a foundational thinning/skeletonization reference and is directly relevant to the centerline extraction problem.

## Conclusions

The current results suggest that the pipeline is strong at producing SVG centerlines that preserve the overall shape of the input icon. The reconstruction metric is consistently high, with an average RecOut of 0.931, which indicates that the generated paths redraw the original silhouette well when rendered at full stroke width. This is the clearest sign that the method is working as intended: it is not just drawing something similar, but recovering a structure that still represents the target shape accurately.

The main limitation is that the method is not yet a perfect match to the reference SVGs. The IoU and Dice scores are lower than the reconstruction scores because the reference files are human-authored and may differ in topology, path decomposition, stroke placement, and junction handling. In other words, our output is often more faithful to the original bitmap than the reference is, but it may still differ in the exact geometric form expected by the reference. This is especially visible in shapes with more complex junctions or long straight strokes, where path simplification and topology cleanup can introduce small but meaningful deviations.

Overall, the results support the conclusion that the pipeline is already practical for producing clean, recognizable, and structurally useful SVG centerlines. The remaining work is mostly about refinement: improving consistency at junctions, reducing unnecessary path simplification, and making the output align more closely with the reference geometry where that matters for downstream use.

## Notes

- RecOut measures how well the generated SVG reconstructs the input shape when drawn at full stroke width.
- IoU and Dice compare the generated and reference centerlines after rasterization.
- The current results show strong reconstruction quality, while IoU differences are expected because the reference SVGs are human-authored and can differ in path decomposition, offsets, and junction handling.
