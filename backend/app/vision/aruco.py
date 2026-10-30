"""Detecção do marcador ArUco e cálculo da escala (pixels por cm).

O marcador impresso tem tamanho conhecido; medindo o lado dele na foto em pixels,
dá para converter qualquer distância da imagem para centímetros.
"""

from dataclasses import dataclass

import cv2
import numpy as np

DICTIONARY = cv2.aruco.DICT_4X4_50


@dataclass
class MarkerDetection:
    marker_id: int
    corners: np.ndarray  # shape (4, 2), ordem: topo-esq, topo-dir, base-dir, base-esq
    side_px: float  # média dos 4 lados, em pixels
    pixels_per_cm: float


def _detector() -> cv2.aruco.ArucoDetector:
    return cv2.aruco.ArucoDetector(
        cv2.aruco.getPredefinedDictionary(DICTIONARY), cv2.aruco.DetectorParameters()
    )


def generate_marker(marker_id: int = 0, size_px: int = 400, border_px: int = 0) -> np.ndarray:
    """Gera a imagem (cinza) do marcador, para imprimir. border_px adiciona margem branca."""
    dictionary = cv2.aruco.getPredefinedDictionary(DICTIONARY)
    img = cv2.aruco.generateImageMarker(dictionary, marker_id, size_px)
    if border_px:
        img = cv2.copyMakeBorder(img, border_px, border_px, border_px, border_px, cv2.BORDER_CONSTANT, value=255)
    return img


def detect_marker(image: np.ndarray, marker_size_cm: float, marker_id: int | None = None) -> MarkerDetection | None:
    """Procura o marcador na imagem.

    marker_size_cm: lado real do marcador impresso (parte preta, sem a margem branca).
    marker_id: se informado, só aceita esse ID. Devolve None se não achar.
    """
    if marker_size_cm <= 0:
        raise ValueError("marker_size_cm deve ser positivo")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    corners_list, ids, _ = _detector().detectMarkers(gray)
    if ids is None or len(ids) == 0:
        return None

    candidates = []
    for corners, found_id in zip(corners_list, ids.flatten()):
        if marker_id is not None and int(found_id) != marker_id:
            continue
        pts = corners.reshape(4, 2)
        sides = [np.linalg.norm(pts[i] - pts[(i + 1) % 4]) for i in range(4)]
        candidates.append((float(np.mean(sides)), int(found_id), pts))

    if not candidates:
        return None

    # Se houver mais de um, usa o maior (o mais próximo da câmera, em geral o melhor medido)
    side_px, found_id, pts = max(candidates, key=lambda c: c[0])
    return MarkerDetection(
        marker_id=found_id,
        corners=pts,
        side_px=side_px,
        pixels_per_cm=side_px / marker_size_cm,
    )
