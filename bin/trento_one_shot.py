#/usr/bin/env python
#author: lgpang
#email: lgpang@qq.com

import numpy as np
from subprocess import call
import os
from time import time
from glob import glob
import pyopencl as cl
import matplotlib.pyplot as plt
import h5py
from scipy.interpolate import InterpolatedUnivariateSpline

import os, sys
cwd, cwf = os.path.split(__file__)
print('cwd=', cwd)

sys.path.append(os.path.join(cwd, '../pyvisc'))
from config import cfg, write_config
from visc import CLVisc
from ini.trento import AuAu200, PbPb2760, PbPb5020

import h5py

def from_sd_to_ed(entropy, eos):
    '''using eos to  convert the entropy density to energy density'''
    s = eos.s
    ed = eos.ed
    # the InterpolatedUnivariateSpline works for both interpolation
    # and extrapolation
    f_ed = InterpolatedUnivariateSpline(s, ed, k=1)
    return f_ed(entropy)


def ebehydro(fpath, cent='0_5', etaos=0.12, gpu_id=0, system='pbpb2760', oneshot=False):
    ''' Run event_by_event hydro, with initial condition 
    from smearing on the particle list'''

    fout = fpath
    if not os.path.exists(fout):
        os.mkdir(fout)

    cfg.NX = 200
    cfg.NY = 200
    cfg.NZ = 121
    cfg.DT = 0.02
    cfg.DX = 0.16
    cfg.DY = 0.16
    cfg.DZ = 0.20

    cfg.ntskip = 20
    cfg.nxskip = 2
    cfg.nyskip = 2
    cfg.nzskip = 2

    cfg.IEOS = 1
    cfg.TAU0 = 0.6
    cfg.fPathOut = fout

    #cfg.TFRZ = 0.137
    cfg.TFRZ = 0.100

    cfg.ETAOS_XMIN = 0.154

    cfg.ETAOS_YMIN = 0.15
    cfg.ETAOS_RIGHT_SLOP = 0.0
    cfg.ETAOS_LEFT_SLOP =  0.0

    cfg.save_to_hdf5 = True

    # for auau
    if system == 'auau200':
        cfg.Eta_gw = 1.3
        cfg.Eta_flat = 1.5
        comments = 'au+au IP-Glasma'
        collision = AuAu200()
        scale_factor = 57.0
    # for pbpb
    else:
        cfg.Eta_gw = 1.8
        cfg.Eta_flat = 2.0
        comments = 'pb+pb IP-Glasma'
        if system == 'pbpb2760':
            collision = PbPb2760()
            scale_factor = 128.0
        elif system == 'pbpb5020':
            collision = PbPb5020()
            scale_factor = 151.0

    grid_max = cfg.NX/2 * cfg.DX

    fini = os.path.join(fout, 'trento_ini/')

    if os.path.exists(fini):
        call(['rm', '-r', fini])

    if oneshot:
        collision.create_ini(cent, fini, num_of_events=1000,
                         grid_max=grid_max, grid_step=cfg.DX,
                         one_shot_ini=oneshot)
        s = np.loadtxt(os.path.join(fini, 'one_shot_ini.dat'))
    else:
        collision.create_ini(cent, fini, num_of_events=1,
                         grid_max=grid_max, grid_step=cfg.DX,
                         one_shot_ini=oneshot)
        s = np.loadtxt(os.path.join(fini, '0.dat'))
    smax = s.max()
    s_scale = s * scale_factor
    t0 = time()

    visc = CLVisc(cfg, gpu_id=gpu_id)

    ed = from_sd_to_ed(s_scale, visc.ideal.eos)

    ev = np.zeros((cfg.NX*cfg.NY*cfg.NZ, 4), cfg.real)

    # repeat the ed(x,y) NZ times
    ev[:, 0] = np.repeat((ed.T).flatten(), cfg.NZ)

    eta_max = cfg.NZ//2 * cfg.DZ
    eta = np.linspace(-eta_max, eta_max, cfg.NZ)

    heta = np.ones(cfg.NZ)

    fall_off = np.abs(eta) > cfg.Eta_flat
    eta_fall = np.abs(eta[fall_off])
    heta[fall_off] = np.exp(-(eta_fall - cfg.Eta_flat)**2/(2.0*cfg.Eta_gw**2))

    # apply the heta longitudinal distribution
    ev[:, 0] *= np.tile(heta, cfg.NX * cfg.NY)

    visc.ideal.load_ini(ev)

    visc.evolve(max_loops=4000, save_hypersf=True, save_bulk=True, save_vorticity=False)

    write_config(cfg, comments)
    t1 = time()
    print('finished. Total time: {dtime}'.format(dtime = t1-t0))
    viscous_on = "true"
    if etaos < 0.0001: viscous_on = "false"
    # get particle spectra from MC sampling and force decay
    call(['python', '../pyvisc/spec.py', '--event_dir', cfg.fPathOut,
      '--viscous_on', viscous_on, "--reso_decay", "true", "--nsampling", "2000",
      '--mode', 'mc'])
    
     # calc the smooth particle spectra
    call(['python', '../pyvisc/spec.py', '--event_dir', cfg.fPathOut,
      '--viscous_on', viscous_on, "--reso_decay", "false", 
      '--mode', 'smooth'])

def one_shot(cent='0_5', system='pbpb2760', gpu_id=0):
    path = '../results/%s_oneshot/%s'%(system, cent)
    fout = os.path.abspath(path)
    if not os.path.exists(fout):
        os.makedirs(fout)
    ebehydro(fout, cent, system = system, etaos=0.16, oneshot=True)


if __name__ == '__main__':
    one_shot(gpu_id=1)
