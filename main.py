# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

import firestore
from flask import current_app, flash, Flask, Markup, redirect, render_template
from flask import request, url_for
from google.cloud import error_reporting
import google.cloud.logging

app = Flask(__name__)
app.config.update(
    SECRET_KEY='secret',
    MAX_CONTENT_LENGTH=8 * 1024 * 1024,
)

app.debug = False
app.testing = False

# Configure logging
if not app.testing:
    logging.basicConfig(level=logging.INFO)
    client = google.cloud.logging.Client()
    # Attaches a Google Stackdriver logging handler to the root logger
    client.setup_logging()


@app.route('/')
def list():
    start_after = request.args.get('start_after', None)
    sensorData, last_time = firestore.next_page(start_after=start_after)

    return render_template('list.html', sensorData=sensorData, last_time=last_time)

@app.route('/dashboard')
def dashboard():
    latest = firestore.latest_values()
    data1 = firestore.highest_sensor('sensor1')
    data2 = firestore.highest_sensor('sensor2')
    data3 = firestore.highest_sensor('sensor3')
    data4 = firestore.highest_sensor('sensor4')
    return render_template('dashboard.html', latest = latest, data1 = data1, data2 = data2, data3 = data3, data4 = data4)

@app.route('/sensorData/<data_id>')
def view(data_id):
    data = firestore.read(data_id)
    return render_template('view.html', data=data)


@app.route('/sensorData/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        s_data = firestore.create(data)

        return redirect(url_for('.view', data_id=s_data['id']))

    return render_template('form.html', action='Add', data={})


@app.route('/sensorData/<data_id>/edit', methods=['GET', 'POST'])
def edit(data_id):
    data = firestore.read(data_id)

    if request.method == 'POST':
        s_data = request.form.to_dict(flat=True)

        data = firestore.update(s_data, data_id)

        return redirect(url_for('.view', data_id=data['id']))

    return render_template('form.html', action='Edit', data=data)


@app.route('/sensorData/<data_id>/delete')
def delete(data_id):
    firestore.delete(data_id)
    return redirect(url_for('.list'))


@app.route('/logs')
def logs():
    logging.info('Hey, you triggered a custom log entry. Good job!')
    flash(Markup('''You triggered a custom log entry. You can view it in the
        <a href="https://console.cloud.google.com/logs">Cloud Console</a>'''))
    return redirect(url_for('.list'))


@app.route('/errors')
def errors():
    raise Exception('This is an intentional exception.')


# Add an error handler that reports exceptions to Stackdriver Error
# Reporting. Note that this error handler is only used when debug
# is False
@app.errorhandler(500)
def server_error(e):
    client = error_reporting.Client()
    client.report_exception(
        http_context=error_reporting.build_flask_context(request))
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


# This is only used when running locally. When running live, gunicorn runs
# the application.
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
