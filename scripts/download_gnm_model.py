"""Cache the pinned official Apache-2.0 GNM release outside public assets."""
import argparse
import hashlib
from pathlib import Path
import urllib.request

REVISION='c01e90d298d82301f9fd18f54806be751775cb7c'
SHA256='61d78bbfb4ad8e0b38495804a4caef3214d3df00f8c3f68761e63b41ce3747eb'
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--out',type=Path,default=Path('.tools/gnm/gnm_head.npz'))
args=p.parse_args()
assert 'public' not in args.out.resolve().parts,'Raw weights cannot be public assets'
args.out.parent.mkdir(parents=True,exist_ok=True)
base=f'https://huggingface.co/google/gnm-v3/resolve/{REVISION}'
if not args.out.exists():
    temporary=args.out.with_suffix('.download')
    urllib.request.urlretrieve(base+'/v3_0/gnm_head.npz',temporary)
    assert hashlib.sha256(temporary.read_bytes()).hexdigest()==SHA256,'Model checksum mismatch'
    temporary.replace(args.out)
assert hashlib.sha256(args.out.read_bytes()).hexdigest()==SHA256,'Cached checksum mismatch'
urllib.request.urlretrieve(base+'/README.md',args.out.parent/'MODEL_CARD.md')
print('Verified official GNM V3:',args.out, args.out.stat().st_size,'bytes')
