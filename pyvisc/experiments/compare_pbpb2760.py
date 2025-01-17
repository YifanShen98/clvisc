#/usr/bin/env python
#author: lgpang
#email: lgpang@qq.com
#createTime: Sun 30 Apr 2017 04:20:10 AM CEST

import matplotlib.pyplot as plt
import numpy as np
import os
from glob import glob
from common_plotting import smash_style
from helper import ebe_mean


def cmp_dndeta(path_to_results='', cent = ['0-5', '5-10', '10-20', '20-30']):
    from pbpb2760 import dNdEta
    exp = dNdEta()
    xpos = [-0.5, -1.0, -1, -1]
    for i, c in enumerate(cent):
        if c == '0-5':
            label0 = r'$ALICE$'
            label1 = r'$CLVisc$'
        else:
            label0, label1 = None, None
        plt.errorbar(exp.x, exp.y[c], yerr=(exp.yerr[c], exp.yerr[c]), label=label0, color='r') 
        path = os.path.join(path_to_results, c.replace('-', '_'))
        dndeta = ebe_mean(path)
        plt.plot(dndeta[:, 0], dndeta[:, 1], color='k', label=label1)
        neta = len(dndeta[:, 0])
        plt.text(xpos[i], dndeta[neta/2, 1]+100, c, fontsize=25)
    plt.xlabel(r'$\eta$')
    plt.ylabel(r'$dN_{ch}/d\eta$')
    smash_style.set(line_styles=False)
    plt.legend(loc='best')
    plt.tight_layout()
    plt.xlim(-10, 10)
    plt.ylim(0, 2000)
    plt.title(r'$Pb+Pb\ \sqrt{s_{NN}}=2.76\ TeV$', fontsize=30)
    plt.savefig('pbpb2760_dndeta.pdf')
    plt.show()

def cmp_ptspec(path_to_results='', cent = ['0-5', '5-10', '10-20'], hadron='pion'):
    from pbpb2760 import dNdPt
    exp = dNdPt()
    for i, c in enumerate(cent):
        if i == 0:
            label0 = r'$ALICE$'
            label1 = r'$CLVisc$'
        else:
            label0, label1 = None, None

        shift = 5**(-i)
        x, y, yerr0, yerr1 = exp.get(hadron, c)

        plt.errorbar(x, y*shift, yerr=(yerr0*shift, yerr1*shift), label=label0, fmt='o', color='r')
        path = os.path.join(path_to_results, c.replace('-', '_'))
        dndpt = ebe_mean(path, kind='dndpt', hadron=hadron, rap='Y')
        plt.semilogy(dndpt[:, 0], 2*dndpt[:, 1]*shift, label=label1, color='k')
        ytxt, theta = 1.3, -20
        if hadron == 'kaon':
            ytxt, theta = 1.8, -12
        elif hadron == 'proton':
            ytxt, theta = 2.0, -5
        plt.text(x[5], ytxt*y[5]*shift, r'$%s$'%c, rotation=theta, size=25)
        plt.text(x[15], ytxt*y[15]*shift, r'$\times 5^{%s}$'%(-i), rotation=theta, size=25)

    plt.xlim(0, 3)
    plt.ylim(1.0E-7, 1.0E4)
    plt.xlabel(r'$p_T\ [GeV]$')
    plt.ylabel(r'$(1/2\pi)d^2 N/dYp_Tdp_T\ [GeV]^{-2}$')
    smash_style.set(line_styles=False)
    plt.legend(loc='best')
    plt.tight_layout()

    if hadron == 'pion':
        plt.title(r'$Pb+Pb\ \sqrt{s_{NN}}=2.76\ TeV,\ \pi^++\pi^-$', fontsize=30)
    elif hadron == 'kaon':
        plt.title(r'$Pb+Pb\ \sqrt{s_{NN}}=2.76\ TeV,\ K^++K^-$', fontsize=30)
    elif hadron == 'proton':
        plt.title(r'$Pb+Pb\ \sqrt{s_{NN}}=2.76\ TeV,\ p+\bar{p}$', fontsize=30)
    plt.savefig('pbpb2760_ptspec_%s.pdf'%hadron)
    plt.show()

def cmp_vn_pion(path_to_results, cent = ['0-5', '5-10', '10-20', '20-30'], save_fig=True, n=2, kind='ampt'):
    from pbpb2760 import Vn
    exp = Vn(n=n)

    for c in cent:
        if c == '0-5':
            label0 = r'$ALICE$'
            label1 = r'$CLVisc$'
        else:
            label0, label1 = None, None
        pt, vn, yerr0, yerr1 = exp.get_ptdiff('pion', c)
        plt.errorbar(pt, vn, yerr=(yerr0, yerr1), label=label0, color='r')
        path = os.path.join(path_to_results, c.replace('-', '_'))
        vn_clvisc = ebe_mean(path, kind='vn', hadron='pion')
        plt.plot(vn_clvisc[:, 0], vn_clvisc[:, n], label = label1, color = 'k')

        plt.text(2, vn[9]+0.01, c, fontsize=25)

    plt.xlabel(r'$p_T\ [GeV]$')
    plt.ylabel(r'$v_%s$'%n)
    smash_style.set(line_styles=False)
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.xlim(0, 2.5)
    plt.ylim(0.001, 0.3)
    plt.title(r'$Pb+Pb\ \sqrt{s_{NN}}=2.76\ TeV$', fontsize=30)
    plt.savefig('figs/pbpb2760_pion_v%s.pdf'%n)
    plt.show()



