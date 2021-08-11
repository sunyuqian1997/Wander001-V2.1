import logging
import string

import os
import cv2
import paddlehub
from PIL import Image
from wechaty_puppet import FileBox
from system.config import Baidu


class RobotImage(object):
    _picture_dir = os.getcwd() + "/images/pictures/"
    _transfer_tmp_dir = os.getcwd() + "/images/transfer_tmp/"
    _photo_dir = os.getcwd() + "/images/photos/"
    _style_imgs_dir = os.getcwd() + "/images/styles/"
    _logo_dir = os.getcwd() + "/images/logo/"
    _style = 1

    # 获取图片（现有）
    def _get_picture(self, longitude, latitude) -> FileBox:
        location_str = str(longitude) + "," + str(latitude)
        baidu = Baidu()
        # 根据地址构建请求对象
        baidu.set_panorama_url(location_str)
        picture_url = baidu.panorama_url

        return FileBox.from_url(picture_url, str(longitude) + "_" + str(latitude) + ".jpg")

    # 保存图像（功能性保存图片或者照片）
    async def save_image(self, image, is_photo=False) -> string:
        image_path = self._photo_dir if is_photo else self._picture_dir + image.name
        await image.to_file(image_path, True)

        return image_path

    def get_image_path(self, image, is_photo=False) -> string:
        return self._photo_dir if is_photo else self._picture_dir + image.name

    def _style_transfer(self, picture_path):
        style_path = self._style_imgs_dir + str(self._style) + ".jpg"

        # 风格迁移
        stylepro_artistic = paddlehub.Module(name="stylepro_artistic")

        try:
            result = stylepro_artistic.style_transfer(
                paths=[
                    {
                        "content": picture_path,
                        "styles": [style_path]
                    }
                ],
                alpha=1.0,
                visualization=True,
                output_dir=self._transfer_tmp_dir
            )
        except TypeError as te:
            logging.error(te)
            if cv2.imread(picture_path) is None:
                # 无此位置的图像
                raise Exception(10002)
            else:
                raise Exception(10003)

        return result[0]["save_path"]

    def _picture_synthesis(self, img_path, save_path, coordinate=None):
        logo_path = self._logo_dir + "realLogo.png"

        # 将图片赋值,方便后面的代码调用
        M_Img = Image.open(img_path)
        S_Img = Image.open(logo_path)

        # 获取图片的尺寸
        M_Img_w, M_Img_h = M_Img.size  # 获取被放图片的大小（母图）
        S_Img_w, S_Img_h = S_Img.size  # 获取小图的大小（子图）

        # # 重新设置子图的尺寸
        # icon = S_Img.resize((321, 60), Image.ANTIALIAS)
        icon = S_Img
        w = 23
        h = int((M_Img_h) - 23 - 60)

        try:
            if coordinate == None or coordinate == "":
                coordinate = (w, h)
                # 粘贴子图到母图的指定坐标（当前居中）
                M_Img.paste(icon, coordinate, mask=None)
            else:
                # 粘贴子图到母图的指定坐标（当前居中）
                M_Img.paste(icon, coordinate, mask=None)
            print("save:" + save_path)
            # 保存图片
            M_Img.save(save_path)
        except Exception as e:
            logging.error(e)
            raise Exception(10005)

    # 拍摄照片（未来）
    async def take_photo(self, longitude, latitude, style=None):
        self._style = self._style if style is None else style
        logging.debug("photo style is " + str(self._style))
        # 获取图片（现有）
        picture = self._get_picture(longitude, latitude)
        # 获取图片并保存到本地，风格迁移时候用
        picture_path = await self.save_image(picture)
        # 得到照片位置（未来时）
        transfer_tmp_path = self._style_transfer(picture_path)
        # 给照片加水印
        photo_path = self._photo_dir + transfer_tmp_path.split("/")[-1]
        logging.debug("photo file: " + transfer_tmp_path.split("/")[-1])
        self._picture_synthesis(transfer_tmp_path, photo_path)

        return FileBox.from_file(photo_path)
