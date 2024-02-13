import os
import logging

logging.basicConfig(
    format='[ %(asctime)s %(levelname)s %(filename)s ] %(message)s',
    datefmt='%H:%M:%S',
    level=os.environ.get('PYTHONLOGLEVEL', 'WARNING').upper(),
)
logging.captureWarnings(True)
# logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
Logger = logging.getLogger(__name__)

def models(df):
    items = list(map('model_{}'.format, range(1, 3)))
    yield from (df
                .filter(items=items)
                .unstack()
                .unique())
