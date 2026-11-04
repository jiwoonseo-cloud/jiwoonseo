"""Exact per-frame deformation of CURVE hair from keyframed wind/slide controls.
Geometric interpolation through the metal core is avoided; no raster interpolation.
"""
import bpy,math,numpy as np
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def coordinates(wind,slide,count=36,N=96):
 rad=.336-(.336-.095)*smooth((slide-.95)/.05)
 # Bulk RNA writes keep the exact same geometry without thousands of costly
 # individual dependency-graph invalidations for every control point.
 k=np.arange(count,dtype=float)[:,None];s=np.linspace(0,1,N)[None,:]
 jitter=.052*np.sin(k*2.399);wk=np.minimum(1,wind*(.84+.27*(.5+.5*np.sin(k*1.77))));wrapped=wk*4.5/4.8;angle=wk*4.5/rad
 r=rad+.011*np.sin(k*1.91)+.003*np.sin(s*21+k);uw=s/np.maximum(.000001,wrapped);theta=-math.pi/2+(1-uw)*(angle+wk*np.mod(k*2.399,math.tau))
 xw=jitter+.027*np.sin(theta*1.7+k)+.025*(1-uw);yw=r*np.cos(theta);zw=r*np.sin(theta)
 ut=(s-wrapped)/np.maximum(.001,1-wrapped);xt=jitter+ut*np.sin(k*2.399)*.52*(1-wind*.8)+.023*np.sin(ut*11+k*.7);yt=-(4.8-wk*4.5)*ut*(.80+.32*(.5+.5*np.sin(k*1.77)));zt=-rad-(.34-rad)*np.minimum(1,ut*7)
 mask=(s<wrapped)&(wrapped>0);tight=1-.86*smooth((slide-.84)/.16);co=np.ones((count,N,4),dtype=np.float32);co[:,:,0]=np.where(mask,xw,xt)*tight;co[:,:,1]=np.where(mask,yw,yt);co[:,:,2]=np.maximum(-.334,np.where(mask,zw,zt))
 return co
def evaluate(scene):
 o=bpy.data.objects.get('36 separate animated human hairs')
 if o is None or o.get('baked_native',False):return
 co=coordinates(float(o['wind']),float(o['slide']),len(o.data.splines),len(o.data.splines[0].points))
 for sp,values in zip(o.data.splines,co):sp.points.foreach_set('co',values.ravel())
 o.data.update_tag()
