from flask import Blueprint, render_template_string
jobs_bp = Blueprint("jobs", __name__)
TBL = """<!doctype html><title>Jobs</title>
<div style="padding:1rem;font-family:system-ui">
  <h3>Jobs</h3>
  <table border="1" cellpadding="6"><tr>
    <th>Job</th><th>DNO</th><th>Poles/Spans</th><th>PASS/WARN/FAIL</th><th>Actions</th>
  </tr><tr><td>J1</td><td>SPEN</td><td>0 / 0</td><td>0/0/0</td>
  <td><a href="/map/view/J1">Map</a> · <a href="/pdf/qa/J1">PDF</a></td></tr></table>
</div>"""
@jobs_bp.get("/")
def jobs():
    return render_template_string(TBL)
