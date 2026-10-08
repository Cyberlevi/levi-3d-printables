#!/usr/bin/env python3
"""Reproducible smooth implicit two-colour sitting cat; coordinates mm, front -Y.
Dependencies: numpy scipy scikit-image trimesh manifold3d. No slicer/printer calls.
Design by Levi / Cyberlevi with AI assistance.
SPDX-License-Identifier: CC-BY-NC-SA-4.0
White and black are complementary closed volumes, cut with Manifold booleans.
"""
from pathlib import Path
import argparse,json,time,hashlib
import numpy as np
from skimage.measure import marching_cubes
from scipy.interpolate import CubicSpline
import trimesh
import manifold3d as M
P=Path('generated')
PUBLIC_STL_NAMES={'body':'single-colour.stl','white':'white-body.stl','black':'black-details.stl'}
A=np.deg2rad(11)
C,S=np.cos(A),np.sin(A)
HEAD=np.array([-3.,-4.,99.])
ROT=np.array([[C,0,S],[0,1,0],[-S,0,C]])

def smin(a,b,k):
    h=np.maximum(k-np.abs(a-b),0)/k
    return np.minimum(a,b)-h*h*k*.25

def ell(x,y,z,center,r):
    qx=(x-center[0])/r[0]; qy=(y-center[1])/r[1]; qz=(z-center[2])/r[2]
    k0=np.sqrt(qx*qx+qy*qy+qz*qz)
    k1=np.sqrt((qx/r[0])**2+(qy/r[1])**2+(qz/r[2])**2)
    return np.where(k0<1e-6,-min(r),k0*(k0-1)/np.maximum(k1,1e-6))

def tri_sdf(x,z,vs):
    d=np.full(np.broadcast_shapes(x.shape,z.shape),1e8,dtype=np.float32)
    sign=np.ones(d.shape,dtype=np.float32)
    for i in range(3):
        a=np.asarray(vs[i]); b=np.asarray(vs[(i+1)%3]); e=b-a
        vx=x-a[0]; vz=z-a[1]
        t=np.clip((vx*e[0]+vz*e[1])/np.dot(e,e),0,1)
        d=np.minimum(d,(vx-t*e[0])**2+(vz-t*e[1])**2)
        sign=np.minimum(sign,np.sign(e[0]*vz-e[1]*vx))
    return np.sqrt(d)*np.where(sign>=0,-1,1)

def ear(x,y,z,side):
    # Broad feline triangular silhouette; both its face and thickness taper.
    # The wide base is embedded in the skull, leaving no prism ledge.
    xx=x*side
    vs=[(9,20),(23,12),(24,37)]
    d=tri_sdf(xx,z+(1.0 if side>0 else 0),vs)
    t=np.clip((z-15)/25,0,1)
    h=6.1*(1-t)+.8*t
    dy=np.abs(y-.5)-h
    outer=np.sqrt(np.maximum(d,0)**2+np.maximum(dy,0)**2)+np.minimum(np.maximum(d,dy),0)-2.35
    # A shallow soft inner cup on the front; thick supporting ear remains behind.
    cup=ell(xx,y,z,(20.3,-7.0,26.7),(5.3,3.1,8.1))
    return np.maximum(outer,-cup)

def tail_radius(f):
    return 7.2+2.0*f+.85*np.sin(np.pi*f)

PROFILE=CubicSpline([-9,0,10,25,40,58,74,86,103],[0,25,34.5,38,37.0,31.5,24.3,20.0,0],bc_type='natural')