def cmp_v2_v3_v4(path_to_results, hadron='pion', cent =['0-5'], save_fig=True, ini='ampt'):
    from pbpb2760 import Vn
    v2_exp = Vn(n=2)
    v3_exp = Vn(n=3)
    v4_exp = Vn(n=4)
    v5_exp = Vn(n=5)

    label0 = r'$ALICE$'

    for c in cent:
        pt2, v2, v2_err0, v2_err1 = v2_exp.get_ptdiff(hadron, c)
        pt3, v3, v3_err0, v3_err1 = v3_exp.get_ptdiff(hadron, c)
        pt4, v4, v4_err0, v4_err1 = v4_exp.get_ptdiff(hadron, c)
        pt5, v5, v5_err0, v5_err1 = v5_exp.get_ptdiff(hadron, c)

        plt.errorbar(pt2, v2, yerr=(v2_err0, v2_err1), label=label0, fmt='ko', ms=10)
        plt.errorbar(pt3, v3, yerr=(v3_err0, v3_err1), fmt='rs', ms=10)
        plt.errorbar(pt4, v4, yerr=(v4_err0, v4_err1), fmt='b*', ms=10)
        plt.errorbar(pt5, v5, yerr=(v5_err0, v5_err1), fmt='md', ms=10)
        path = os.path.join(path_to_results, c.replace('-', '_'))
        vn_clvisc = ebe_mean(path, kind='vn', hadron=hadron)
        colors = ['k', 'r', 'b', 'm']
        for n in [2, 3, 4, 5]:
            label1 = None 
            if n == 2: label1 = r'$CLVisc$'
            plt.plot(vn_clvisc[:, 0], vn_clvisc[:, n], label = label1, color = colors[n-2])

        plt.text(2.5, v2[10], r"$v_2$", fontsize=40, color='k')
        plt.text(2.5, v3[10], r"$v_3$", fontsize=40, color='r')
        plt.text(2.5, v4[10], r"$v_4$", fontsize=40, color='b')
        plt.text(2.5, v5[10], r"$v_5$", fontsize=40, color='m')

        plt.xlabel(r'$p_T\ [GeV]$')
        if hadron == 'pion':
            plt.ylabel(r'$v_n\ \mathrm{for}\ \pi^+$')
        elif hadron == 'kaon':
            plt.ylabel(r'$v_n\ \mathrm{for}\ K^+$')
        elif hadron == 'proton':
            plt.ylabel(r'$v_n\ \mathrm{for}\ proton$')
        elif hadron == 'charged':
            plt.ylabel(r'$v_n\ \mathrm{for}\ h^{\pm}$')

        smash_style.set(line_styles=False)
        plt.legend(loc='upper left', title=c+r'$\%$')
        plt.tight_layout()
        plt.xlim(0, 2.5)
        plt.ylim(0.001, 1.3 * vn_clvisc[14, 2])
        plt.title(r'$Pb+Pb\ \sqrt{s_{NN}}=2.76\ TeV$', fontsize=30)
        plt.savefig('figs/pbpb2760_%s_%s_ini%s_vn.pdf'%(hadron, c.replace('-', '_'), ini))
        plt.show()


