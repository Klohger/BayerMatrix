from pathlib import Path
from typing import Literal

from PIL import Image

Matrix = list[list[int]]


def MakeBayer(
    size: int = 16,
    x: int = 0,
    y: int = 0,
    value: int = 0,
    step: int = 1,
    matrix: Matrix | None = None,
):
    if matrix is None:
        matrix = [[0 for _ in range(size)] for _ in range(size)]

    if size == 1:
        matrix[y][x] = value
        return matrix

    half = size // 2
    # fmt: off
    # subdivide into quad tree and call recursively 
    MakeBayer(size=half,     x=x,          y=y,         value=value + (step * 0),   step=step * 4, matrix=matrix)   # Top Left
    MakeBayer(size=half,     x=x + half,   y=y + half,  value=value + (step * 1),   step=step * 4, matrix=matrix)   # Bottom Right
    MakeBayer(size=half,     x=x + half,   y=y,         value=value + (step * 2),   step=step * 4, matrix=matrix)   # Top Right
    MakeBayer(size=half,     x=x,          y=y + half,  value=value + (step * 3),   step=step * 4, matrix=matrix)   # Bottom Left
    # fmt: on
    return matrix


def PrintMatrix(matrix: Matrix):
    print(f"Bayer Matrix {matrix.__len__()}")
    for row in matrix:
        print(*list(map(lambda n: str(n).ljust(4), row)), sep="")


def SaveAsImage(
    matrix: Matrix,
    tileCount: int = 1,
    mode: Literal["L"] | Literal["I"] | Literal["F"] = "L",
    folder: Path = Path.cwd(),
    ext: str = ".png",
    format: str = "PNG",
    normalize: bool = True,
):
    matrixSize = matrix.__len__()
    outputPath = (
        folder / f"bayer{matrixSize}{f'tile{tileCount}' if tileCount > 1 else '' }{f'mode{mode}' if mode != 'L' else '' }{ext}"
    )

    img = Image.new(mode, size=(matrixSize * tileCount, matrixSize * tileCount), color=None)  # type: ignore
    imgData = img.load()
    for y in range(img.height):
        for x in range(img.width):
            color = matrix[y % matrixSize][x % matrixSize]
            if normalize:
                match mode:
                    case "L":
                        color = (color * (256 / (matrixSize * matrixSize))).__floor__()
                    case "I":
                        # so apparently the docs are lying and in i mode 'I' each pixel is represented by a 16 bit unsigned integer
                        color = (
                            color * (65536 / (matrixSize * matrixSize))
                        ).__floor__()
                    case "F":
                        color *= 1 / (matrixSize * matrixSize)

            imgData[x, y] = color
    img.save(outputPath, format)
    print(f"Saved {outputPath}")


if __name__ == "__main__":
    # size should be a power of two.
    # note that matrix sizes larger than 16 go out of 0..255 range,
    # so image export will not work correctly
    sizesLowerThan32 = 2, 4, 8, 16

    tileCounts = 1, 2, 4, 8, 16

    for size in sizesLowerThan32:
        for tileCount in tileCounts:
            matrix = MakeBayer(size)
            SaveAsImage(
                matrix,
                tileCount,
                folder=Path("./images"),
                mode="L",
            )

    sizesHigherThan16 = 32, 64, 128, 256

    for size in sizesHigherThan16:
        for tileCount in tileCounts:
            matrix = MakeBayer(size)
            SaveAsImage(
                matrix,
                tileCount,
                folder=Path("./images"),
                mode="I",
            )
