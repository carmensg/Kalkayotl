
"""
This file contains scipy custom distributions
"""

import numpy as np
from scipy.stats import rv_continuous
from scipy.optimize import root_scalar
from scipy.special import gamma as gamma_function
import scipy.integrate as integrate
from scipy.special import hyp2f1

#=============== EDSD generator ===============================
class edsd_gen(rv_continuous):
	"EDSD distribution"
	def _pdf(self, x,L):
		return (0.5 * ( x**2 / L**3)) * np.exp(-x/L)

	def _cdf(self, x,L):
		result = 1.0 - np.exp(-x/L)*(x**2 + 2. * x * L + 2. * L**2)/(2.*L**2)
		return result

	def _rvs(self,L):
		sz, rndm = self._size, self._random_state
		u = rndm.random_sample(size=sz)

		v = np.zeros_like(u)

		for i in range(sz[0]):

			sol = root_scalar(lambda x : self._cdf(x,L) - u[i],
				bracket=[0,1.e10],
				method='brentq')
			v[i] = sol.root
		return v



edsd = edsd_gen(a=0.0,name='edsd')
#===============================================================

#=============== EFF generator ===============================
class eff_gen(rv_continuous):
	"EFF distribution"
	""" This probability density function is defined for x>0"""
	def _pdf(self,x,gamma):

		cte = np.sqrt(np.pi)*gamma_function(0.5*(gamma-1.))/gamma_function(gamma/2.)
		nx = (1. + x**2)**(-0.5*gamma)
		return nx/cte

	def _cdf(self,x,gamma):
		cte = np.sqrt(np.pi)*gamma_function(0.5*(gamma-1.))/gamma_function(gamma/2.)

		a = hyp2f1(0.5,0.5*gamma,1.5,-x**2)

		return 0.5 + x*(a/cte)
				

	def _rvs(self,gamma):
		#---------------------------------------------
		sz, rndm = self._size, self._random_state
		# Uniform between 0.01 and 0.99. It avoids problems with the
		# numeric integrator
		u = rndm.uniform(0.01,0.99,size=sz) 

		v = np.zeros_like(u)

		for i in range(sz[0]):
			try:
				sol = root_scalar(lambda x : self._cdf(x,gamma) - u[i],
				bracket=[-1000.,1000.],
				method='brentq')
			except Exception as e:
				print(u[i])
				print(self._cdf(-1000.0,gamma))
				print(self._cdf(1000.00,gamma))
				raise
			v[i] = sol.root
			sol  = None
		return v

eff = eff_gen(name='EFF')
#===============================================================

#=============== Multivariate EFF generator ===============================
class multivariate_eff_gen(rv_continuous):
	"Multivariate EFF distribution"
	""" Implement as multivariate t distribution"""
	

mveff = multivariate_eff_gen(name='EFF')
#===============================================================

#=============== King generator ===============================
class king_gen(rv_continuous):
	"King distribution"
	def _pdf(self,x,rt):
		"""
		The tidal radius is in units of the core radius
		"""
		cte = 2.*( rt/(1 + rt**2) - 2.*np.arcsinh(rt)/np.sqrt(1.+ rt**2) + np.arctan(rt))

		a = 1./np.sqrt(1. +  x**2)
		u = 1./np.sqrt(1. + rt**2)

		res = ((a-u)**2)/cte

		return np.where(np.abs(x) < rt,res,np.full_like(x,np.nan))

	def _cdf(self,x,rt):
		u   = 1 + rt**2
		cte = 2.*( rt/(1 + rt**2) - 2.*np.arcsinh(rt)/np.sqrt(1.+ rt**2) + np.arctan(rt))

		val = (rt+x)/u - (2.*(np.arcsinh(rt)+np.arcsinh(x))/np.sqrt(u)) + (np.arctan(rt)+np.arctan(x))

		res = val/cte
		
		return res
				

	def _rvs(self,rt):
		#----------------------------------------
		sz, rndm = self._size, self._random_state
		u = rndm.uniform(0.0,1.0,size=sz) 

		v = np.zeros_like(u)

		for i in range(sz[0]):
			try:
				sol = root_scalar(lambda x : self._cdf(x,rt) - u[i],
				bracket=[-rt,rt],
				method='brentq')
			except Exception as e:
				print(u[i])
				print(self._cdf(-rt,rt))
				print(self._cdf(rt,rt))
				raise
			v[i] = sol.root
			sol  = None
		return v

