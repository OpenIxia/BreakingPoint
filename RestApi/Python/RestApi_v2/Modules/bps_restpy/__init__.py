import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())
log.setLevel(logging.INFO)