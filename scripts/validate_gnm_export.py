"""Compare exported GLB geometry/morphs with independent official GNM evaluations."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--repo',type=Path,required=True)
p.add_argument('--model-file',type=Path,required=True)
p.add_argument('--poses',type=Path,required=True)
p.add_argument('--assets',type=Path,default=Path('public/assets'))
args=p.parse_args()
sys.dont_write_bytecode=True
sys.path.insert(0,str(args.repo.resolve()))
import numpy as np
from gnm.shape import gnm_numpy

model=gnm_numpy.GNM.from_custom_file(str(args.model_file))
data=(args.assets/'face.glb').read_bytes()
magic,version,total=struct.unpack_from('<III',data)
assert magic==0x46546c67 and version==2 and total==len(data)
json_size=struct.unpack_from('<I',data,12)[0]
document=json.loads(data[20:20+json_size])
binary=data[28+json_size:]
def read(index):
    accessor=document['accessors'][index]
    view=document['bufferViews'][accessor['bufferView']]
    width={'SCALAR':1,'VEC3':3}[accessor['type']]
    dtype={5126:'<f4',5125:'<u4'}[accessor['componentType']]
    offset=view.get('byteOffset',0)+accessor.get('byteOffset',0)
    return np.frombuffer(binary,dtype=dtype,count=accessor['count']*width,offset=offset).reshape(accessor['count'],width)

mesh=document['meshes'][0]
primitive=mesh['primitives'][0]
positions=read(primitive['attributes']['POSITION'])
assert np.allclose(positions,model.template_vertex_positions,atol=1e-7)
exported=np.concatenate([read(part['indices']).reshape(-1,3) for part in mesh['primitives']])
assert sorted(map(tuple,exported.tolist()))==sorted(map(tuple,model.triangles.tolist()))
poses=json.loads(args.poses.read_text())
names=mesh['extras']['targetNames']
for i,name in enumerate(names):
    params=poses[name]
    expected=model(np.zeros(model.identity_dim),np.array(params['expression']),np.array(params.get('rotations',np.zeros((model.num_joints,3)))),np.zeros(3))
    delta=read(primitive['targets'][i]['POSITION'])
    assert np.allclose(positions+delta,expected,atol=1e-7),name
    assert np.max(np.linalg.norm(delta,axis=1))>.001,name
manifest=json.loads((args.assets/'face-manifest.json').read_text())
assert manifest['sha256']==hashlib.sha256(data).hexdigest()
assert len(names)==5 and len(mesh['primitives'])==9
assert not list(args.assets.glob('*.npz')) and not list(args.assets.glob('*.h5'))
print(json.dumps({'neutral_matches':True,'triangle_topology_matches':True,'five_morphs_match_official_evaluator':True,'materials':len(mesh['primitives']),'vertices':len(positions),'triangles':len(exported),'bytes':len(data)},indent=2))
