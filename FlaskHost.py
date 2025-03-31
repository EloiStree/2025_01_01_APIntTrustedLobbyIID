
## pip install flask markdown --break-system-packages


# http://apint-home.ddns.net:8080/services
# http://apint-home.ddns.net:8080/client
# http://apint-home.ddns.net:8080/ntp

# http://raspberrypi:8080/services
# http://raspberrypi:8080/client
# http://raspberrypi:8080/ntp

bool_allows_to_reboot = False
bool_allows_to_reboot = True

import os
import socket
import struct
import sys

import markdown

if sys.stdout.isatty():
    print("Running in a terminal.")
    stop_service_script ="""
    sudo systemctl stop apint_flask.service
    sudo systemctl stop apint_flask.timer
    """

    # run code to stop current service
    os.system(stop_service_script)

else:
    print("Not running in a terminal.")



from flask import Flask, jsonify, render_template, request
import subprocess
import os
import ntplib
from datetime import datetime, timezone
import time

app = Flask(__name__,template_folder=os.path.dirname(os.path.abspath(__file__)))

# List of services and timers to check
services = [
    "ntp",
    "apint_push_iid.service",
    "apint_push_iid.timer",
    "apint_flask.service",
    "apint_flask.timer",
    "apint_client_pyjs.service",
    "apint_client_pyjs.timer"
]

def get_service_status(service):
    try:
        result = subprocess.run(["systemctl", "is-active", service], capture_output=True, text=True)
        status = result.stdout.strip()
        return status
    except Exception as e:
        return f"Error: {e}"

@app.route('/')
def home():
    return render_template("WWW/client_index.html")

@app.route('/rtfm')
def rtfm():
    
    return serve_page("rtfm")


def load_markdown_file(filename):
    """Loads a Markdown file, converts it to HTML, and returns it."""
    file_path = os.path.join("WWW/md/", filename)
    
    if not os.path.exists(file_path):
        return "<h1>404 - Page Not Found</h1><p>The requested page does not exist.</p>"

    with open(file_path, "r", encoding="utf-8") as file:
        md_content = file.read()
    return markdown.markdown(md_content)

@app.route("/md/<page>")
def serve_page(page):
    html_content = load_markdown_file(f"{page}.md")

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{page}</title>
        <style>
            body {{
            background-color: black;
            color: #00ff00;
            }}
            a {{
            color: #00AA00;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    return html



def replace_body_in_default_html(body):
    html_page_to_load= "WWW/insert_body_here.html"
    html_template = open(html_page_to_load).read()
    html_template = html_template.replace("BODY", body)
    return html_template

@app.route('/services')
def services_route():
    service_statuses = {service: get_service_status(service) for service in services}
    #unpack  the json to make it more readyable in html
    html_services = """
    <table border="1" style="width:100%; text-align:left;">
        <thead>
            <tr>
                <th>Service</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
    """
    for service, status in service_statuses.items():
        color = "green" if status == "active" else "red"
        html_services += f"<tr><td>{service}</td><td style='color:{color};'>{status}</td></tr>"
    html_services += """
        </tbody>
    </table>
    """
    return replace_body_in_default_html(html_services)

@app.route('/client')
def client_page():
    return render_template('RunClient.html')




import os
hostname=""
hostname_ip=""
def refresh_hostname():
    global hostname_ip, hostname
    if hostname_ip==None or hostname_ip=="":
        output = os.popen("hostname -I").read().strip()
        hostname = output
        ip_addresses = output.split()
        stack=""
        for ip in ip_addresses:
            if "." in ip:  
                stack+= ip+"\n"
        hostname_ip=stack
          
@app.route('/ipv4')
def get_local_ipv4():
    global hostname_ip
    refresh_hostname()
    return hostname_ip

@app.route('/hostname')
def get_local_hostname():
    global  hostname
    refresh_hostname()
    return hostname



bool_allows_anonymous_push = True
udp_local_listener_server = 3615
udp_local_listener_ip = "127.0.0.1"

@app.route('/push_iid')
def push_integer():
    """
    Allows to push iid with http call if you need and trust your local network.
    http://raspberrypi.local:8080/push_iid?index=43&value=5&date=1634567890
    """
    if not bool_allows_anonymous_push:
        return "Pushing not allowed"
    
    index = request.args.get('index')
    value = request.args.get('value')
    date = request.args.get('date')
    delayms= request.args.get('delayms')
    if date is None and delayms is not None:
        date = int(time.time()*1000) + int(delayms)
    elif date is not None and delayms is not None:
        date = int(date) + int(delayms)
    elif date is not None and delayms is None:
        date = int(date)
    else:
        date = None
    
    
    bytes_to_send = None
    try:
        if index is not None and value is None and date is None:
            bytes_to_send = struct.pack('<i', int(index))
        elif index is not None and value is not None and date is None:
            bytes_to_send = struct.pack('<ii', int(index), int(value))
        elif index is None and value is not None and date is not None:
            bytes_to_send = struct.pack('<iQ', int(value), int(date))
        elif index is not None and value is not None and date is not None:
            bytes_to_send = struct.pack('<iiQ', int(index), int(value), int(date))
        
        if bytes_to_send is not None:
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.sendto(bytes_to_send, (udp_local_listener_ip, udp_local_listener_server))
            udp_socket.close()
            return "Data pushed successfully"
        else:
            return "Invalid parameters"
    except Exception as e:
        return f"Error: {e}"  
        
        
        
    


@app.route('/web3-min-js')
def web3_min_js():
    return render_template('WWW/web3.min.js')

@app.route('/reboot')
def reboot_page():
    if not bool_allows_to_reboot:
        return "Rebooting not allowed"
    else :  
        os.system("sudo reboot")
        return "Rebooting..."

@app.route('/ntp')
def ntp_page():
    return render_template('WWW/client_ntp_page.html')

@app.route('/ntp-offset', methods=['POST'])
def ntp_post_offset():
    dico ={}
    data = request.get_json()
    client_timestamp = data.get('timestamp')
    if client_timestamp is None:
        return jsonify({'error': 'Timestamp not provided'}), 400
    server_timestamp = int(time.time() * 1000)
    offset = server_timestamp - client_timestamp
    dico["offset"] = offset
    dico["server_timestamp"] = server_timestamp
    dico["client_timestamp"] = client_timestamp     
    return jsonify(dico)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
