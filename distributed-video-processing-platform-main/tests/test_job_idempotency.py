def test_duplicate_message_guard():
    completed_jobs=set()
    job_id="same-job"
    def process(jid):
        if jid in completed_jobs: return "ignored"
        completed_jobs.add(jid); return "processed"
    assert process(job_id)=="processed"
    assert process(job_id)=="ignored"

def test_retry_limit():
    max_retries=3
    assert [i < max_retries for i in (1,2,3)] == [True,True,False]