def ptspec_identify(path, cent='0_5', data_src=1):
    path = os.path.join(path, cent)
    pion = ebe_mean(path, kind='dndpt', hadron='pion', rap='Y')
    kaon = ebe_mean(path, kind='dndpt', hadron='kaon', rap='Y')
    proton = ebe_mean(path, kind='dndpt', hadron='proton', rap='Y')

    proton_fix_factor = 0.7
    if data_src == 0:
        #dat0 = np.loadtxt('dNdPt_2p76.dat', skiprows=10)
        dat = np.loadtxt( 'data/dNdYptdpt_Alice/dNdPt_pbpb2760_%s_pion_exp.dat'%cent, skiprows=10)
        dat2 = np.loadtxt('data/dNdYptdpt_Alice/dNdPt_pbpb2760_%s_kaon_exp.dat'%cent, skiprows=10)
        dat3 = np.loadtxt('data/dNdYptdpt_Alice/dNdPt_pbpb2760_%s_proton_exp.dat'%cent, skiprows=10)
        # 1304.0347
        #plt.errorbar(dat0[:,0], dat0[:,3], dat0[:,6], fmt='o', label=r'$ALICE\ charged$')
        plt.errorbar(dat[:,0], dat[:,3], dat[:,6], fmt='o',   color='r', label=r'$ALICE\ \pi^+$')
        plt.errorbar(dat2[:,0], dat2[:,3], dat2[:,6], fmt='s',color='g', label=r'$ALICE\ K^+$')
        plt.errorbar(dat3[:,0], dat3[:,3], dat3[:,6], fmt='d',color='b', label=r'$ALICE\ p$')
        #plt.semilogy(charged[:, 0], charged[:, 1], label=r'$CLVisc\ \pi^+$')
        plt.semilogy(pion[:, 0], pion[:, 1], 'k-', label=r'$CLVisc$')
        plt.semilogy(kaon[:, 0], kaon[:, 1], 'k-')
        plt.semilogy(proton[:, 0], proton_fix_factor*proton[:, 1], 'k-')
        #plt.semilogy(eta, 3.5*proton[:, 1], label=r'$CLVisc$')
    elif data_src == 1:
        from pbpb2760 import dNdPt
        exp = dNdPt()
        x_pion, y_pion, yerr0_pion, yerr1_pion = exp.get('pion', cent.replace('_', '-'))
        x_kaon, y_kaon, yerr0_kaon, yerr1_kaon = exp.get('kaon', cent.replace('_', '-'))
        x_proton, y_proton, yerr0_proton, yerr1_proton = exp.get('proton', cent.replace('_', '-'))
        plt.errorbar(x_pion, y_pion, yerr=(yerr0_pion, yerr1_pion), fmt='o',   color='r', label=r'$ALICE\ \pi^{+}+\pi^{-}$')
        plt.errorbar(x_kaon, y_kaon, yerr=(yerr0_kaon, yerr1_kaon), fmt='s',   color='g', label=r'$ALICE\ K^{+}+K^{-}$')
        plt.errorbar(x_proton, y_proton, yerr=(yerr0_proton, yerr1_proton), fmt='d',   color='b', label=r'$ALICE\ p+\bar{p}$')
        #plt.semilogy(charged[:, 0], charged[:, 1], label=r'$CLVisc\ \pi^+$')
        plt.semilogy(pion[:, 0], 2*pion[:, 1], 'k-', label=r'$CLVisc$')
        plt.semilogy(kaon[:, 0], 2*kaon[:, 1], 'k-')
        plt.semilogy(proton[:, 0],proton_fix_factor*2*proton[:, 1], 'k-')
        #plt.semilogy(eta, 3.5*proton[:, 1], label=r'$CLVisc$')

    plt.xlabel(r'$p_T\ [GeV]$')
    plt.ylabel(r'$\frac{dN}{2\pi dY p_Tdp_T}\ [GeV^{-2}]$')

    smash_style.set(line_styles=False)
    #plt.legend(loc='best', ncol=2, mode='expand')
    plt.title(r'$Pb+Pb\ 2.76\ TeV, centrality\ %s$'%cent.replace('_', '-'))
    plt.xlim(0, 4)
    plt.ylim(1.0E-2, 1.0E4)
    plt.tight_layout()
    plt.legend(loc='upper right')
    plt.savefig('figs/pbpb2760_ptspec_%s_identify.pdf'%cent)
    plt.show()



if __name__=='__main__':
    '''dndeta is not sensitive to Tfrz
    pt_spectra fit best with Tfrz=100 MeV; while v2 fits best with Tfrz=137 MeV'''
    #path = "/lustre/nyx/hyihp/lpang/trento_ebe_hydro/results_pbpb2760_tfrz100/"
    #cmp_dndeta(path, cent=['0-5', '5-10', '10-20', '20-30'])
    #cmp_ptspec(path, cent=['0-5', '5-10', '10-20', '20-40', '40-60', '60-80'], hadron='pion')
    #cmp_ptspec(path, cent=['0-5', '5-10', '10-20', '20-40', '40-60', '60-80'], hadron='kaon')
    #cmp_ptspec(path, cent=['0-5', '5-10', '10-20', '20-40', '40-60', '60-80'], hadron='proton')
    path = "/lustre/nyx/hyihp/lpang/trento_ebe_hydro/results_pbpb2760_tfrz137/"
    #cmp_vn_pion(path, cent=['0-5', '5-10', '10-20', '20-30'], save_fig=False, n=5)
    #cmp_v2_v3_v4(path, hadron='pion', cent=['0-5', '5-10', '10-20', '20-30'], ini='trento')
    #cmp_v2_v3_v4(path, hadron='kaon', cent=['0-5', '5-10', '10-20', '20-30'], ini='trento')
    cmp_v2_v3_v4(path, hadron='proton', cent=['0-5', '5-10', '10-20', '20-30'], ini='trento')

    #path = "/lustre/nyx/hyihp/lpang/trento_ebe_hydro/pbpb2p76_results_ampt/etas0p16/"
    #cmp_dndeta(path, cent=['0-5'])
    #path = "/lustre/nyx/hyihp/lpang/trento_ebe_hydro/results_pbpb2760_tfrz100/"
    #cmp_vn_pion(path, cent=['0-5', '5-10', '10-20', '20-30'], save_fig=False, n=2)
    #cmp_v2_v3_v4(path, hadron='pion', cent=['0-5', '5-10', '10-20', '20-30', '30-40', '40-50'], ini='ampt')
