import numpy as np
import SimpleITK as sitk
import os
import sys
import cv2


class Preprocess:
    file_path: str = None
    folder_path: str = None
    array_images: np.ndarray = None

    def __init__(self, file_path, folder_path):
        self.file_path = file_path
        self.folder_path = folder_path
        self.read_file()
        self.save_images()

    def read_file(self):
        image = sitk.ReadImage(self.file_path)
        self.array_images = sitk.GetArrayFromImage(image)

    def save_images(self):

        if not os.path.exists(self.folder_path):
            os.mkdir(self.folder_path)

        for i, image in enumerate(self.array_images):
            image = cv2.resize(image, (256, 256))
            cv2.imwrite(fr"{self.folder_path}/{i}.jpg", image)


if __name__ == "__main__":
    # Logger.logr.info("Hellow")
    path_input = sys.argv[1]  # входной файл
    path_output = sys.argv[2]  # выходная директория
    print(path_input, path_output, sep='\n')
    Preprocess(path_input, path_output)
