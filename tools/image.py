import cv2


def compress_cv2_image(img, quality=50):
    return cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, quality])[1]

def decompress_cv2_image(compressed_cv2):
    return cv2.imdecode(compressed_cv2, -1)