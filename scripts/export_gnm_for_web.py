"""Export official GNM neutral geometry; never export model bases or identities.

Inspected against gnm-shape 3.0.0. Runtime/model validation remains required.
Uses only a supplied local model file; never downloads weights implicitly.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--model-file', type=Path, required=True)
    p.add_argument('--out', type=Path, default=Path('gnm-export'))
    p.add_argument('--rights-note', required=True, help='Asset-specific redistribution evidence, separate from code license')
    p.add_argument('--unit-to-metres', type=float, required=True)
    p.add_argument('--front', choices=['+z','-z'], required=True, help='Visually validated source front direction; Y must be up')
    p.add_argument('--poses', type=Path, help='Optional curated JSON: name -> expression vector and joint rotations; never published')
    args = p.parse_args()
    repo = args.repo.resolve()
    if not (repo/'gnm/shape/gnm_numpy.py').is_file():
        p.error('Not an official GNM source layout')
    config = subprocess.check_output(['git','-c',f'safe.directory={repo.as_posix()}','-C',str(repo),'config','--get','remote.origin.url'],text=True).strip()
    if config.lower().removesuffix('.git') not in ('https://github.com/google/gnm','git@github.com:google/gnm'):
        p.error('Origin must be official google/GNM')
    if not args.model_file.is_file(): p.error('Local model file missing; consult upstream model asset instructions')
    if args.unit_to_metres <= 0: p.error('Scale must be positive')
    sys.dont_write_bytecode = True  # The research checkout is strictly read-only.
    sys.path.insert(0,str(repo))
    import numpy as np
    from gnm.shape import gnm_numpy
    model = gnm_numpy.GNM.from_custom_file(str(args.model_file.resolve()))
    vertices = np.asarray(model.template_vertex_positions,dtype=np.float32)
    faces = np.asarray(model.triangles,dtype=np.uint32)
    assert vertices.ndim == 2 and vertices.shape[1] == 3 and np.isfinite(vertices).all()
    assert faces.ndim == 2 and faces.shape[1] == 3 and faces.max() < len(vertices)
    assert np.all(faces[:,0]!=faces[:,1]) and np.all(faces[:,1]!=faces[:,2]) and np.all(faces[:,2]!=faces[:,0])
    identity=np.zeros(model.identity_dim)
    neutral=np.asarray(model(identity,np.zeros(model.expression_dim),np.zeros((model.num_joints,3)),np.zeros(3)))
    assert np.allclose(neutral,vertices,atol=1e-5), 'Zero-parameter output differs from template; inspect version'
    rotation=np.diag([-1,1,-1] if args.front=='-z' else [1,1,1])
    transform=lambda v: np.asarray(v @ rotation * args.unit_to_metres,dtype='<f4')
    vertices=transform(vertices)
    def normals(v):
        n=np.zeros_like(v);tri=v[faces];cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
        for i in range(3): np.add.at(n,faces[:,i],cross)
        return n/np.maximum(np.linalg.norm(n,axis=1,keepdims=True),1e-12)
    base_normals=normals(vertices)
    pose_data=json.loads(args.poses.read_text()) if args.poses else {}
    assert len(pose_data)<=5,'Keep a curated set of at most five poses'
    targets=[]
    pose_statistics={}
    for name,pose in pose_data.items():
        expression=np.asarray(pose['expression'],dtype=np.float32)
        joints=np.asarray(pose.get('rotations',np.zeros((model.num_joints,3))),dtype=np.float32)
        assert expression.shape==(model.expression_dim,) and joints.shape==(model.num_joints,3)
        v=transform(model(identity,expression,joints,np.zeros(3)))
        assert v.shape==vertices.shape and np.isfinite(v).all()
        assert np.array_equal(model.triangles,faces),'Pose topology changed'
        assert np.max(np.abs(v-vertices))>1e-7,f'{name}: no deformation'
        targets.append((v-vertices,normals(v)-base_normals))
        distances=np.linalg.norm(v-vertices,axis=1)
        pose_statistics[name]={'maximum_displacement_metres':float(distances.max()),'rms_displacement_metres':float(np.sqrt(np.mean(distances**2))),'source':pose.get('provenance','Explicit curated GNM coefficients')}
    binary=bytearray();views=[];accessors=[]
    def accessor(array,kind,component):
        nonlocal binary
        array=np.ascontiguousarray(array)
        while len(binary)%4: binary.append(0)
        offset=len(binary);binary.extend(array.tobytes())
        views.append({'buffer':0,'byteOffset':offset,'byteLength':array.nbytes})
        a={'bufferView':len(views)-1,'componentType':component,'count':len(array),'type':kind}
        if kind=='VEC3':a.update(min=array.min(axis=0).tolist(),max=array.max(axis=0).tolist())
        accessors.append(a);return len(accessors)-1
    attrs={'POSITION':accessor(vertices,'VEC3',5126),'NORMAL':accessor(base_normals.astype('<f4'),'VEC3',5126)}
    morphs=[{'POSITION':accessor(v.astype('<f4'),'VEC3',5126),'NORMAL':accessor(n.astype('<f4'),'VEC3',5126)} for v,n in targets]
    # Material assignment uses actual upstream vertex-group memberships.
    palette=[('skin',[.72,.68,.61,1]),('mouth_sock',[.13,.10,.09,1]),('gums',[.37,.22,.20,1]),('teeth',[.90,.87,.78,1]),('tongue',[.40,.24,.23,1]),('scleras',[.82,.80,.73,1]),('irises',[.20,.17,.12,1]),('pupils',[.025,.023,.02,1]),('eye_exteriors',[.9,.9,.9,.05])]
    assignment=np.zeros(len(faces),dtype=int)
    for i,(name,_) in enumerate(palette[1:],1):
        if name in model.vertex_group_names:
            membership=np.asarray(model.vertex_group(name))[faces].mean(axis=1)
            assignment[membership>.5]=i
    primitives=[];materials=[];parts={}
    for i,(name,color) in enumerate(palette):
        subset=faces[assignment==i]
        if not len(subset): continue
        parts[name]=len(subset)
        material={'name':name,'pbrMetallicRoughness':{'baseColorFactor':color,'metallicFactor':0,'roughnessFactor':.78},'doubleSided':False}
        if color[3]<1: material.update(alphaMode='BLEND')
        primitive={'attributes':attrs,'indices':accessor(subset.astype('<u4').reshape(-1),'SCALAR',5125),'material':len(materials)}
        if targets:primitive['targets']=morphs
        primitives.append(primitive);materials.append(material)
    assert sum(parts.values())==len(faces)
    mesh={'primitives':primitives,'name':'GNM neutral template','extras':{'targetNames':list(pose_data)}}
    if targets:mesh['weights']=[0]*len(targets)
    gltf={'asset':{'version':'2.0','generator':'GNM website exporter; inspected gnm-shape 3.0.0'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'mesh':0}],'meshes':[mesh],'materials':materials,'buffers':[{'byteLength':len(binary)}],'bufferViews':views,'accessors':accessors}
    raw=json.dumps(gltf,separators=(',',':')).encode()
    raw+=b' '*((-len(raw))%4);binary+=b'\0'*((-len(binary))%4)
    glb=struct.pack('<III',0x46546c67,2,12+8+len(raw)+8+len(binary))+struct.pack('<II',len(raw),0x4e4f534a)+raw+struct.pack('<II',len(binary),0x004e4942)+binary
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/'face.glb').write_bytes(glb)
    sha=subprocess.check_output(['git','-c',f'safe.directory={repo.as_posix()}','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
    manifest={'source':'google/GNM neutral template','asset':'/assets/face.glb','vertices':len(vertices),'triangles':len(faces),'morph_names':list(pose_data),'asset_bytes':len(glb),'sha256':hashlib.sha256(glb).hexdigest(),'upstream_commit':sha,'unit_to_metres':args.unit_to_metres,'source_front':args.front,'coordinate_transform':'right-handed, Y up; optional 180-degree Y rotation; original winding preserved','bounds_metres':[vertices.min(axis=0).tolist(),vertices.max(axis=0).tolist()],'materials':list(parts),'part_triangles':parts,'texture_available':False,'source_uv_available':hasattr(model,'triangle_uvs'),'source_component_names':[str(n) for n in model.mesh_component_names],'rights_evidence':args.rights_note,'limitations':['Untextured full topology retained; UV seams are not exported because no textures are used.','Material boundaries use majority upstream vertex-group membership.','Baked joint poses interpolate as morph deltas, not exact continuous joint rotations.','GNM expressions are not the separate Audio2Motion representation.']}
    manifest['pose_statistics']=pose_statistics
    manifest['model_sha256']=hashlib.sha256(args.model_file.read_bytes()).hexdigest()
    manifest['model_release']='google/gnm-v3@c01e90d298d82301f9fd18f54806be751775cb7c' if manifest['model_sha256']=='61d78bbfb4ad8e0b38495804a4caef3214d3df00f8c3f68761e63b41ce3747eb' else 'Local input; release not independently verified'
    (args.out/'face-manifest.json').write_text(json.dumps(manifest,indent=2))
    (args.out/'GNM-LICENSE.txt').write_text((repo/'LICENSE').read_text(encoding='utf-8'))
    (args.out/'GNM-NOTICE.txt').write_text('GNM Head — Google LLC. https://github.com/google/GNM\nSee upstream citation: Ploumpis et al., GNM Head, 2026, arXiv:2607.23687.\nAsset permissions evidence: '+args.rights_note,encoding='utf-8')
    print(json.dumps({'vertices':len(vertices),'triangles':len(faces),'bytes':len(glb),'output':str(args.out)}))

if __name__=='__main__':main()
