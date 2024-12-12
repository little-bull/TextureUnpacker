import os
from PIL import Image  
from pathlib import Path

'''
必要属性
1. 切割区域            Rect 
2. 旋转               Rotated
3. 子图原始尺寸       SourceSize
4. 偏移量              Offset


V2
- frames
    name.png
        frame
        sourceSize
        sourceColorRect
        offset
        rotated
- metadata
    format : 2
V3
- frames
    name.png
        textureRect : 父图切割区域            Rect
        spriteSourceSize : 子图整体尺寸       SourceSize
        spriteColorRect ： 子图渲染原点和尺寸  ColorRect
        spriteTrimmed ： 子图渲染原点是否偏移  Trimmed
        spriteOffset ： 渲染原点偏移量        Offset
        textureRotated ： 图片是否旋转         Rotated
        spriteSize
        aliases[]
- metadata
    format : 3
'''

def check_format(plist):
    fm = plist['metadata']['format']
    items = []
    if fm == 2:
        for key in plist['frames']:
            items.append(transform_v2(plist['frames'][key], key))
    elif fm == 3:
        for key in plist['frames']:
            items.append(transform_v3(plist['frames'][key], key))
    return items


def transform_v2(frame, pathname):
    result = {'pathname': pathname}
    if frame['frame']:
        p1 = frame['frame'].replace('}', '').replace('{', '').split(',')
        p2 = frame['sourceSize'].replace('}', '').replace('{', '').split(',')
        p3 = frame['sourceColorRect'].replace('}', '').replace('{', '').split(',')
        p4 = frame['rotated']

        # 去透明后的子图矩形
        x, y, w, h = tuple(map(int, p1))
        # 子图原始大小
        size = tuple(map(int, p2))
        # 子图在原始图片中的偏移
        ox, oy, _, _ = tuple(map(int, p3))

        # 获取子图左上角，右下角
        if p4:
            box = (x, y, x + h, y + w)
        else:
            box = (x, y, x + w, y + h)
        result['Rect'] = box
        result['SourceSize'] = size
        result['Offset'] = (ox, oy)
        result['Rotated'] = p4
    return result


def transform_v3(frame, pathname):
    result = {'pathname': pathname}
    if 'textureRect' in frame.keys():
        p1 = frame['textureRect'].replace('}', '').replace('{', '').split(',')
        p2 = frame['spriteSourceSize'].replace('}', '').replace('{', '').split(',')
        p3 = frame['spriteOffset'].replace('}', '').replace('{', '').split(',')
        p4 = frame['textureRotated']
    cx = 0
    cy = 0
    if 'spriteTrimmed' in frame.keys():
        if frame['spriteTrimmed']:
            p5 = frame['spriteColorRect'].replace('}', '').replace('{', '').split(',')
            cx, cy, _, _ = tuple(map(int, p5))

    # 去透明后的子图矩形
    x, y, w, h = tuple(map(int, p1))
    # 子图原始大小
    size = tuple(map(int, p2))
    # 子图在原始图片中的偏移
    ox, oy = tuple(map(int, p3))

    # 获取子图左上角，右下角
    if p4:
        box = (x, y, x + h, y + w)
    else:
        box = (x, y, x + w, y + h)

    result['Rect'] = box
    result['SourceSize'] = size
    result['Offset'] = (ox + cx, oy + cy)
    # result['Offset'] = (ox, oy)
    result['Rotated'] = p4
    return result


def extract_image(img, item):
    box = item['Rect']
    size = item['SourceSize']
    offset = item['Offset']
    rotated = item['Rotated']
    # 使用原始大小创建图像，全透明
    image = Image.new('RGBA', size, (0, 0, 0, 0))
    # 从图集中裁剪出子图
    sprite = img.crop(box)

    # rotated纹理旋转90度
    if rotated:
        sprite = sprite.transpose(Image.ROTATE_90)

    # 粘贴子图，设置偏移
    image.paste(sprite, offset)

    return image


def extract_image_2_png(img, path, item):
    box = item['Rect']
    size = item['SourceSize']
    offset = item['Offset']
    rotated = item['Rotated']
    pathname = item['pathname']
    # 使用原始大小创建图像，全透明
    image = Image.new('RGBA', size, (0, 0, 0, 0))
    # 从图集中裁剪出子图
    sprite = img.crop(box)

    # rotated纹理旋转90度
    if rotated:
        sprite = sprite.transpose(Image.ROTATE_90)

    # 粘贴子图，设置偏移
    image.paste(sprite, offset)

    img_path = os.path.join(path, pathname)
    # 保存到文件
    if not img_path.endswith("png") :
        img_path += ".png"
    # print('保存文件：%s' % img_path)
    Path(img_path).parent.mkdir(parents=True, exist_ok=True)

    image.save(img_path, 'png')



def extract_image_2_jpg(img, path, item):
    box = item['Rect']
    size = item['SourceSize']
    offset = item['Offset']
    rotated = item['Rotated']
    pathname = item['pathname']
    pathname = pathname.replace(".png",".jpg")
    # 使用原始大小创建图像，全透明
    image = Image.new('RGB', size, (0, 0, 0))
    # 从图集中裁剪出子图
    sprite = img.crop(box)

    # rotated纹理旋转90度
    if rotated:
        sprite = sprite.transpose(Image.ROTATE_90)

    # 粘贴子图，设置偏移
    image.paste(sprite, offset)

    img_path = os.path.join(path, pathname)
    # 保存到文件
    if not img_path.endswith("jpg") :
        img_path += ".jpg"

    Path(img_path).parent.mkdir(parents=True, exist_ok=True)
    image.save(img_path, 'jpeg')