def field(x,y,z):
    # A continuous sculpted pear loft replaces separate torso and neck ellipsoids.
    zz=np.clip(z,-9,103)
    radius=np.maximum(PROFILE(zz),.001)
    center_y=4.5-3*np.clip(z/90,0,1)
    rho=np.sqrt(x*x+((y-center_y)/.84)**2)
    body=(rho-radius)*.83
    body=np.maximum(body,np.maximum(-9-z,z-103))
    dx=x-HEAD[0]; dy=y-HEAD[1]; dz=z-HEAD[2]
    hx=C*dx-S*dz; hz=S*dx+C*dz
    head=ell(hx,dy,hz,(0,0,0),(31,24.5,25.5))
    # Barely raised paired cheek pillows, fully blended into the lower face.
    head=smin(head,ell(hx,dy,hz,(-6.5,-20.5,-6.3),(10.8,5.4,7.2)),5.2)
    head=smin(head,ell(hx,dy,hz,(6.5,-20.5,-6.3),(10.8,5.4,7.2)),5.2)
    head=smin(head,ear(hx,dy,hz,-1),5.5)
    head=smin(head,ear(hx,dy,hz,1),5.5)
    body=smin(body,head,11)
    # Readable rounded forearms lean gently inward into generously padded paws.
    # Their upper ends merge into the shoulder; the lower surfaces stand proud.
    for side in [-1,1]:
        lx=x-side*(11.2+.16*(z-10))
        ly=y-(-29.5+.24*(z-10))
        leg=ell(lx,ly,z,(0,0,24),(8.3,9.2,24.8))
        paw=ell(x,y,z,(side*11.2,-32.1,7.7),(10.0,11.4,9.4))
        leg=smin(leg,paw,3.2)
        body=smin(body,leg,2.5)
    # A visibly separate round tail wraps the haunch. Its buried inner half
    # supplies continuous structural attachment; a shallow upper groove casts
    # a real shadow line without a fragile detached ring or through-gap.
    angles=np.linspace(np.deg2rad(111),np.deg2rad(-61),53)
    pts=np.array([[38.0*np.cos(t)+11.0*max(-np.sin(t),0)**4,5.0+(31.0 if np.sin(t)>0 else 42.0)*np.sin(t)-5.0*max((i/(len(angles)-1)-.70)/.30,0)**2,7.8+1.5*(i/(len(angles)-1))+1.5*np.sin(np.pi*i/(len(angles)-1))] for i,t in enumerate(angles)])
    tail=np.full(np.broadcast_shapes(x.shape,y.shape,z.shape),1e5,dtype=np.float32)
    groove_field=np.full(tail.shape,1e5,dtype=np.float32)
    for i in range(len(pts)-1):
        a=pts[i]; b=pts[i+1]; e=b-a
        t=np.clip(((x-a[0])*e[0]+(y-a[1])*e[1]+(z-a[2])*e[2])/np.dot(e,e),0,1)
        fraction=(i+t)/(len(pts)-1)
        r=tail_radius(fraction)
        d=np.sqrt((x-a[0]-t*e[0])**2+(y-a[1]-t*e[1])**2+(z-a[2]-t*e[2])**2)-r
        tail=np.minimum(tail,d)
        if np.deg2rad(-18)<=angles[i]<=np.deg2rad(104):
            n1=np.array([np.cos(angles[i])/38,np.sin(angles[i])/(31 if np.sin(angles[i])>0 else 42),0.]);n1/=np.linalg.norm(n1)
            n2=np.array([np.cos(angles[i+1])/38,np.sin(angles[i+1])/(31 if np.sin(angles[i+1])>0 else 42),0.]);n2/=np.linalg.norm(n2)
            ga=a-n1*1.25+np.array([0,0,tail_radius(i/(len(pts)-1))*.90])
            gb=b-n2*1.25+np.array([0,0,tail_radius((i+1)/(len(pts)-1))*.90])
            ge=gb-ga
            gt=np.clip(((x-ga[0])*ge[0]+(y-ga[1])*ge[1]+(z-ga[2])*ge[2])/np.dot(ge,ge),0,1)
            gd=np.sqrt((x-ga[0]-gt*ge[0])**2+(y-ga[1]-gt*ge[1])**2+(z-ga[2]-gt*ge[2])**2)-1.15
            groove_field=np.minimum(groove_field,gd)
    body=smin(body,tail,1.15)
    body=-smin(-body,groove_field,.55)
    # The central valley and short rounded toe notches separate two full paws.
    for side in [-1,1]:
        for off in [-2.8,2.8]:
            groove=ell(x,y,z,(side*11.2+off,-43.4,5.8),(.48,.65,2.8))
            body=np.maximum(body,-groove)
    return np.maximum(body,.0-z).astype(np.float32)

