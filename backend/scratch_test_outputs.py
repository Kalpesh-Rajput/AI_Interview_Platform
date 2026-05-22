import sys
from pathlib import Path
backend_path = Path("c:/test/new_ats/Final/ATS_Interview_Intelligence/backend")
sys.path.insert(0, str(backend_path))

import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "lsv2_pt_dummy"

from langsmith import traceable, get_current_run_tree

captured_rt = []

@traceable(run_type="llm")
def test_llm_call():
    rt = get_current_run_tree()
    captured_rt.append(rt)
    if rt.outputs is None:
        rt.outputs = {}
    rt.outputs["usage_metadata"] = {
        "input_tokens": 100,
        "output_tokens": 50,
        "total_tokens": 150,
        "total_cost": 0.0003
    }
    return "This is completion content"

res = test_llm_call()
print("Returned result:", res)
rt = captured_rt[0]
print("After execution - rt.outputs:", rt.outputs)
