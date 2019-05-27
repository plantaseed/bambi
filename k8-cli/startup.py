from flask import Flask, render_template, redirect, url_for, request
from urllib.parse import urlparse
import cli_std_lib
import os
from subprocess import Popen, PIPE
import sys
import time
import socket
import yaml
from werkzeug import secure_filename

# create the application object
app = Flask(__name__)
bambi = None
# use decorators to link the function to a url


# route for handling the login page logic
@app.route('/', methods=['GET', 'POST'])
def login():
    global bambi
    error = None
    if request.method == 'POST':
        if 'Config' in request.form and request.form['Config'] == 'Config':
            return redirect(url_for('config'))

        exists = os.path.isfile('./config.yaml')
        if not exists:
            return "Need to provide config.yaml file first"

        if 'Auth' in request.form and request.form['Auth'] == 'Auth':
            return redirect(url_for('auth'))

        exists = os.path.isfile('./certs_and_configs/key.json')
        if not exists:
            return "Please authenticate your manager first"

        if bambi is None:
            bambi = cli_std_lib.Bambi()

        addr = urlparse(request.url_root).hostname
        bambi.name = request.form['username']
        bambi.app = "code-server" + "-" + bambi.name

        if not auth_to_git_repo(request.form['username'], request.form['password']):
            return "no access to git"

        addr = bambi.create_workspace(
            request.form['username'], request.form['password'])
        time.sleep(5)

        if not addr:
            addr = bambi.get_address_to_workspace()
            t = 0
            while 1:
                time.sleep(1)
                if not addr:
                    addr = bambi.get_address_to_workspace()
                t += 1
                if t >= 30:
                    return "server not responding, timed out!"

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(
                    (addr.split(':', 1)[0], int(addr.split(':', 1)[1])))
                if not result:
                    break

        print("final addr = " + addr)
        return redirect("https://" + addr)

    return render_template('index.html', error=error)


@app.route('/config', methods=['GET', 'POST'])
def config():
    error = None
    if request.method == 'POST':
        if 'Login' in request.form and request.form['Login'] == 'Login':
            return redirect(url_for('login'))
        if 'config' in request.files:
            config = request.files['config']
            config.save(secure_filename("config.yaml"))
            print(config)
            return render_template('config.html', error=error)

    return render_template('config.html', error=error)


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    error = None
    p = Popen(["gcloud", "auth", "application-default", "login",
               "--no-launch-browser", "--quiet"], stdout=PIPE, stderr=PIPE,  stdin=PIPE)
    p.stderr.readline()  # go to the following link
    p.stderr.readline()  # \n

    if 'Token' in request.form and len(request.form['Token']) > 0:
        print(request.form['Token'].encode("utf-8"), file=sys.stderr)
        print(p.communicate(request.form['Token'].encode(
            "utf-8")), file=sys.stderr)

        if p.returncode:
            return "invalid token"

        p1 = Popen(["gcloud", "iam", "service-accounts", "list"],
                   stdout=PIPE, stderr=PIPE)

        p2 = Popen(['grep', 'Compute.Engine.default.service.account*r*@*'],
                   stdin=p1.stdout, stdout=PIPE, stderr=PIPE)

        stdout, _ = p2.communicate()
        account = stdout.decode('utf-8').split("  ")[1][:-1]

        p = Popen(["gcloud", "iam", "service-accounts", "keys", "create",
                   "certs_and_configs/key.json", "--iam-account", account])
        p.communicate()

        return redirect('/')
    return render_template('login.html', error=error, url="https://accounts.google.com/o/oauth2/auth?redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&prompt=select_account&response_type=code&client_id=764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform&access_type=offline")


def auth_to_git_repo(USER, PASSWORD):
    config = yaml.safe_load(open('config.yaml'))
    process = Popen(['sh', '-c', 'if git ls-remote https://' + USER + ':' + PASSWORD + '@' + str(
        config["config"]["project"]["git_url"]) + ' >/dev/null ; then echo True ; fi'], stdout=PIPE, stderr=PIPE)
    stdout, _ = process.communicate()
    branch = stdout.decode("utf-8").strip()
    if branch == "True":
        return True
    return False


if __name__ == '__main__':
    app.run(host='0.0.0.0')
