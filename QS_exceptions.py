# noinspection PyPep8Naming
class PDF_Exception(ValueError):
    """
    Eccezione lanciata nel caso in cui la pdf passata come parametro non sia corretta: ovvero, una tra quelle gestite 
    dalla libreria
    """

    def __init__(self, paramToCheck, pdf):
        super(PDF_Exception, self).__init__('"%s" - chosen PDF ("%s") is not valid' % (paramToCheck, pdf))
