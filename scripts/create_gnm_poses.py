"""Bake semantic presets using the official GNM ExpressionSampler, offline only."""
import argparse
import json
from pathlib import Path
import sys

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--repo',type=Path,required=True)
p.add_argument('--out',type=Path,default=Path('.tools/gnm/curated-poses.json'))
args=p.parse_args()
sys.dont_write_bytecode=True
sys.path.insert(0,str(args.repo.resolve()))
import numpy as np
from gnm.shape import semantic_sampler

sampler=semantic_sampler.ExpressionSampler()
presets={
    'jaw_open':semantic_sampler.Expression.SURPRISE,
    'smile':semantic_sampler.Expression.HAPPY,
    'wide_smile':semantic_sampler.Expression.SMILE_WIDE,
    'pucker':semantic_sampler.Expression.PUCKER,
    'wink_left':semantic_sampler.Expression.WINK_LEFT,
}
poses={}
for name,label in presets.items():
    values=sampler.sample_expression(label,num_samples=16,rng=np.random.default_rng(42)).mean(axis=0)
    assert np.isfinite(values).all()
    poses[name]={'expression':values.tolist(),'provenance':f'Official ExpressionSampler.{label.name}; mean of 16 samples; seed 42'}
args.out.parent.mkdir(parents=True,exist_ok=True)
args.out.write_text(json.dumps(poses,indent=2))
print('Created official semantic poses:',', '.join(poses))
