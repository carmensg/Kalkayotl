'''
Copyright 2019 Javier Olivares Romero

This file is part of Kalkayotl.

	Kalkayotl is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	PyAspidistra is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with Kalkayotl.  If not, see <http://www.gnu.org/licenses/>.
'''
#------------ Load libraries -------------------
from __future__ import absolute_import, unicode_literals, print_function
import sys
import os
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1" 
import numpy as np

#----- Import the module ----------
from kalkayotl import Inference


#============ Directory and data =============================
#----- Directory where chains and plots will be saved ----
dir_out    = os.getcwd() + "/Example/"
#--------------------------------------

#------- Creates directory if it does not exists -------
os.makedirs(dir_out,exist_ok=True)
#---------------------------------

#----------- Data file --------------------
file_data = dir_out + "Ruprecht_147.csv"
#-----------------------------------------
#==================================================


#=============== Tuning knobs ============================
#----------------- Chains-----------------------------------------------------
# The number of parallel chains you want to run. Two are the minimum required
# to analyse convergence.
chains = 2

# Number of computer cores to be used. You can increase it to run faster.
# IMPORTANT. Depending on your computer configuration you may have different performances.
# I recommend to use 2 cores; this is one per chain.
cores  = 2

# tuning_iters is the number of iterations used to tune the sampler
# These will not be used for the statistics nor the plots. 
# If the sampler shows warnings you most probably must increase this value.
tuning_iters   = 1000  

# After discarding the burning you will obtain sample_iters*chains samples
# from the posterior distribution. These are the ones used in the plots and to
# compute statistics.
sample_iters    = 2000

# Initialization mode
# This initialization improves the sampler efficiency.
# Notice that in some cases errors like "Bad initial energy"
# or "X.rvel is zero" may require additional random initializations.
init_mode = 'advi+adapt_diag'

#---- Iterations to run the advi algorithm-----
# In most cases the algorithm converges before the total number of
# iterations have been reached.
init_iter = 500000 

#----- Target_accept-------
# This parameter controls the acceptance of the proposed steps in the Hamiltonian
# Monte Carlo sampler. It should be larger than 0.7-0.8. Increasing it helps in the convergence
# of the sampler but increases the computing time.
#---------------------------------------------------------------------------

#------------ Statistic ----------------------------------------------
# Chose your favourite statistic and quantiles.
# This will be computed and written in both 
# Source_{statistic}.csv and Cluster_{statistic}.csv files
statistic = "mean"
quantiles = [0.025,0.975]
#----------------------------------------------------------------------

# --------- Transformation------------------------------------
# In which space you want to sample: distance or parallax?
# For distance use "pc", for parallax use "mas"
# IMPORTANT: The units of the parameters and hyper-parameters
# defined below must coincide with those of the chosen transformation.
transformation = "pc"

#--------- Zero point -----------------------------------------------
# The zero point of the parallax measurements
# You can provide either a scalar or a vector of the same dimension
# as the valid sources in your data set.
zero_point = -0.029  # This is Lindegren+2018 value
#---------------------------------------------------------------------

#------- Independent measurements--------
# In the Gaia astrometric data the measurements of stars are correlated between sources.
# By default, Kalkayotl will not assume independence amongst sources.
# Set it to True if you want to assume independence, 
# and thus neglect the parallax spatial correlations. 
indep_measures = False

#------ Parametrization -----------------
# The performance of the HMC sampler can be improved by non-central parametrizations.
# Kalkayotl comes with two options: central and non-central. While the former works better
# for nearby clusters (<500 pc) the latter does it for faraway clusters (>500 pc).
parametrization="central"
#==========================================================



#============= hyper-parameters ================================================
# parameters is a dictionary with at least two entries: "location" and "scale".
# For each of them you can either provide a value or set it to None to infer it.
# Notice that you can infer one or both.
# IMPORTANT. In the EDSD prior you must set both. Location to zero and
# scale to the scale length (in pc).

# hyper_alpha controls the cluster location, which is Gaussian distributed.
# Therefore you need to specify the median and standard deviation, in that order.
hyper_alpha = [305.,30.]

# The hyper_beta hyper-parameter controls the cluster scale, which is Gamma distributed.
# hyper_beta corresponds to the mean of the prior distribution.
hyper_beta = [50.]

# hyper_gamma controls the gamma and tidal radius parameters in 
# the EFF and King prior families. In both the parameter is distributed as
# 1+ Gamma(2,2/hyper_gamma) with the mean value at hyper_gamma.
#Set it to None in other prior families.

# hyper_delta is only used in the GMM prior (use None in the rest of prior families),
# where it represents the vector of hyper-parameters for the Dirichlet
# distribution controlling the weights in the mixture.
# IMPORTANT. The number of Gaussians in the mixture corresponds to the
# length of this vector. 



