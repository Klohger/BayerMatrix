from typing import Final


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

    # subdivide into quad tree and call recursively
    MakeBayer(half,     x,          y, value + (step * 0),  step * 4,           matrix)             # Top Left
    MakeBayer(half,     x + half,   y + half,               value + (step * 1), step * 4, matrix)   # Bottom Right
    MakeBayer(half,     x + half,   y, value + (step * 2),  step * 4,           matrix)             # Top Right
    MakeBayer(half,     x,          y + half,               value + (step * 3), step * 4, matrix)   # Bottom Left
    return matrix


def PrintMatrix(matrix: Matrix):
    print(f"Bayer Matrix {matrix.__len__()}")
    for row in matrix:
        print(*list(map(lambda n: str(n).ljust(4), row)), sep="")


def OutputToPng(
    matrix: Matrix,
    tileCount: int = 1,
    path: str = "",
    normalizeBrightness: bool = True,
):
    from PIL import Image

    matrixSize = matrix.__len__()
    pngFilename = (
        
        f"{path}/bayer{matrixSize}{f'tile{tileCount}' if tileCount > 1 else '' }.png"
    )

    img = Image.new("L", (matrixSize * tileCount, matrixSize * tileCount))
    imgData = img.load()
    for y in range(img.height):
        for x in range(img.width):
            color = matrix[y % matrixSize][x % matrixSize]
            if normalizeBrightness:
                color *= 256 / (matrixSize * matrixSize)

            imgData[x, y] = color
    img.save(pngFilename, "PNG")
    print("Saved %s" % pngFilename)


if __name__ == "__main__":
    # size should be a power of two.
    # note that matrix sizes larger than 16 go out of 0..255 range,
    # so image export will not work correctly
    sizes = 2, 4, 8, 16

    tileCounts = 1, 2, 4, 8, 16

    for size in sizes:
        for tileCount in tileCounts:
            matrix = MakeBayer(size)
            OutputToPng(matrix, tileCount, path="images")
