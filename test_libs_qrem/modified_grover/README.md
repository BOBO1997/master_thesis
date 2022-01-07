# Demonstration of Proposed QREM Method with Modified Grover Algorithm on Simulator

## Settings

1. 10-qubit system with parameter $b_{max}= \frac \pi {500}$
   1. with readout noise $p(0|1) = p(1|0) = 0.01$ for every qubit
      1. running modified Grover circuits with 100-shots and calibration circuits with 8192-shots
      2. running modified Grover circuits with 8192-shots and calibration circuits with 8192-shots
   2. with readout noise $p(0|1) = p(1|0) = 0.03$ for every qubit
      1. running modified Grover circuits with 100-shots and calibration circuits with 8192-shots
      2. running modified Grover circuits with 8192-shots and calibration circuits with 8192-shots
   3. with readout noise $p(0|1) = p(1|0) = 0.05$ for every qubit
      1. running modified Grover circuits with 100-shots and calibration circuits with 8192-shots
      2. running modified Grover circuits with 8192-shots and calibration circuits with 8192-shots
2. 20-qubit system with parameter $b_{max}= \frac \pi {500}$
   1. with readout noise $p(0|1) = p(1|0) = 0.01$ for every qubit
      1. running modified Grover circuits with 100-shots and calibration circuits with 8192-shots
      2. running modified Grover circuits with 8192-shots and calibration circuits with 8192-shots
   2. with readout noise $p(0|1) = p(1|0) = 0.03$ for every qubit
      1. running modified Grover circuits with 100-shots and calibration circuits with 8192-shots
      2. running modified Grover circuits with 8192-shots and calibration circuits with 8192-shots
   3. with readout noise $p(0|1) = p(1|0) = 0.05$ for every qubit
      1. running modified Grover circuits with 100-shots and calibration circuits with 8192-shots
      2. running modified Grover circuits with 8192-shots and calibration circuits with 8192-shots

## How to Run?

You can move to each specific directory and run the notebooks by the following three steps:

1. Run `run.ipynb` file (then, `raw_hist_list_list.pkl` file is stored at `pkls` directory)
2. Run `mitigation_METHOD.ipynb` file (then `METHOD_hit_list_list.pkl` file and `METHOD_info_list_list.pkl` file is stored at `pkls` directory)
3. Run `analysis.ipynb` file to compute estimation errors and show figures of them.