#========================= PRIORS ===========================================
# Uncomment those prior families that you are interested in using. 
list_of_prior = [
	# {"type":"EDSD",         "parameters":{"location":0.0,"scale":1350.0}, 
	# 						"hyper_alpha":None, 
	# 						"hyper_beta":None, 
	# 						"hyper_gamma":None,
	# 						"hyper_delta": None,
	# 						"tuning_iters":1*tuning_iters,
	# 						"target_accept":0.8},

	# {"type":"Uniform",      "parameters":{"location":None,"scale":None},
	# 						"hyper_alpha":hyper_alpha,
	# 						"hyper_beta":hyper_beta,
	# 						"hyper_gamma":None, 
	# 						"hyper_delta":None,
	# 						"tuning_iters":1*tuning_iters,
	# 						"target_accept":0.8},

	{"type":"Gaussian",     "parameters":{"location":None,"scale":None},
							"hyper_alpha":hyper_alpha,
							"hyper_beta":hyper_beta,
							"hyper_gamma":None,
							"hyper_delta":None,
							"tuning_iters":1*tuning_iters,
							"target_accept":0.8},

	# {"type":"King",         "parameters":{"location":None,"scale":None,"rt":None},
	# 						"hyper_alpha":hyper_alpha, 
	# 						"hyper_beta":hyper_beta, 
	# 						"hyper_gamma":[10.0],
	# 						"hyper_delta":None,
	# 						"tuning_iters":10*tuning_iters,
	# 						"target_accept":0.95},
	# NOTE: the tidal radius and its parameters are scaled.

	
	# {"type":"EFF",          "parameters":{"location":None,"scale":None,"gamma":None},
	# 						"hyper_alpha":hyper_alpha,
	# 						"hyper_beta":hyper_beta, 
	# 						"hyper_gamma":[0.5],
	# 						"hyper_delta":None,
	# 						"tuning_iters":10*tuning_iters,
	# 						"target_accept":0.95},
	# NOTE: the mean of the Gamma parameter will be at 1.0 + hyper_gamma

	# {"type":"GMM",          "parameters":{"location":None,"scale":None,"weights":None},
	# 						"hyper_alpha":hyper_alpha, 
	# 						"hyper_beta":[50.0], 
	# 						"hyper_gamma":None,
	# 						"hyper_delta":np.array([5,5]),
	# 						"tuning_iters":10*tuning_iters,
	# 						"target_accept":0.95}
	# NOTE: If you face failures of the style zero derivative try reducing the hyper_beta value.
	]
#======================= Inference and Analysis =====================================================

#--------------------- Loop over prior types ------------------------------------
for prior in list_of_prior:

	#------ Output directories for each prior -------------------
	dir_prior = dir_out + prior["type"] + "/"

	#---------- Create prior directory -------------
	os.makedirs(dir_prior,exist_ok=True)
	#------------------------------------------------

	#--------- Initialize the inference module ----------------------------------------
	p1d = Inference(dimension=1,                       # For now it only works in 1D.
					prior=prior["type"],
					parameters=prior["parameters"],
					hyper_alpha=prior["hyper_alpha"],
					hyper_beta=prior["hyper_beta"],
					hyper_gamma=prior["hyper_gamma"],
					hyper_delta=prior["hyper_delta"],
					dir_out=dir_prior,
					transformation=transformation,
					zero_point=zero_point,
					indep_measures=indep_measures,
					parametrization=parametrization)
	#-------- Load the data set --------------------
	# It will use the Gaia column names by default.
	p1d.load_data(file_data,corr_func="Lindegren+2020")

	#------ Prepares the model -------------------
	p1d.setup()

	#============ Sampling with HMC ======================================

	#------- Run the sampler ---------------------
	p1d.run(sample_iters=sample_iters,
			burning_iters=prior["tuning_iters"],
			init=init_mode,
			n_init=init_iter,
			target_accept=prior["target_accept"],
			chains=chains,
			cores=cores)
	# Note: whenever you want to analyze a previously run model, comment the .run() line.
	# This will load the model, the data and the following line will load the traces.

	# -------- Load the chains --------------------------------
	# This is useful if you have already computed the chains
	# and want to re-analyse (in that case comment the p1d.run() line)
	p1d.load_trace(sample_iters=sample_iters)

	# ------- Re-analyse the convergence of the sampler---
	p1d.convergence()

	#-------- Plot the trace of the chains ------------------------------------
	# If you provide the list of IDs (string list) it will plot the traces
	# of the provided sources. If IDs keyword is removed it only plots the population parameters.
	# Note: if you run the example with your own data either provide a valid ID or remove the keyword.
	p1d.plot_chains(IDs=['4087735025198194176'])

	#----- Compute and save the posterior statistics ---------
	p1d.save_statistics(statistic=statistic,quantiles=quantiles)

	#------- Save the samples into HDF5 file --------------
	p1d.save_samples()

	#=============== Evidence computation ==============================
	# IMPORTANT. It will increase the computing time!

	# N_samples is the number of sources from the data set that will be used
	# Set to None to use all sources

	# M_samples is the number of samples to draw from the prior. The larger the better
	# but it will further increase computing time.

	# dlogz is the tolerance in the evidence computation 
	# The sampler will stop once this value is attained.

	# nlive is the number of live points used in the computation. The larger the better
	# but it will further increase the computing time.

	# UNCOMMENT NEXT LINE
	# p1d.evidence(N_samples=100,M_samples=1000,dlogz=1.0,nlive=100)
	#----------------------------------------------------------------------------------
#=======================================================================================


#=============== Extract Samples =========================================
import h5py
file_distances = dir_out + "/Gaussian/Samples.h5"
hf = h5py.File(file_distances,'r')
srcs = hf.get("Sources")

n_samples = 100
samples = np.empty((len(srcs.keys()),n_samples))
#-------- loop over array and fill it with samples -------
for i,ID in enumerate(srcs.keys()):
	#--- Extracts a random choice of the samples --------------
	samples[i] = np.random.choice(np.array(srcs.get(str(ID))),
							size=n_samples,replace=False)
	#----------------------------------------------------------

	print("Source {0} at {1:3.1f} +/- {2:3.1f} pc.".format(ID,
										samples[i].mean(),
										samples[i].std()))

#- Close HDF5 file ---
hf.close()
#============================================================================