import cv2
import os
import sys
import numpy as np
import SimpleITK as sitk


class Postprocess:
    output_file_path: str = None
    folder_path: str = None
    paths_image_list: str = None

    def __init__(self, folder_path: str,
                 output_file_path: str) -> None:
        self.output_file_path = output_file_path
        self.folder_path = folder_path
        self.__sorted_folder()
        self.save_file()

    def __sorted_folder(self) -> None:
        self.paths_image_list = list(sorted(os.listdir(self.folder_path),
                                            key=lambda x: int(x.split('.')[0])))

    def save_file(self) -> None:
        w, h = 256, 256
        result_image = np.empty((w, h, 1, len(self.paths_image_list)), np.float32)

        for i, image_path in enumerate(self.paths_image_list):
            result_image[..., i] = cv2.imread(os.path.join(self.folder_path, image_path))

        result_image = sitk.GetImageFromArray(result_image)
        sitk.WriteImage(result_image, os.path.join(self.output_file_path, "segm.nii.gz"))


if __name__ == "__main__":
    path_input = sys.argv[1]  # входной файл
    path_output = sys.argv[2]  # выходная директория
    print(path_input, path_output, sep='\n')
    Postprocess(path_input, path_output)
