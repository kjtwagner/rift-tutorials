

import numpy as np
import scipy.stats

# https://arxiv.org/pdf/1806.10596.pdf
#   angle between 0.25, 0.45
#   simplistic statement, it is actually distance dependent a bit narrower, see Fig 1 in their paper, and correlated with distance.

def external_prior(right_ascension, declination, phi_orb, inclination, psi, distance,xpy=np,cosine_variable=False):
    var = inclination
    return scipy.stats.norm(loc=0.35,scale=0.1/1.96).pdf(var)  # quoted range is 95% CI


def ln_external_prior(right_ascension, declination, phi_orb, inclination, psi, distance,xpy=np,cosine_variable=False):
    var = inclination
    mu_incl = 0.35
    sigma_incl = 0.1/1.96
    nm = np.log(1./np.sqrt(2*np.pi*sigma_incl**2))
    #if xpy==np:
    #    return np.log(scipy.stats.norm(loc=mu_incl,scale=sigma_incl).pdf(var))
    #else:
    return  -0.5* ((var - mu_incl)/sigma_incl)**2 +nm

import lal
def prepare_ln_external_prior(P=None,**kwargs):
    m1 = P.m1/lal.MSUN_SI
    m2 = P.m2/lal.MSUN_SI
    print(" PREPARING  for : {} {}".format(m1,m2))
    # No action needed
    return None
