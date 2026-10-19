from scipy import ndimage
import numpy as np

# Grasp conventions shared by sim data generation (generate_data.py) and the real arm (sim_robot.py)
GRASP_YAW = 0.0  # world-frame claw heading (rad) at hover and grasp -- matches the recorded hover poses
GRIPPER_OPEN_TICKS = 2400  # partly open: clears the piece without sweeping its neighbours
GRIPPER_OPEN_SIM = -(GRIPPER_OPEN_TICKS / 2048 - 1) * 3.14  # same value in sim radians (gripper joint sign is -1)

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

def select_grasp_bbox(boxes, img_w, img_h,
                      min_area_frac=0.0035, max_area_frac=0.25,
                      max_aspect=1.6, max_center_dist_frac=0.35):
    """
    Pick the blue blob most likely to be the piece under the gripper.
    boxes: list of (x, y, w, h) in pixels. Returns one box or None.
    Thresholds are fractions of the image, so sim (640x360) and real
    (1920x1080) frames are filtered the same way.
    """
    img_area = img_w * img_h
    cx, cy = img_w / 2, img_h / 2
    max_dist = max_center_dist_frac * np.hypot(img_w, img_h)

    best, best_dist = None, np.inf
    for x, y, w, h in boxes:
        area_frac = (w * h) / img_area
        if not (min_area_frac <= area_frac <= max_area_frac):
            continue  # specks and large background regions
        if max(w, h) / max(min(w, h), 1) > max_aspect:
            continue  # long thin blobs (edges, reflections) -- the piece is roughly square
        dist = np.hypot(x + w / 2 - cx, y + h / 2 - cy)
        if dist <= max_dist and dist < best_dist:
            best, best_dist = (x, y, w, h), dist
    return best
