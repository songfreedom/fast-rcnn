# --------------------------------------------------------
# Fast R-CNN
# Copyright (c) 2015 Microsoft
# Licensed under The MIT License [see LICENSE for details]
# Written by Ross Girshick
# --------------------------------------------------------

"""Factory method for easily getting imdbs by name."""

__sets = {}

import datasets.pascal_voc
import datasets.imagenet
import numpy as np

def _selective_search_IJCV_top_k(split, year, top_k):
    """Return an imdb that uses the top k proposals from the selective search
    IJCV code.
    """
    imdb = datasets.pascal_voc(split, year)
    imdb.roidb_handler = imdb.selective_search_IJCV_roidb
    imdb.config['top_k'] = top_k
    return imdb

def _init_imdb(model_to_use, proposal, proposal_file):
    # Set up voc_<year>_<split> using selective search "fast" mode
    for year in ['2007', '2012', '2007_2012']:
        for split in ['train', 'val', 'trainval', 'test']:
            name = 'voc_{}_{}'.format(year, split)
            __sets[name] = (lambda split=split, year=year:
                    datasets.pascal_voc(split, year, model_to_use, proposal, proposal_file))
    
    # Set up voc_<year>_<split>_top_<k> using selective search "quality" mode
    # but only returning the first k boxes
    for top_k in np.arange(1000, 11000, 1000):
        for year in ['2007', '2012']:
            for split in ['train', 'val', 'trainval', 'test']:
                name = 'voc_{}_{}_top_{:d}'.format(year, split, top_k)
                __sets[name] = (lambda split=split, year=year, top_k=top_k:
                        _selective_search_IJCV_top_k(split, year, top_k))
                
    for split in ['train', 'val', 'val_10', 'val_2000', 'test']:
        name = 'imagenet_{}'.format(split)
        __sets[name] = (lambda split=split:
                datasets.imagenet(split, model_to_use, proposal, proposal_file))
            

def get_imdb(name, model_to_use='frcnn', proposal='ss', proposal_file=''):
    """Get an imdb (image database) by name."""
    
    if len(__sets) == 0:
        _init_imdb(model_to_use, proposal, proposal_file)
    
    if not __sets.has_key(name):
        raise KeyError('Unknown dataset: {}'.format(name))
    return __sets[name]()

def list_imdbs():
    """List all registered imdbs."""
    return __sets.keys()
