# Checking the Violation of the Bell inequality by [Baccari et al., PRL, 2020] on IBM Quantum Brooklyn

## The order to run the programs

1. [cast_jobs.ipynb](https://github.com/BOBO1997/master_thesis/blob/main/bell_ineq/path_graphs/brooklyn/cast_jobs.ipynb)
  - In this file, the quantum circuits for the Bell inequality are created and sent to the real device.
  - The jobs (or their job IDs) of the job for those quantum circuits are saved as [pkls/jobs.pkl](https://github.com/BOBO1997/master_thesis/blob/main/bell_ineq/path_graphs/brooklyn/pkls/jobs.pkl). If job objects cannot be saved, please save job IDs instead. The device properties are also saved at the same time.
  - The self-made functions are imported from [../../libs_bell](https://github.com/BOBO1997/master_thesis/tree/main/bell_ineq/libs_bell).
2. [retrieve_jobs.ipynb](https://github.com/BOBO1997/master_thesis/blob/main/bell_ineq/path_graphs/brooklyn/retrieve_jobs.ipynb)
  - This file retrieves the completed jobs from the real quantum devices. If the saved objects are IBMQJobs, we can load and open it as a job. If they are job IDs, then we have to first use `retrieve_jobs()` method in `IBMQBackend` to recover the job objects from the job IDs.
  - After retrieving the results, the results for main process (Bell inequality) are converted to histograms and saved as [pkls/raw_hist_list.pkl](https://github.com/BOBO1997/master_thesis/blob/main/bell_ineq/path_graphs/brooklyn/pkls/raw_hist_list.pkl). The results for QREM are saved separately as [pkls/results_meas_cal.pkl](https://github.com/BOBO1997/master_thesis/blob/main/bell_ineq/path_graphs/brooklyn/pkls/results_meas_cal.pkl).
3. [mitigation_ignis.ipynb](https://github.com/BOBO1997/master_thesis/blob/main/bell_ineq/path_graphs/brooklyn/mitigation_ignis.ipynb)
  - According to the results for QREM, we use `qiskit.ignis.mitigation.TensoredMeasFitter` to make the calibration matrices which characterize the readout noise on each qubit.
  - Then in this file, the readout error effect of noisy histograms for Bell inequality are mitigated by the rigorous inversion of the calibration matrices through [libs_qrem]().
  - [libs_qrem](https://github.com/BOBO1997/libs_qrem) allows us to mitigate the readout error super fast thanks to its implementation in C++. To use this package, please install it by following the instruction [here](https://github.com/BOBO1997/libs_qrem).
4. [mitigation_lnp.ipynb](https://github.com/BOBO1997/master_thesis/blob/main/bell_ineq/path_graphs/brooklyn/mitigation_lnp.ipynb)
  - This file mitigates the noisy histograms using the least norm problem option in libs_qrem, proposed by [Yang, Raymond, Uno, PRA, 2022](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.106.012423).
  - We included the mitigated result by this mitigation option in this Bell inequality experiment.
  - Other files for the other mitigation options in this directory were not used in this experiment.
5. [analysis.ipynb](https://github.com/BOBO1997/master_thesis/blob/main/bell_ineq/path_graphs/brooklyn/analysis.ipynb)
  - In this file, we compute the correlation of the Bell inequality by Baccari et al. with the raw/mitigated histograms for the observables.
  - The correlations for different number of qubits are plotted onto figures.
  

Since Qiskit would be updated destructively, some functions and methods may not available in the latest Qiskit version.
Please, feel free to optimize these codes when you use them, according to your purpose.