def to_manifold(tm):
    tm.remove_unreferenced_vertices()
    return M.Manifold(M.Mesh(np.asarray(tm.vertices,dtype=np.float32),np.asarray(tm.faces,dtype=np.uint32)))

def to_tri(m):
    out=m.to_mesh()
    return trimesh.Trimesh(np.asarray(out.vert_properties[:,:3]),np.asarray(out.tri_verts),process=False)

def extract(vals,origin,step,level):
    v,f,n,_=marching_cubes(vals,level=level,spacing=(step,step,step),allow_degenerate=False)
    v+=origin
    tm=trimesh.Trimesh(v,f,process=True)
    # skimage's convention is opposite the interior-negative SDF.
    if tm.volume<0: tm.invert()
    # Six Taubin passes remove grid anisotropy without smoothing colour borders.
    # Pin all planar contact vertices at each pass to retain exact flat Z=0.
    anchor=tm.vertices[:,2] < .025 if level==0 else np.zeros(len(tm.vertices),dtype=bool)
    original=tm.vertices[anchor].copy()
    lap=trimesh.smoothing.laplacian_calculation(tm,equal_weight=True,pinned_vertices=np.flatnonzero(anchor))
    for weight in [.33,-.34]*3:
        tm.vertices += weight*(lap.dot(tm.vertices)-tm.vertices)
        tm.vertices[anchor]=original
    m=to_manifold(tm)
    if m.status()!=M.Error.NoError: raise RuntimeError(f'Implicit mesh manifold failure: {m.status()}')
    return m.simplify(.028)

def ell_m(center,r):
    return M.Manifold.sphere(1,72).scale(r).translate(center)

def prism(poly,origin,u,v,depth=(-18,18)):
    sec=M.CrossSection([np.asarray(poly,dtype=np.float64)],M.FillRule.EvenOdd)
    # x=u, y=v, extrusion=normal; arbitrary frame may reflect, handled by transform.
    u=np.asarray(u);v=np.asarray(v);n=np.cross(u,v);origin=np.asarray(origin)+n*depth[0]
    transform=np.column_stack([u,v,n,origin])
    return sec.extrude(depth[1]-depth[0]).transform(transform)

def face_prism(poly):
    origin=HEAD+ROT@np.array([0,-18,0.])
    return prism(poly,origin,ROT[:,0],ROT[:,2],(-18,20))

def capsule_path(points,radii):
    # Convex hull of neighbouring smooth circles creates robust round-ended strokes.
    result=[]
    for i in range(len(points)-1):
        t=np.linspace(0,2*np.pi,20,endpoint=False)
        p=np.array(points[i]);q=np.array(points[i+1])
        allp=np.concatenate([p+np.column_stack([np.cos(t),np.sin(t)])*radii[i],q+np.column_stack([np.cos(t),np.sin(t)])*radii[i+1]])
        from scipy.spatial import ConvexHull
        result.append(face_prism(allp[ConvexHull(allp).vertices]))
    return M.Manifold.batch_boolean(result,M.OpType.Add)

