from qiskit.result import Result

def job_ids_to_result(job_ids, device):
    result_list = []
    for job_id in job_ids:
        result_list.append(device.retrieve_job(job_id).result())
    return result_list


def flatten_results_jobs_list(results_jobs_list):
    results_list = []
    for one_job_results in results_jobs_list:
        results = separate_results(one_job_results)
        results_list += results
    return results_list


def separate_results(one_job_results):
    return [Result(backend_name=one_job_results.backend_name,
                   backend_version=one_job_results.backend_version,
                   qobj_id=one_job_results.qobj_id,
                   job_id=one_job_results.job_id,
                   success=True,
                   results=[results]) for results in one_job_results.results]


def merge_results(results_list):
    results = []
    for res in results_list:
        results += res.results
    return Result(backend_name=results_list[0].backend_name,
                  backend_version=results_list[0].backend_version,
                  qobj_id=results_list[0].qobj_id,
                  job_id=results_list[0].job_id,
                  success=True,
                  results=results)


def results_list_to_counts_dict_list(results_list):
    counts_dict_list = []
    for results in results_list:
        counts_dict_list.append(results.get_counts())
    return counts_dict_list


def arrange_results_list_tensored(results_list):

    assert len(results_list) % 4 == 0
    pos = 0
    results_graph_states = []
    results_meas_cal = []
    for i in range(len(results_list) // 4):
            results_graph_states += results_list[pos:pos + 2]
            pos += 2
            results_meas_cal.append(merge_results(results_list[pos:pos + 2]))
            pos += 2
    return results_graph_states, results_meas_cal


def arrange_results_list_tensored3(results_list):

    assert len(results_list) % 3 == 0
    pos = 0
    results_graph_states = []
    results_meas_cal = []
    for i in range(len(results_list) // 3):
        results_graph_states += results_list[pos:pos + 1]
        pos += 1
        results_meas_cal.append(merge_results(results_list[pos:pos + 2]))
        pos += 2
    return results_graph_states, results_meas_cal
