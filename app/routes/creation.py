import logging

from flask import (Blueprint, redirect, request,
                   render_template, session, url_for)

from app.core import gatherer, tools
from app.core.preprocess import Formatter, Modifier
from app.forms.creation import (ContentForm, ConvertNfcapdCsvForm,
                                ConvertPcapNfcapdForm, MergingFlowsForm,
                                PreprocessingFlowsForm, SplitPcapForm)
from app.paths import paths, root


bp = Blueprint('creation', __name__)
logger = logging.getLogger('creation')


@bp.route('/content/<function>/<directory>/', methods=['GET', 'POST'])
def content(function, directory):
    form = ContentForm(request.form)

    # clearing the previous directory.
    if directory in ['pcap', 'nfcapd', 'csv']:
        paths_hist = {'root': root}
    else:
        paths_hist = session['paths_hist']

    # checking if the folder was already opened.
    if not directory in paths_hist.keys():
        paths_hist[directory] = f'{directory}/'

    # creating the full path.
    full_path = paths_hist['root'] + paths_hist[directory]
    # getting inner directory content.
    inner_dirs, files = tools.get_content(full_path)
    form.files_choices(files)

    if request.method == 'POST' and form.validate_on_submit():
        session['files'] = form.files.data
        return redirect(url_for(f'creation.{function}', directory=directory))

    # creating the paths of the inner directories.
    for inner_dir in inner_dirs:
        paths_hist[inner_dir] = f'{paths_hist[directory]}{inner_dir}/'

    session['paths_hist'] = paths_hist

    return render_template('creation/content.html',
                           form=form,
                           inner_dirs=inner_dirs,
                           relative_path=session['paths_hist'][directory],
                           function=function)


@bp.route('/parameters/split_pcap/<directory>/', methods=['GET', 'POST'])
def split_pcap(directory):
    form = SplitPcapForm()

    if request.method == 'POST' and form.validate_on_submit():
        path = (session['paths_hist']['root'] +
                session['paths_hist'][directory])
        logger.info(f'path: {path} file: {session["files"]}')

        gatherer.split_pcap(path, session['files'], form.split.data)

        return redirect(url_for('creation.content',
                                function='split_pcap',
                                directory=directory))
    return render_template('creation/split_pcap.html', form=form)


@bp.route('/parameters/convert_pcap_nfcapd/<directory>/',
          methods=['GET', 'POST'])
def convert_pcap_nfcapd(directory):
    form = ConvertPcapNfcapdForm()

    if request.method == 'POST' and form.validate_on_submit():
        path = (session['paths_hist']['root'] +
                session['paths_hist'][directory])
        logger.info(f'path: {path} file: {session["files"]}')

        gatherer.convert_pcap_nfcapd(path, session['files'],
                                     paths['nfcapd'], form.window.data)

        return redirect(url_for('creation.content',
                                function='convert_pcap_nfcapd',
                                directory=directory))
    return render_template('creation/convert_pcap_nfcapd.html', form=form)


@bp.route('/parameters/convert_nfcapd_csv/<directory>/',
          methods=['GET', 'POST'])
def convert_nfcapd_csv(directory):
    form = ConvertNfcapdCsvForm()

    if request.method == 'POST' and form.validate_on_submit():
        path = (session['paths_hist']['root'] +
                session['paths_hist'][directory])
        logger.info(f'path: {path} file: {session["files"]}')

        gatherer.convert_nfcapd_csv(path, session['files'],
                                    f'{paths["csv"]}/raw/', form.name.data)

        return redirect(url_for('creation.content',
                                function='convert_nfcapd_csv',
                                directory=directory))
    return render_template('creation/convert_nfcapd_csv.html', form=form)


@bp.route('/parameters/preprocessing_flows/<directory>/',
          methods=['GET', 'POST'])
def preprocessing_flows(directory):
    form = PreprocessingFlowsForm()

    if request.method == 'POST' and form.validate_on_submit():
        path = (session['paths_hist']['root'] +
                session['paths_hist'][directory])
        logger.info(f'path: {path} file: {session["files"]}')

        for file in session['files']:
            # gathering flows.
            header, flows = gatherer.open_csv(path, file, form.sample.data)
            # preprocessing flows.
            formatter = Formatter(header, flows)
            header = formatter.format_header()
            flows = formatter.format_flows()

            modifier = Modifier(header, flows,
                                label=form.label.data,
                                threshold=form.threshold.data)
            header = modifier.extend_header()
            flows = list()
            while getattr(modifier, 'flows'):
                flow = modifier.aggregate_flow()
                flows.append(flow)

            # exporting flows.
            name = file.split(".csv")[0]
            tools.export_flows_csv(header, flows,
                                   f'{paths["csv"]}/flows/',
                                   f'{name}_s{len(flows)}.csv')

        return redirect(url_for('creation.content',
                                function='preprocessing_flows',
                                directory=directory))
    return render_template('creation/preprocessing_flows.html', form=form)


@bp.route('/parameters/merging_flows/<directory>/',
          methods=['GET', 'POST'])
def merging_flows(directory):
    form = MergingFlowsForm()

    if request.method == 'POST' and form.validate_on_submit():
        path = (session['paths_hist']['root'] +
                session['paths_hist'][directory])
        logger.info(f'path: {path} file: {session["files"]}')

        for file in session['files']:
            header, flows = gatherer.open_csv(path, file)

            tools.export_flows_csv(header, flows,
                                   f'{paths["csv"]}/datasets/',
                                   f'{form.name.data}.csv')

        return redirect(url_for('creation.content',
                                function='merging_flows',
                                directory=directory))
    return render_template('creation/merging_flows.html', form=form)
