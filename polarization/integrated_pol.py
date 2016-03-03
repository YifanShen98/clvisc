#/usr/bin/env python
#author: lgpang
#email: lgpang@qq.com

import matplotlib.pyplot as plt
import numpy as np
import math

from gpu_polarization import Polarization
import four_momentum as mom
from common_plotting import smash_style
from numba import jit
import matplotlib.pyplot as plt

import h5py

# store the data in hdf5 file
f_h5 = h5py.File('vor_int_ideal.hdf5', 'r+')

rapidity = np.linspace(-5, 5, 11, endpoint=True)

def init_momentum():
    dset_pt = f_h5.create_dataset('mom/PT', data=mom.PT)
    dset_phi = f_h5.create_dataset('mom/PHI', data=mom.PHI)
    dset_rapidity = f_h5.create_dataset('mom/Y', data=rapidity)

def integrated_polarization(fpath, event_id):
    '''calc the pt, phi integrated lambda polarization as a function of
    rapidity.
    The results is stored in hdf5 file'''
    sf = np.loadtxt('%s/hypersf.dat'%fpath, dtype=np.float32)
    omega = np.loadtxt('%s/omegamu_sf.dat'%fpath, dtype=np.float32)
    LambdaPolarization = Polarization(sf, omega)

    npt, nphi = mom.NPT, mom.NPHI
    vor = np.zeros((npt, nphi))
    rho = np.zeros((npt, nphi))
    vor_int, rho_int = [], []

    for Y in rapidity:
        for i, pt in enumerate(mom.PT):
            for j, phi in enumerate(mom.PHI):
                px = pt * math.cos(phi)
                py = pt * math.sin(phi)
                pol_ij, omg_ij, rho_ij = LambdaPolarization.pol_vor_rho(Y, px, py)
                vor[i, j] = pol_ij
                rho[i, j] = rho_ij
        name = 'event%s/rapidity%s/vor_vs_pt_phi'%(event_id, Y)
        dset_vor = f_h5.create_dataset(name, data=vor)
        name = 'event%s/rapidity%s/rho_vs_pt_phi'%(event_id, Y)
        dset_rho = f_h5.create_dataset(name, data=rho)

        vor_int.append( mom.pt_phi_integral(vor) )
        rho_int.append( mom.pt_phi_integral(rho) )
        print(Y, 'finished')

    name = 'event%s/integral_pt_phi/vor'%event_id
    dset_vorint = f_h5.create_dataset(name, data=vor_int)
    name = 'event%s/integral_pt_phi/rho'%event_id
    dset_rhoint = f_h5.create_dataset(name, data=rho_int)
    print('event', event_id, 'finished')



if __name__ == '__main__':
    for event_id in range(11, 15):
        fpath = '/tmp/lgpang/cent20_25_etas0p00/cent20_25_event%s'%event_id
        integrated_polarization(fpath, event_id)
        print('event', event_id, 'finished')

    f_h5.close()
