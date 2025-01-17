#/usr/bin/env python
#author: lgpang
#email: lgpang@qq.com
#createTime: Fr 29 Apr 2016 11:44:06 CEST

from sampler import main
import time
from multiprocessing import Pool
from subprocess import call


def f(eid):
    t1 = time.time()
    fpath = "/lustre/nyx/hyihp/lpang/trento_ebe_hydro/results/6_15/event%s/"%eid
    fsrc = "/lustre/nyx/hyihp/lpang/trento_ebe_hydro/PyVisc/sampler/mcspec/pdg05.dat"
    call(['cp', fsrc, fpath])
    try:
        viscous_on = 'true'
        force_decay = 'true'
        main(fpath, viscous_on, force_decay, nsampling=1000)
        print(eid, 'finished')
    except:
        print(eid, ' hydro not finished')

    t2 = time.time()

    print('it takes ', t2 - t1, 's for 100 events')


if __name__ == '__main__':
    p = Pool(12)
    p.map(f, range(100))
