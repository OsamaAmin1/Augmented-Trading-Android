"""Bounded branch-and-bound compatibility for SciPy 1.8 HiGHS linprog.
Returns optimal only after all open nodes are pruned. No heuristic orders on timeout.
"""
import time, heapq, itertools, math
import numpy as np
from scipy.optimize import linprog, OptimizeResult

def milp(c, *, integrality, bounds, constraints, options=None):
    options=options or {}; deadline=time.monotonic()+float(options.get('time_limit',5)); gap=float(options.get('mip_rel_gap',1e-8)); c=np.asarray(c,float); n=len(c)
    if not np.all(np.isin(integrality,[0,1])):raise ValueError('Unsupported integer type')
    a=np.asarray(constraints.A,float); lo=np.broadcast_to(constraints.lb,(len(a),)); hi=np.broadcast_to(constraints.ub,(len(a),)); upper=[]; rhs=[]; eq=[]; erhs=[]
    for row,l,u in zip(a,lo,hi):
        if np.isfinite(l) and np.isfinite(u) and l==u:eq.append(row);erhs.append(l)
        else:
            if np.isfinite(u):upper.append(row);rhs.append(u)
            if np.isfinite(l):upper.append(-row);rhs.append(-l)
    lb=np.broadcast_to(bounds.lb,(n,));ub=np.broadcast_to(bounds.ub,(n,)); root=[(float(l),None if np.isposinf(u) else float(u)) for l,u in zip(lb,ub)]
    ids=np.flatnonzero(integrality); best=None; bestval=math.inf; nodes=0; queue=[]; seq=itertools.count()
    def lp(b):
        remaining=deadline-time.monotonic()
        if remaining<=0: return None
        return linprog(c,A_ub=np.array(upper) if upper else None,b_ub=rhs or None,A_eq=np.array(eq) if eq else None,b_eq=erhs or None,bounds=b,method='highs',options={'time_limit':remaining})
    def fail(message):return OptimizeResult(status=1,x=None,message=message,mip_gap=math.inf)
    def tol():return gap*max(abs(bestval),1e-8)+1e-11
    heapq.heappush(queue,(-math.inf,next(seq),root))
    while queue:
        bound,_,b=heapq.heappop(queue)
        if best is not None and bound>=bestval-tol():continue
        if nodes>=20000:return fail('Integer node limit; no certified solution')
        r=lp(b); nodes+=1
        if r is None:return fail('Integer time limit; no certified solution')
        if r.status==2:continue
        if r.status!=0:return fail('LP relaxation not solved: '+str(r.message))
        if best is not None and r.fun>=bestval-tol():continue
        fractions=[(abs(r.x[j]-round(r.x[j])),int(j)) for j in ids]; frac,j=max(fractions,default=(0,0))
        if frac<=1e-7:
            # Fix rounded integers and re-solve the continuous risk variables.
            fixed=list(b)
            for k in ids:fixed[k]=(float(round(r.x[k])),float(round(r.x[k])))
            z=lp(fixed)
            if z is None or z.status!=0:return fail('Integer solution could not be certified')
            if z.fun<bestval:best=z.x;bestval=float(z.fun)
            continue
        l,u=b[j]; floor=math.floor(r.x[j]);ceil=floor+1
        for nl,nu in [(l,min(u,floor) if u is not None else floor),(max(l,ceil),u)]:
            if nu is not None and nl>nu:continue
            child=list(b);child[j]=(nl,nu);heapq.heappush(queue,(float(r.fun),next(seq),child))
    if best is None:return OptimizeResult(status=2,x=None,message='Integer problem infeasible',mip_gap=0.)
    return OptimizeResult(status=0,x=best,fun=bestval,message='Integer optimality certified within configured tolerance',mip_gap=gap)
