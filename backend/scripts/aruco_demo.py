"""Demonstração isolada do ArUco.

Sem argumentos: gera o marcador para imprimir (marker_0.png) e uma foto de teste
(demo_scene.png) com o marcador de 10 cm a 20 px/cm, e confere a detecção.

Com uma foto sua:  python scripts/aruco_demo.py minha_foto.jpg 10
(o segundo argumento é o lado real do marcador impresso, em cm)
"""

import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.vision.aruco import detect_marker, generate_marker  # noqa: E402


def make_demo_scene(marker_cm: float = 10.0, px_per_cm: float = 20.0) -> np.ndarray:
    scene = np.full((700, 1000, 3), 235, np.uint8)
    side = int(marker_cm * px_per_cm)
    marker = cv2.cvtColor(generate_marker(0, side, border_px=int(side * 0.25)), cv2.COLOR_GRAY2BGR)
    scene[200 : 200 + marker.shape[0], 300 : 300 + marker.shape[1]] = marker
    return scene


def main() -> None:
    if len(sys.argv) >= 3:
        image = cv2.imread(sys.argv[1])
        if image is None:
            sys.exit(f"Não consegui abrir {sys.argv[1]}")
        size_cm = float(sys.argv[2])
    else:
        cv2.imwrite("marker_0.png", generate_marker(0, 600, border_px=150))
        image = make_demo_scene()
        cv2.imwrite("demo_scene.png", image)
        size_cm = 10.0
        print("Gerados: marker_0.png (imprimir) e demo_scene.png (cena de teste)")

    result = detect_marker(image, marker_size_cm=size_cm)
    if result is None:
        print("Marcador NÃO encontrado.")
        sys.exit(1)

    print(f"Marcador id={result.marker_id}  lado={result.side_px:.1f}px  escala={result.pixels_per_cm:.2f} px/cm")
    for p in result.corners.astype(int):
        cv2.circle(image, tuple(p), 6, (0, 0, 255), -1)
    cv2.imwrite("demo_result.png", image)
    print("Resultado salvo em demo_result.png")


if __name__ == "__main__":
    main()
