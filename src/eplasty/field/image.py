import pystacia

from eplasty.field.blob import Blob, BlobData

class Image(Blob):
    img_format = 'jpeg'
    cheap = False

    def __init__(self, *args, **kwargs):
        super(Image, self).__init__(
            *args, mimetype=('image/' + self.img_format), **kwargs
        )

    def hydrate(self, inst, col_vals, dict_, session):
        super(Image, self).hydrate(inst, col_vals, dict_, session)
        blob = dict_.get(self.name)
        if blob and blob.data is not None:
            dict_[self.name] = pystacia.read_blob(blob.data, self.img_format)
            dict_[self.name].filename =  blob.filename
        else:
            dict_[self.name] = None

    def get_c_vals(self, dict_):
        dict_ = dict_.copy()
        if dict_.get(self.name) is not None:
            dict_[self.name] = BlobData(
                dict_[self.name].get_blob(self.img_format),
                'image/' + self.img_format,
                dict_[self.name].filename,
            )
        
        return super(Image, self).get_c_vals(dict_)

    def _is_compatible(self, value):
        return value is None or isinstance(value, pystacia.Image)

class Thumb(Image):
    def __init__(self, *args, **kwargs):
        origin = kwargs.pop('origin')
        self.size = kwargs.pop('size')
        origin.dependent_fields.append(self)
        self.origin = origin
        super(Thumb, self).__init__(*args, **kwargs)

    def set_dependent(self, inst, img):
        to_width, to_height = self.size
        factor = min(to_width/img.width, to_height/img.height)
        filename = 'thumb_' + img.filename
        img = img.copy()
        if factor < 1:
            img.rescale(factor=factor)
        img.filename = filename
        self.__set__(inst, img)
        return img
