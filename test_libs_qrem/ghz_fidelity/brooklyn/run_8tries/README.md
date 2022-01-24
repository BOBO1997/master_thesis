# Execution Method

1. run `cast_jobs.ipynb`
1. run `retrieve_jobs.ipynb`
2. run `mitigation_[method].ipynb`
3. run `fidelity_[method].ipynb`
4. run `visualization.ipynb`

If the `retrive_jobs.ipynb` is completed once, one can start from the step 3 to try other QREM methods by running `mitigation_[method].ipynb`.

In the default settings, the raw measurement results are already prepared in the `pkls/results`.

The `mitigation_ignis.ipynb` is run up to size 24 so far, whose outcomes are stored at `pkls/ignis` (but not uploaded to GitHub since the file sizes are too big).