king = king_gen(name='King')



###################################################### TEST ################################################################################
import sys
import matplotlib
matplotlib.use('PDF')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import scipy.stats as st


def test_edsd(n=1000,L=100.):
	#----- Generate samples ---------
	s = edsd.rvs(L=L,size=n)


	#------ grid -----
	x = np.linspace(0,10.*L,100)
	y = edsd.pdf(x,L=L)
	z = (x**2/(2.*L**3))*np.exp(-x/L)

	pdf = PdfPages(filename="Test_EDSD.pdf")
	plt.figure(1)
	plt.hist(s,bins=50,density=True,color="grey",label="Samples")
	plt.plot(x,y,color="black",label="PDF")
	plt.plot(x,z,color="red",linestyle="--",label="True")
	plt.legend()
	
	#-------------- Save fig --------------------------
	pdf.savefig(bbox_inches='tight')
	plt.close(1)
	
	pdf.close()

def test_eff(n=10000,r0=100.,rc=2.,gamma=2):

	# ----- Generate samples ---------
	s = r0 + rc*eff.rvs(gamma=gamma,size=n)

	#------ grid ----------------------
	range_dist = (r0-20*rc,r0+20*rc)
	x = np.linspace(range_dist[0],range_dist[1],1000)
	y = eff.pdf(x,loc=r0,scale=rc,gamma=gamma)
	z = eff.cdf(x,loc=r0,scale=rc,gamma=gamma)

	pdf = PdfPages(filename="Test_EFF.pdf")
	plt.figure(0)
	plt.hist(s,bins=100,range=range_dist,density=True,color="grey",label="Samples")
	plt.plot(x,y,color="black",label="PDF")
	plt.xlim(range_dist)
	plt.yscale('log')
	plt.legend()
	
	#-------------- Save fig --------------------------
	pdf.savefig(bbox_inches='tight')
	plt.close(0)

	plt.figure(1)
	plt.plot(x,z,color="black",label="CDF")
	plt.legend()
	
	#-------------- Save fig --------------------------
	pdf.savefig(bbox_inches='tight')
	plt.close(1)
	
	pdf.close()

def test_king(n=100000,r0=100.,rc=2.,rt=20.):
	#----- Generate samples ---------
	s = king.rvs(loc=r0,scale=rc,rt=rt/rc,size=n)
	#------ grid -----
	
	range_dist = (r0-1.5*rt,r0+1.5*rt)
	x = np.linspace(range_dist[0],range_dist[1],1000)
	y = king.pdf(x,loc=r0,scale=rc,rt=rt/rc)
	z = king.cdf(x,loc=r0,scale=rc,rt=rt/rc)
	
	pdf = PdfPages(filename="Test_King.pdf")
	plt.figure(0)
	plt.hist(s,bins=100,range=range_dist,density=True,color="grey",label="Samples")
	plt.plot(x,y,color="black",label="PDF")
	plt.xlim(range_dist)
	plt.yscale('log')
	plt.legend()
	
	#-------------- Save fig --------------------------
	pdf.savefig(bbox_inches='tight')
	plt.close(0)

	plt.figure(1)
	plt.plot(x,z,color="black",label="CDF")
	plt.xlim(range_dist)
	plt.legend()
	
	#-------------- Save fig --------------------------
	pdf.savefig(bbox_inches='tight')
	plt.close(1)
	
	pdf.close()


	

if __name__ == "__main__":


	# test_edsd()

	# test_eff()

	test_king()
