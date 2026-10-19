from scipy import ndimage
import numpy as np

def select_grasp_cell(probs, threshold=0.5, fallback_to_argmax=True):
    """
    probs: (grid_size, grid_size) array of sigmoid probabilities
    Returns (row, col) of the chosen grasp cell, in grid coordinates.
    """
    above_thresh = probs > threshold

    if not above_thresh.any():
        if fallback_to_argmax:
            # nothing confident enough -- fall back to the single best cell
            idx = np.unravel_index(np.argmax(probs), probs.shape)
            return idx
        return None

    # label connected components (clusters of adjacent graspable cells)
    labeled, n_clusters = ndimage.label(above_thresh)

    if n_clusters == 1:
        # simple case: one region, take confidence-weighted centroid
        return _weighted_centroid(probs, labeled, 1)

    # multiple disjoint clusters: pick the one with highest total/average confidence
    best_cluster_id = None
    best_score = -np.inf
    for cluster_id in range(1, n_clusters + 1):
        cluster_mask = labeled == cluster_id
        cluster_score = probs[cluster_mask].mean()  # or .sum() to also favor larger clusters
        if cluster_score > best_score:
            best_score = cluster_score
            best_cluster_id = cluster_id

    return _weighted_centroid(probs, labeled, best_cluster_id)

def _weighted_centroid(probs, labeled, cluster_id):
    mask = labeled == cluster_id
    rows, cols = np.where(mask)
    weights = probs[mask]
    centroid_row = np.average(rows, weights=weights)
    centroid_col = np.average(cols, weights=weights)

    # round to nearest actual grid cell (centroid may fall between cells)
    grid_size = probs.shape[0]
    row_idx = int(np.clip(round(centroid_row), 0, grid_size - 1))
    col_idx = int(np.clip(round(centroid_col), 0, grid_size - 1))
    return (row_idx, col_idx)
