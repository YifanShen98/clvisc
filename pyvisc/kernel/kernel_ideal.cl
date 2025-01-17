#include<helper.h>

__kernel void kt_src_christoffel(
             __global real4 * d_Src,
		     __global real4 * d_ev,
             read_only image2d_t eos_table,
		     const real tau,
             const int step) {
    int I = get_global_id(0);

    if ( I < NX*NY*NZ ) {
        if ( step == 1 ) {
            d_Src[I] = (real4)(0.0f, 0.0f, 0.0f, 0.0f);
        }
        real4 e_v = d_ev[I];
        real ed = e_v.s0;
        real vx = e_v.s1;
        real vy = e_v.s2;
        real vz = e_v.s3;
        real pressure = P(ed, eos_table);
        real u0 = gamma(vx, vy, vz);

        // Tzz_tilde = T^{eta eta} * tau^2; no 1/tau in vz
        real Tzz_tilde = (ed + pressure)*u0*u0*vz*vz + pressure;
        real Ttz_tilde = (ed + pressure)*u0*u0*vz;

#ifdef RIEMANN_TEST
// the Christoffel terms are removed to compare with RIEMANN solution
// in (t, x, y, z) coordinates,
// later we use T^{mu nu} instead of \tilde{T}^{mu nu} in hydro evolution
        d_Src[I] = d_Src[I];
#else
        d_Src[I] = d_Src[I] - (real4)(Tzz_tilde, 0.0f, 0.0f, Ttz_tilde);
#endif
    }
}

// output: d_Src; all the others are input
__kernel void kt_src_alongx(
             __global real4 * d_Src,
		     __global real4 * d_ev,
             read_only image2d_t eos_table,
		     const real tau) {
    int J = get_global_id(1);
    int K = get_global_id(2);
    __local real4 ev[NX+4];

    // Use num of threads = BSZ to compute src for NX elements
    for ( int I = get_global_id(0); I < NX; I = I + BSZ ) {
        int IND = I*NY*NZ + J*NZ + K;
        ev[I+2] = d_ev[IND];
    }

    barrier(CLK_LOCAL_MEM_FENCE);

    // set boundary condition (constant extrapolation)
    if ( get_local_id(0) == 0 ) {
       ev[0] = ev[2];
       ev[1] = ev[2];
       ev[NX+3] = ev[NX+1];
       ev[NX+2] = ev[NX+1];
    }
    
    barrier(CLK_LOCAL_MEM_FENCE);

    for ( int I = get_global_id(0); I < NX; I = I + BSZ ) {
        int IND = I*NY*NZ + J*NZ + K;
        int i = I + 2;
#ifdef RIEMANN_TEST
        d_Src[IND] = d_Src[IND] - kt1d(ev[i-2], ev[i-1],
                     ev[i], ev[i+1], ev[i+2], tau, ALONG_X, eos_table)/DX;
#else
        d_Src[IND] = d_Src[IND] - tau * kt1d(ev[i-2], ev[i-1],
                     ev[i], ev[i+1], ev[i+2], tau, ALONG_X, eos_table)/DX;
#endif
    }
}


// output: d_Src; all the others are input
__kernel void kt_src_alongy(
             __global real4 * d_Src,
		     __global real4 * d_ev,
             read_only image2d_t eos_table,
		     const real tau) {
    int I = get_global_id(0);
    int K = get_global_id(2);
    __local real4 ev[NY+4];

    // Use num of threads = BSZ to compute src for NX elements
    for ( int J = get_local_id(1); J < NY; J = J + BSZ ) {
        int IND = I*NY*NZ + J*NZ + K;
        ev[J+2] = d_ev[IND];
    }

    barrier(CLK_LOCAL_MEM_FENCE);

    // set boundary condition (constant extrapolation)
    if ( get_global_id(1) == 0 ) {
       ev[0] = ev[2];
       ev[1] = ev[2];
       ev[NY+3] = ev[NY+1];
       ev[NY+2] = ev[NY+1];
    }
    
    barrier(CLK_LOCAL_MEM_FENCE);

    for ( int J = get_global_id(1); J < NY; J = J + BSZ ) {
        int IND = I*NY*NZ + J*NZ + K;
        int j = J + 2;
#ifdef RIEMANN_TEST
        d_Src[IND] = d_Src[IND] - kt1d(ev[j-2], ev[j-1],
                     ev[j], ev[j+1], ev[j+2], tau, ALONG_Y, eos_table)/DY;
#else
        d_Src[IND] = d_Src[IND] - tau * kt1d(ev[j-2], ev[j-1],
                     ev[j], ev[j+1], ev[j+2], tau, ALONG_Y, eos_table)/DY;
#endif
    }
}

