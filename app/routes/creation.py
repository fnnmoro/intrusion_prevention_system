from flask import (Blueprint, redirect, request,
                   render_template, session, url_for)

from app.core import gatherer
from app.core.preprocess import Formatter, Modifier
from app.core.tools import export_flows_csv, clean_files, get_content


bp = Blueprint('creation', __name__)

@bp.route('/<function>/<dir>/')
def content(function, dir):
    # clears the path history if the dir received is from the main options
    if dir in ['pcap', 'nfcapd', 'csv']:
        path_history = {'root': root}
    else:
        path_history = session['path_history']

    # checks if the folder was already opened
    if not dir in path_history.keys():
        path_history[dir] = f'{dir}/'
    # creates the full path
    full_path = path_history['root'] + path_history[dir]

    # gets dir content
    inner_dirs, files = get_content(full_path)

    # creates the path of the inner dirs
    for inner_dir in inner_dirs:
        path_history[inner_dir] = f'{path_history[dir]}{inner_dir}/'

    session['path_history'] = path_history

    return render_template('creation/content.html',
                           dir=dir,
                           inner_dirs=inner_dirs,
                           files=files,
                           relative_path=session['path_history'][dir],
                           function=function)


@bp.route('/<function>/<dir>/parameters', methods=['GET','POST'])
def parameters(function, dir):
    session['function'] = function
    session['dir'] = dir
    session['files'] = request.form.getlist('files')
    session['path'] = (session['path_history']['root']
                       + session['path_history'][dir])

    # functions parameters to be used according to the function selected
    functions = {'split_pcap':
                    {'parameters': [{'name': 'Split size',
                                    'type': 'number'}]},
                 'convert_pcap_nfcapd':
                    {'parameters': [{'name': 'Time window size',
                                     'type': 'number'}]},
                 'convert_nfcapd_csv':
                    {'parameters': [{'name': 'File name',
                                     'type': 'text'}]},
                 'convert_csv_flows':
                    {'parameters': [{'name': 'Sample size',
                                    'type': 'number'},
                                   {'name': 'Aggregation size',
                                    'type': 'number'},
                                   {'name': 'Flow label',
                                    'type': 'number'}]},
                'merge_flows':
                    {'parameters': [{'name': 'Dataset name',
                                     'type': 'text'}]}}

    return render_template('creation/parameters.html',
                           parameters=functions[function]['parameters'],
                           url=f'creation.{function}')


@bp.route('/split_pcap', methods=['GET', 'POST'])
def split_pcap():
    gatherer.split_pcap(session['path'],
                        session['files'],
                        int(request.form['split_size']))

    return redirect(url_for('creation.content',
                            function=session['function'],
                            dir=session['dir']))


@bp.route('/convert_pcap_nfcapd', methods=['GET', 'POST'])
def convert_pcap_nfcapd():
    gatherer.convert_pcap_nfcapd(session['path'],
                                 session['files'],
                                 paths['nfcapd'],
                                 request.form['time_window_size'])

    return redirect(url_for('creation.content',
                            function=session['function'],
                            dir=session['dir']))


@bp.route('/convert_nfcapd_csv', methods=['GET', 'POST'])
def convert_nfcapd_csv():
    gatherer.convert_nfcapd_csv(session['path'],
                                session['files'],
                                f'{paths["csv"]}/raw/',
                                request.form['file_name'])

    return redirect(url_for('creation.content',
                            function=session['function'],
                            dir=session['dir']))


@bp.route('/convert_csv_flows', methods=['GET', 'POST'])
def convert_csv_flows():
    for file in session['files']:
        header, flows = gatherer.open_csv(session['path'],
                                          file,
                                          int(request.form['sample_size']))

        fomatter = Formatter(header, flows)
        header = formatter.format_header()
        flows = formatter.format_flows()

        modifier = Modifier(header, flows)
        if int(request.form['aggregation_size']):
            header, flows = modifier.aggregate_flows(
                                     int(request.form['aggregation_size']))
        header, flows = modifier.create_features(
                                 int(request.form['flow_label']))

        export_flows_csv(header, flows,
                         f'{paths["csv"]}/flows/',
                         f'{file.split(".csv")[0]}_s{len(flows)}.csv')

    return redirect(url_for('creation.content',
                            function=session['function'],
                            dir=session['dir']))


@bp.route('/merge_flows', methods=['GET', 'POST'])
def merge_flows():
    for file in session['files']:
        header, flows = gatherer.open_csv(session['path'],
                                          file)

        export_flows_csv(header, flows,
                         f'{paths["csv"]}/datasets/',
                         f'{request.form["dataset_name"]}.csv')

    return redirect(url_for('creation.content',
                            function=session['function'],
                            dir=session['dir']))
