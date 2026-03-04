import os
import json
import glob

def generate_html_viewer():
    output_dir = "outputs/accounts"
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Clara Answer - Account Dashboard</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }
            .container { max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #f8f9fa; color: #2c3e50; font-weight: 600; }
            tr:hover { background-color: #f1f8ff; }
            .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
            .badge-v1 { background-color: #e3f2fd; color: #1976d2; }
            .badge-v2 { background-color: #e8f5e9; color: #388e3c; }
            .badge-change { background-color: #fff3e0; color: #f57c00; margin-bottom: 4px; display: block; }
            .details-row { display: none; background-color: #fafbfc; }
            .details-content { display: flex; gap: 20px; padding: 15px; border: 1px solid #ddd; border-top: none; }
            .json-block { flex: 1; background: #282c34; color: #abb2bf; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: monospace; font-size: 13px; }
            .btn { background: #3498db; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; }
            .btn:hover { background: #2980b9; }
        </style>
        <script>
            function toggleDetails(id) {
                const el = document.getElementById('details-' + id);
                if (el.style.display === 'table-row') {
                    el.style.display = 'none';
                } else {
                    el.style.display = 'table-row';
                }
            }
        </script>
    </head>
    <body>
        <div class="container">
            <h1>Clara Agent Automation Dashboard</h1>
            <p>Overview of processed accounts and agent versions.</p>
            <table>
                <thead>
                    <tr>
                        <th>Account ID</th>
                        <th>v1 Created</th>
                        <th>v2 Updated</th>
                        <th>Changes Logged</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    dirs = glob.glob(f"{output_dir}/account_*")
    dirs.sort()
    
    for account_dir in dirs:
        account_id = os.path.basename(account_dir)
        
        v1_memo_path = f"{account_dir}/v1/memo.json"
        v2_memo_path = f"{account_dir}/v2/memo.json"
        changelog_path = f"{account_dir}/changelog.json"
        
        has_v1 = os.path.exists(v1_memo_path)
        has_v2 = os.path.exists(v2_memo_path)
        
        v1_json = "{}"
        v2_json = "{}"
        changes_html = "No changes"
        
        if has_v1:
            with open(v1_memo_path, 'r') as f:
                v1_json = f.read()
                
        if has_v2:
            with open(v2_memo_path, 'r') as f:
                v2_json = f.read()
                
        if os.path.exists(changelog_path):
            with open(changelog_path, 'r') as f:
                cl = json.load(f)
                changes = cl.get("changes", [])
                if changes:
                    changes_html = "".join([f'<span class="badge badge-change">{c}</span>' for c in changes])
        
        html_content += f"""
                    <tr>
                        <td><strong>{account_id}</strong></td>
                        <td><span class="badge badge-v1">{'Yes' if has_v1 else 'No'}</span></td>
                        <td><span class="badge badge-v2">{'Yes' if has_v2 else 'No'}</span></td>
                        <td>{changes_html}</td>
                        <td><button class="btn" onclick="toggleDetails('{account_id}')">View Diff</button></td>
                    </tr>
                    <tr id="details-{account_id}" class="details-row">
                        <td colspan="5">
                            <div class="details-content">
                                <div class="json-block"><strong>v1 Memo:</strong><br><pre>{v1_json}</pre></div>
                                <div class="json-block"><strong>v2 Memo:</strong><br><pre>{v2_json}</pre></div>
                            </div>
                        </td>
                    </tr>
        """
        
    html_content += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    
    # Write to file
    with open("outputs/viewer.html", "w") as f:
        f.write(html_content)
        
    print("Static HTML viewer generated at outputs/viewer.html")

if __name__ == "__main__":
    generate_html_viewer()
