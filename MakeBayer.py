from math import log10
from pathlib import Path
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
    # Subdivide into four recursively until size is 1.
    MakeBayer(size=half,     x=x,          y=y,         value=value + (step * 0),   step=step * 4, matrix=matrix)   # Top Left
    MakeBayer(size=half,     x=x + half,   y=y + half,  value=value + (step * 1),   step=step * 4, matrix=matrix)   # Bottom Right
    MakeBayer(size=half,     x=x + half,   y=y,         value=value + (step * 2),   step=step * 4, matrix=matrix)   # Top Right
    MakeBayer(size=half,     x=x,          y=y + half,  value=value + (step * 3),   step=step * 4, matrix=matrix)   # Bottom Left
    # fmt: on
    return matrix


def PrintMatrixGrid(matrix: Matrix):
    print(f"Bayer Matrix {matrix.__len__()}")
    for row in matrix:
        print(
            *[
                str(num).rjust(
                    log10(matrix.__len__() * matrix.__len__() - 1).__floor__() + 1
                , "0")
                for num in row
            ],
            sep=" ",
        )


def PrintMatrix(matrix: Matrix):
    print(f"Bayer Matrix {matrix.__len__()}\n{[num for row in matrix for num in row]}")


def SaveAsImage(
    matrix: Matrix,
    tileCount: int = 1,
    mode: str = "L",
    folder: Path = Path.cwd(),
    ext: str = "png",
    format: str | None = None,
    normalize: bool = True,
    scale: int = 1,
    sizePadding: int | None = None,
):
    matrixSize = matrix.__len__()
    outputPath = (
        folder
        / f'Bayer.{str(matrixSize).rjust(sizePadding, "0") if sizePadding else matrixSize}-Scale.{scale}-Tile.{tileCount}-Mode.{mode}{ "-Norm" if normalize else "" }.{ext}'
    )

    img = Image.new(mode, size=(matrixSize * tileCount, matrixSize * tileCount), color=None)  # type: ignore

    imgData = img.load()
    for y in range(img.height):
        for x in range(img.width):
            color = matrix[y % matrixSize][x % matrixSize]
            if normalize:
                match mode:
                    case "L":
                        color = (color * 256) // (matrixSize * matrixSize)
                    case "I" | "I;16":
                        color = (color * 65536) // (matrixSize * matrixSize)

                    case "F":
                        color /= matrixSize * matrixSize
                    case unconfigured:
                        raise Exception(
                            f"""brightness normalization for mode {unconfigured} has not been implemented! 
                            Either disable brightness normalization by setting parameter normalize to False 
                            or add an implementation for the mode."""
                        )

            imgData[x, y] = color
    if scale > 1:
        img = img.resize(
            (img.width * scale, img.height * scale), resample=Image.NEAREST
        )
    img.save(outputPath, format, optimize=True)
    print(f"Saved {outputPath}")


# NOTE: Size should be a power of two and is UNCHECKED.
# Matrix sizes larger than 16 go out of 0..255 range,
# so to export images you will have to increase the bit depth
# by setting the image mode to "I", "I;16" or "F".
# You can read about pillow modes here: https://pillow.readthedocs.io/en/latest/handbook/concepts.html#modes
# NOTE: in the docs they say that mode "I" represents a pixel with a 32 bit signed integer.
# This is false: they're represented with a 16 bit unsigned integer, just like "I;16".
# You can read about it here: https://stackoverflow.com/questions/69192736/what-is-i-mode-in-pillow
if __name__ == "__main__":
    sizes = 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024
    # tileCounts = 1, 2, 4
    print(f"Generating matrices {sizes[0]}-{sizes[sizes.__len__()-1]}...")
    matrices = {size: MakeBayer(size) for size in sizes}
    print(f"Generated!")

    folder = Path("./images")
    folder.mkdir(exist_ok=True)

    pngFolder = folder / "PNG"
    pngFolder.mkdir(exist_ok=True)

    for size in sizes[0:4]:  # 2, 4, 8, 16
        # for tileCount in tileCounts:
        SaveAsImage(
            matrix=matrices[size],
            # tileCount=tileCount,
            folder=pngFolder,
            mode="L",
            sizePadding=3,
        )

    for size in sizes[4:8]:  # 32, 64, 128, 256
        # for tileCount in tileCounts:
        SaveAsImage(
            matrix=matrices[size],
            # tileCount=tileCount,
            folder=pngFolder,
            mode="I",
            sizePadding=3,
        )

    tiffFolder = folder / "TIFF"
    tiffFolder.mkdir(exist_ok=True)
    for size in sizes:
        # for tileCount in tileCounts:
        SaveAsImage(
            matrix=matrices[size],
            # tileCount=tileCount,
            folder=tiffFolder,
            ext="tiff",
            mode="F",
            sizePadding=4,
        )