def cutters():
    patches=[]
    # Upturned sleeping eyelids: narrow ends, a full soft upper arch.
    for side in [-1,1]:
        t=np.linspace(-1,1,17)
        pts=np.column_stack([side*12+t*5.2,4.8+2.6*(1-t*t)])
        radii=.32+.64*np.sin(np.linspace(0,np.pi,len(t)))
        patches.append(capsule_path(pts,radii))
    # Rounded triangular nose and a gently smiling W-shaped mouth.
    nose=M.CrossSection([[[-2.8,-2.5],[2.8,-2.5],[0,-5.6]]],M.FillRule.EvenOdd).offset(.7, M.JoinType.Round, circular_segments=32)
    nosepoly=nose.to_polygons()[0]
    patches.append(face_prism(nosepoly))
    patches.append(capsule_path([[0,-5],[0,-7.6]], [.65,.62]))
    for side in [-1,1]:
        t=np.linspace(0,1,12)
        pts=np.column_stack([side*4.8*t,-7.4-2.2*np.sin(np.pi*t*.9)])
        patches.append(capsule_path(pts,np.linspace(.65,.42,len(t))))
    # Anatomical left (viewer right) flank heart, projected onto the curved body.
    t=np.linspace(0,2*np.pi,140,endpoint=False)
    heart=np.column_stack([16*np.sin(t)**3,13*np.cos(t)-5*np.cos(2*t)-2*np.cos(3*t)-np.cos(4*t)])*.59
    a=np.deg2rad(44)
    patches.append(prism(heart,(28.0,-13,40),(np.cos(a),np.sin(a),0),(0,0,1),(-12,15)))
    # Broad organic spots at the shoulder, opposite flank, and back.
    patches.append(ell_m((-30,-1,48),(8,13,13)))
    patches.append(ell_m((19,5,74),(9,14,12)))
    patches.append(ell_m((-14,27,57),(13,9,12)))
    patches.append(ell_m((13,29,25),(12,9,14)))
    patches.append(ell_m((-27,14,21),(9,12,11)))
    # Whole black ear and tail end are structurally sound full-depth coloured volumes.
    earcut=ell_m((-24,0,43),(20,22,28)).transform(np.column_stack([ROT,HEAD]))
    tip=ell_m((25.0,-38.0,9.3),(11.8,12.1,11.8))
    protect=ell_m((11.2,-32.1,7.7),(10.7,12.0,10.1))+ell_m((12.0,-27.8,18),(9.0,10.0,12.8))
    tip=tip-protect.hull()
    return M.Manifold.batch_boolean(patches,M.OpType.Add),earcut+tip

def stats(m):
    t=to_tri(m)
    parts=t.split(only_watertight=False)
    return {'vertices':len(t.vertices),'triangles':len(t.faces),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'volume_mm3':float(t.volume),'components':len(parts),'component_volumes_mm3':sorted([float(p.volume) for p in parts],reverse=True),'bounds_mm':t.bounds.tolist(),'dimensions_mm':t.extents.tolist(),'manifold_status':str(m.status())}