// output: d_Src; all the others are input
__kernel void kt_src_alongz(
             __global real4 * d_Src,
		     __global real4 * d_ev,
             read_only image2d_t eos_table,
		     const real tau) {
    int I = get_global_id(0);
    int J = get_global_id(1);
    __local real4 ev[NZ+4];

    // Use num of threads = BSZ to compute src for NX elements
    for ( int K = get_local_id(2); K < NZ; K = K + BSZ ) {
        int IND = I*NY*NZ + J*NZ + K;
        ev[K+2] = d_ev[IND];
    }

    barrier(CLK_LOCAL_MEM_FENCE);

    // set boundary condition (constant extrapolation)
    if ( get_global_id(2) == 0 ) {
       ev[0] = ev[2];
       ev[1] = ev[2];
       ev[NZ+3] = ev[NZ+1];
       ev[NZ+2] = ev[NZ+1];
    }
    
    barrier(CLK_LOCAL_MEM_FENCE);

    for ( int K = get_global_id(2); K < NZ; K = K + BSZ ) {
        int IND = I*NY*NZ + J*NZ + K;
        int k = K + 2;
#ifdef RIEMANN_TEST
        d_Src[IND] = d_Src[IND] - kt1d(ev[k-2], ev[k-1],
                     ev[k], ev[k+1], ev[k+2], tau, ALONG_Z, eos_table)/DZ;
#else 
        d_Src[IND] = d_Src[IND] - tau * kt1d(ev[k-2], ev[k-1],
                     ev[k], ev[k+1], ev[k+2], tau, ALONG_Z, eos_table)/(tau*DZ);
#endif
    }
}



/** update d_evnew with d_ev1 and d_Src*/
__kernel void update_ev(
	__global real4 * d_evnew,
	__global real4 * d_ev1,
	__global real4 * d_Src,
    read_only image2d_t eos_table,
	const real tau,
	const int  step)
{
    int I = get_global_id(0);
    if ( I < NX*NY*NZ ) {
    real4 e_v = d_ev1[I];
    real ed = e_v.s0;
    real vx = e_v.s1;
    real vy = e_v.s2;
    real vz = e_v.s3;
    real pressure = P(ed, eos_table);
    real u0 = gamma(vx, vy, vz);
    real4 umu = u0*(real4)(1.0f, vx, vy, vz);

    // when step=2, tau=(n+1)*DT, while T0m need tau=n*DT
    real old_time = tau - (step-1)*DT;

#ifdef RIEMANN_TEST
    real4 T0m = ((ed + pressure)*u0*umu - pressure*gm[0]);
#else 
    real4 T0m = ((ed + pressure)*u0*umu - pressure*gm[0]) * old_time;
#endif
    /** step==1: Q' = Q0 + Src*DT
        step==2: Q  = Q0 + (Src(Q0)+Src(Q'))*DT/2
    */
    T0m = T0m + d_Src[I]*DT/step;

#ifdef RIEMANN_TEST
    real T00 = max(acu, T0m.s0);
    real T01 = (fabs(T0m.s1) < acu) ? 0.0f : T0m.s1;
    real T02 = (fabs(T0m.s2) < acu) ? 0.0f : T0m.s2;
    real T03 = (fabs(T0m.s3) < acu) ? 0.0f : T0m.s3;
#else
    real T00 = max(acu, T0m.s0)/tau;
    real T01 = (fabs(T0m.s1) < acu) ? 0.0f : T0m.s1/tau;
    real T02 = (fabs(T0m.s2) < acu) ? 0.0f : T0m.s2/tau;
    real T03 = (fabs(T0m.s3) < acu) ? 0.0f : T0m.s3/tau;
#endif


    real M = sqrt(T01*T01 + T02*T02 + T03*T03);
    real SCALE_COEF = 0.999f;
    if ( M > T00 ) {
	    T01 *= SCALE_COEF * T00 / M;
	    T02 *= SCALE_COEF * T00 / M;
	    T03 *= SCALE_COEF * T00 / M;
        M = SCALE_COEF * T00;
        //M = 0.0f;
    }

    real ed_find;
    rootFinding_newton(&ed_find, T00, M, eos_table);
    //rootFinding(&ed_find, T00, M, eos_table);
    ed_find = max(0.0f, ed_find);

    real pr = P(ed_find, eos_table);

    // vi = T0i/(T00+pr) = (e+p)u0*u0*vi/((e+p)*u0*u0)
    real epv = max(acu, T00 + pr);
    d_evnew[I] = (real4)(ed_find, T01/epv, T02/epv, T03/epv);
    }
}
