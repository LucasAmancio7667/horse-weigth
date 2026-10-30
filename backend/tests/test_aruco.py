import cv2
import numpy as np
import pytest

from app.vision.aruco import detect_marker, generate_marker


def scene_with_marker(marker_cm=10.0, px_per_cm=20.0, marker_id=0, angle_deg=0.0):
    """Cena sintética: fundo cinza com o marcador (e margem branca) numa escala conhecida."""
    side = int(marker_cm * px_per_cm)
    marker = generate_marker(marker_id, side, border_px=side // 4)
    h, w = 1200, 1600
    scene = np.full((h, w), 200, np.uint8)
    y, x = 200, 300
    scene[y : y + marker.shape[0], x : x + marker.shape[1]] = marker
    if angle_deg:
        m = cv2.getRotationMatrix2D((x + marker.shape[1] / 2, y + marker.shape[0] / 2), angle_deg, 1.0)
        scene = cv2.warpAffine(scene, m, (w, h), borderValue=200)
    return cv2.cvtColor(scene, cv2.COLOR_GRAY2BGR)


def test_detects_marker_and_computes_scale():
    result = detect_marker(scene_with_marker(10, 20), marker_size_cm=10)
    assert result is not None
    assert result.marker_id == 0
    assert result.pixels_per_cm == pytest.approx(20.0, rel=0.02)
    assert result.corners.shape == (4, 2)


def test_scale_follows_marker_size_in_image():
    # mesmo marcador de 15 cm, mas fotografado "mais perto" (30 px/cm)
    result = detect_marker(scene_with_marker(15, 30), marker_size_cm=15)
    assert result.pixels_per_cm == pytest.approx(30.0, rel=0.02)


def test_tolerates_rotation():
    result = detect_marker(scene_with_marker(10, 20, angle_deg=12), marker_size_cm=10)
    assert result is not None
    assert result.pixels_per_cm == pytest.approx(20.0, rel=0.03)


def test_returns_none_without_marker():
    blank = np.full((400, 400, 3), 180, np.uint8)
    assert detect_marker(blank, marker_size_cm=10) is None


def test_can_filter_by_marker_id():
    image = scene_with_marker(marker_id=7)
    assert detect_marker(image, 10, marker_id=0) is None
    assert detect_marker(image, 10, marker_id=7).marker_id == 7


def test_rejects_invalid_marker_size():
    with pytest.raises(ValueError):
        detect_marker(scene_with_marker(), marker_size_cm=0)
