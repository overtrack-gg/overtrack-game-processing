import os

import tesserocr

# noinspection PyArgumentList
tesseract_mensura = tesserocr.PyTessBaseAPI(
    path=os.path.join(os.path.dirname(__file__), 'data'),
    lang='Mensura',
    oem=tesserocr.OEM.TESSERACT_ONLY,
    psm=tesserocr.PSM.SINGLE_LINE
)

# noinspection PyArgumentList
tesseract_arame = tesserocr.PyTessBaseAPI(
    path=os.path.join(os.path.dirname(__file__), 'data'),
    lang='Arame',
    oem=tesserocr.OEM.TESSERACT_ONLY,
    psm=tesserocr.PSM.SINGLE_LINE
)


tesseract_ttlakes_digits = tesserocr.PyTessBaseAPI(
    path=os.path.join(os.path.dirname(__file__), 'data'),
    lang='TT_digits',
    oem=tesserocr.OEM.TESSERACT_ONLY,
    psm=tesserocr.PSM.SINGLE_LINE
)

tesseract_ttlakes = tesserocr.PyTessBaseAPI(
    path=os.path.join(os.path.dirname(__file__), 'data'),
    lang='TTLakes_Bold',
    oem=tesserocr.OEM.TESSERACT_ONLY,
    psm=tesserocr.PSM.SINGLE_LINE
)

