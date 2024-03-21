import sys
import cv2
import numpy as np
import tritonclient.http as httpclient
from typing import List
import os


class TritonClient:
    path_input_folder: str = None
    path_output_folder: str = None
    count_data: int = 0
    batch: int = 32
    paths_data_batch: List[List[str]] = []

    def __init__(self, path_input_folder,
                 path_output_folder, batch):
        self.path_input_folder = path_input_folder
        self.path_output_folder = path_output_folder
        self.batch = batch

        self.__read_folder()
        self.triton_inference()

    def __read_folder(self):
        paths_data = os.listdir(self.path_input_folder)
        self.count_data = len(paths_data)

        for i in range(0, self.count_data, self.batch):
            self.paths_data_batch.append(paths_data[i: i + self.batch])

    def __apply_batch(self, list_paths_batch: List[str]):

        input_image_batch = None
        for _path in list_paths_batch:
            path = os.path.join(self.path_input_folder, _path)

            if input_image_batch is None:
                input_image_batch = np.expand_dims(cv2.imread(path).astype(np.float32) / 255., 3)
            else:
                image = cv2.imread(path).astype(np.float32) / 255.
                input_image_batch = np.concatenate((input_image_batch, np.expand_dims(image, 3)) , axis=3)

        return np.transpose(input_image_batch, (3, 0, 1, 2))

    def triton_inference(self):
        triton_client = httpclient.InferenceServerClient(url="192.168.0.34:8000")
        model_name = "LV_Unet"

        count = 0
        for paths in self.paths_data_batch:
            input_image = self.__apply_batch(paths)
            inputs, outputs = [], []
            inputs.append(httpclient.InferInput("input_1", input_image.shape, "FP32"))
            inputs[0].set_data_from_numpy(input_image)

            outputs.append(httpclient.InferRequestedOutput("activation_18", binary_data=True))

            results = triton_client.infer(
                model_name=model_name,
                inputs=inputs,
                outputs=outputs,
            )

            result = results.as_numpy("activation_18")
            for img in result:
                cv2.imwrite(os.path.join(self.path_output_folder, f'{count}.jpg'), img*255)
                count += 1


if __name__ == "__main__":
    path_input = sys.argv[1]  # входной файл
    path_output = sys.argv[2]  # выходная директория
    TritonClient(path_input, path_output, 32)
