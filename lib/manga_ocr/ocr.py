import re
from pathlib import Path
import unidic_lite
import jaconv
import torch
from PIL import Image
from loguru import logger
from transformers import AutoFeatureExtractor, AutoTokenizer, VisionEncoderDecoderModel, AutoConfig
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MangaOcr:
    def __init__(self, pretrained_model_name_or_path, force_cpu=False):
        logger.info(f'Loading OCR model from {pretrained_model_name_or_path}')
        try:
            self.feature_extractor = AutoFeatureExtractor.from_pretrained(pretrained_model_name_or_path, local_files_only=True)
            self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path, local_files_only=True , config=AutoConfig.from_pretrained(pretrained_model_name_or_path))
            self.model = VisionEncoderDecoderModel.from_pretrained(pretrained_model_name_or_path, local_files_only=True, config=AutoConfig.from_pretrained(pretrained_model_name_or_path))
        except:
            self.feature_extractor = AutoFeatureExtractor.from_pretrained(resource_path(pretrained_model_name_or_path), local_files_only=True)
            self.tokenizer = AutoTokenizer.from_pretrained(resource_path(pretrained_model_name_or_path), local_files_only=True, config=AutoConfig.from_pretrained(pretrained_model_name_or_path))
            self.model = VisionEncoderDecoderModel.from_pretrained(resource_path(pretrained_model_name_or_path), local_files_only=True, config=AutoConfig.from_pretrained(pretrained_model_name_or_path))


        if not force_cpu and torch.cuda.is_available():
            logger.info('Using CUDA')
            self.model.cuda()
        elif not force_cpu and torch.backends.mps.is_available():
            logger.info('Using MPS')
            self.model.to('mps')
        else:
            logger.info('Using CPU')

        logger.info('OCR ready')

    def __call__(self, img_or_path):
        if isinstance(img_or_path, str) or isinstance(img_or_path, Path):
            img = Image.open(img_or_path)
        elif isinstance(img_or_path, Image.Image):
            img = img_or_path
        else:
            raise ValueError(f'img_or_path must be a path or PIL.Image, instead got: {img_or_path}')

        img = img.convert('L').convert('RGB')

        x = self._preprocess(img)
        x = self.model.generate(x[None].to(self.model.device), max_length=300)[0].cpu()
        x = self.tokenizer.decode(x, skip_special_tokens=True)
        x = post_process(x)
        return x

    def _preprocess(self, img):
        pixel_values = self.feature_extractor(img, return_tensors="pt").pixel_values
        return pixel_values.squeeze()


def post_process(text):
    text = ''.join(text.split(''))
    text = text.replace('…', '...')
    text = re.sub('[・.]{2,}', lambda x: (x.end() - x.start()) * '.', text)
    text = jaconv.h2z(text, ascii=True, digit=True)

    return text