def main():
    global P
    ap=argparse.ArgumentParser();ap.add_argument('--step',type=float,default=.32);ap.add_argument('--cached',action='store_true');ap.add_argument('--rough',action='store_true');ap.add_argument('--output',type=Path,default=Path('generated'),help='Output directory (default: ./generated)');args=ap.parse_args();step=args.step
    P=args.output.expanduser().resolve();P.mkdir(parents=True,exist_ok=True)
    started=time.time();origin=np.array([-49.,-48.,-3.],dtype=np.float32)
    axes=[np.arange(origin[i],end+step,step,dtype=np.float32) for i,end in enumerate([49,48,152])]
    if args.cached:
        body=to_manifold(trimesh.load(P/'body-raw.stl',force='mesh'))
        inner=to_manifold(trimesh.load(P/'inner-raw.stl',force='mesh'))
    else:
        vals=np.empty(tuple(map(len,axes)),dtype=np.float32)
        print('Sampling grid',vals.shape,flush=True)
        for i in range(0,len(axes[0]),12):
            vals[i:i+12]=field(axes[0][i:i+12,None,None],axes[1][None,:,None],axes[2][None,None,:])
        print('Extracting body',time.time()-started,flush=True)
        body=extract(vals,origin,step,0)
        if args.rough:
            rough_tm=to_tri(body)
            rough_scale=140/rough_tm.extents[2]
            body=body.translate((0,0,-rough_tm.bounds[0,2])).scale((rough_scale,)*3)
            to_tri(body).export(P/PUBLIC_STL_NAMES['body'])
            info=stats(body);info.update({'stage':'rough body only, before colour booleans','grid_step_mm':step,'scale_to_140mm':rough_scale})
            (P/'rough-statistics.json').write_text(json.dumps(info,ensure_ascii=False,indent=2))
            print(json.dumps(info),flush=True)
            return
        inner=extract(vals,origin,step,-1.65)
        to_tri(body).export(P/'body-raw.stl')
        to_tri(inner).export(P/'inner-raw.stl')
    # Set exact height, preserve a true planar Z=0 contact patch.
    full=to_tri(body); height=full.bounds[1,2]-full.bounds[0,2];scale=140/height
    print('Constructing colour volumes',time.time()-started,'body faces',len(full.faces),flush=True)
    patch,solid= cutters()
    colour_mask=(patch-inner)+solid
    black=body^colour_mask
    white=body-colour_mask
    for name,m in [('body',body),('white',white),('black',black)]:
        if m.status()!=M.Error.NoError or m.is_empty(): raise RuntimeError(name+' boolean invalid '+str(m.status()))
    zbase=full.bounds[0,2]
    body=body.translate((0,0,-zbase)).scale((scale,scale,scale))
    white=white.translate((0,0,-zbase)).scale((scale,scale,scale))
    black=black.translate((0,0,-zbase)).scale((scale,scale,scale))
    data={'design':'Pöttyös cica V3, 140 mm; distinct rounded forearms, padded paws and a separate-looking wrapped round tail','front':'negative Y','black_patch_nominal_depth_mm':1.65*scale,'grid_step_mm_before_scale':step,'scale_to_140mm':scale}
    for name,m in [('body',body),('white',white),('black',black)]:
        tm=to_tri(m);tm.export(P/PUBLIC_STL_NAMES[name]);data[name]=stats(m)
        saved=trimesh.load(P/PUBLIC_STL_NAMES[name],force='mesh',process=True)
        data[name]['stl_roundtrip_watertight']=bool(saved.is_watertight)
        data[name]['stl_roundtrip_winding_consistent']=bool(saved.is_winding_consistent)
        data[name]['stl_roundtrip_degenerate_faces']=int((~saved.nondegenerate_faces()).sum())
        data[name]['center_mass_mm']=saved.center_mass.tolist()
        data[name]['bounding_box_midpoint_mm']=saved.bounds.mean(axis=0).tolist()
        print(name,data[name]['dimensions_mm'],data[name]['triangles'],data[name]['watertight'],data[name]['components'],flush=True)
    data['black_white_overlap_volume_mm3']=(white^black).volume()
    data['partition_volume_error_mm3']=abs(body.volume()-(white+black).volume())
    base_tm=to_tri(body)
    base_faces=base_tm.triangles[:,:,2].max(axis=1)<1e-5
    data['base_contact_area_mm2']=float(base_tm.area_faces[base_faces].sum())
    data['stl_sha256']={name:hashlib.sha256((P/name).read_bytes()).hexdigest() for name in PUBLIC_STL_NAMES.values()}
    for name in ['body','white','black']:
        if not data[name]['stl_roundtrip_watertight'] or data[name]['stl_roundtrip_degenerate_faces']:
            raise RuntimeError(name+' STL round-trip validation failed')
    if data['body']['components']!=1 or data['white']['components']!=1:
        raise RuntimeError('Unexpected disconnected white/body component')
    data['generation_seconds']=time.time()-started
    (P/'mesh-statistics.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    print('Finished',data['generation_seconds'],flush=True)
if __name__=='__main__':main()
