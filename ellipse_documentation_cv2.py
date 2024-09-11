def ellipse(
    img: MatLike,
    center: Point,
    axes: Size,
    angle: float,
    startAngle: float,
    endAngle: float,
    color: Scalar,
    thickness: int = ...,
    lineType: int = ...,
    shift: int = ...
) -> MatLike: ...

def ellipse(
    img: UMat,
    center: Point,
    axes: Size,
    angle: float,
    startAngle: float,
    endAngle: float,
    color: Scalar,
    thickness: int = ...,
    lineType: int = ...,
    shift: int = ...
) -> UMat: ...

def ellipse(
    img: MatLike,
    box: RotatedRect,
    color: Scalar,
    thickness: int = ...,
    lineType: int = ...
) -> MatLike: ...

def ellipse(
    img: UMat,
    box: RotatedRect,
    color: Scalar,
    thickness: int = ...,
    lineType: int = ...
) -> UMat: ...



def rectangle(
    img: MatLike,
    pt1: Point,
    pt2: Point,
    color: Scalar,
    thickness: int = ...,
    lineType: int = ...,
    shift: int = ...
) -> MatLike: ...

def rectangle(
    img: UMat,
    pt1: Point,
    pt2: Point,
    color: Scalar,
    thickness: int = ...,
    lineType: int = ...,
    shift: int = ...
) -> UMat: ...

def rectangle(
    img: MatLike,
    rec: Rect,
    color: Scalar,
    thickness: int = ...,
    lineType: int = ...,
    shift: int = ...
) -> MatLike: ...

def rectangle(
    img: UMat,
    rec: Rect,
    color: Scalar,
    thickness: int = ...,
    lineType: int = ...,
    shift: int = ...
) -> UMat: ...