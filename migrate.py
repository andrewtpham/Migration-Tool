from flask import Flask, request
from flask_cors import CORS, cross_origin
import traceback
import coreapi
from DataConnectors.CSVFileConnector import CSVFileConnector
from DataConnectors.CSVFolderConnector import CSVFolderConnector

import json

import numpy as np
import pandas as pd

url = ""
token = ""

try:
    # Initialize a client & load the schema document
    client = coreapi.Client()

    # Authentification
    auth = coreapi.auth.TokenAuthentication(
        token=token,
    )
    client = coreapi.Client(auth=auth)

    schema = client.get(url)
except Exception as e:
    print("Couldn't initialize Client.")
    traceback.print_exc()
    exit

connector = CSVFolderConnector("./import_csv/")

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)


def create_item(endpoint, params):
    try:
        return client.action(schema, [endpoint, "create"], params)
    except coreapi.exceptions.ParameterError as pe:
        return pe


def get_items(endpoint):
    return client.action(schema, [endpoint, "list"])


if __name__ == '__main__':
    # tolaDataScheme = client.getTolaDataScheme()
    tolaDataScheme = json.load(open('./endpointConfiguration.json'))

    # organisation
    organizations = {item.get('name'): item.get('url')
                     for item in get_items('organization')}


@app.route('/tola-scheme', methods=['GET'])
def get_tola_scheme():
    return json.dumps(tolaDataScheme)


@app.route('/input-scheme', methods=['GET'])
def get_input_scheme():
    return connector.get_input_scheme()


@app.route('/get-organizations', methods=['GET'])
def get_organizations():
    return json.dumps(list(organizations.keys()))


@app.route('/migrate', methods=['POST'])
@cross_origin()
def migrate():
    data = request.json
    couples = data.get('mapping')
    data_mapping = pd.DataFrame(couples)
    split = data_mapping['pair'].apply(lambda x: pd.Series(x.split(' ⟷ ')))
    data_mapping.drop('pair', axis=1, inplace=True)
    data_mapping = pd.concat([split, data_mapping], axis=1)
    data_mapping.columns = ['input_endpoint', 'tola_endpoint', 'input', 'tola']
    data_groups = data_mapping.groupby(['tola_endpoint'])

    organization_url = organizations.get(data.get('organization'))

    '''
    Order:

    Organisation, Sector, Workflowlevel1, Stakeholders, 
    Level, Objective, DisaggregationType, DisaggregationLabel, 
    Indicator, Siteprofile, WorkflowLevel2, PeriodicTarget, 
    CollectedData
    '''

    data = json.loads(connector.get_data())
    responses = {}

    # country
    country = {item.get('country'): item.get('url')
               for item in get_items('country')}

    # sector
    try:
        sector_mapping = data_groups.get_group('sector').set_index(
            'tola', drop=True).drop(['input_endpoint'], axis=1)
        sector_import = data_groups.get_group(
            'sector')['input_endpoint'].iloc[0]

        sector_params = pd.DataFrame()
        for item in sector_mapping.itertuples():
            sector_params[str(item.Index)] = list(json.loads(
                data.get(sector_import)).get(str(item.input)).values())

        sector_params['organization'] = organization_url

        responses['sector_response'] = list(
            map(lambda x: create_item('sector', x), sector_params.to_dict(orient='records')))

    except KeyError:
        pass

    sector = {item.get('sector'): item.get('url')
              for item in get_items('sector')}

    # stakeholder
    try:
        stakeholder_mapping = data_groups.get_group('stakeholder').set_index(
            'tola', drop=True).drop(['input_endpoint'], axis=1)
        stakeholder_import = data_groups.get_group(
            'stakeholder')['input_endpoint'].iloc[0]

        stakeholder_params = pd.DataFrame()
        for item in stakeholder_mapping.itertuples():
            stakeholder_params[str(item.Index)] = list(json.loads(
                data.get(stakeholder_import)).get(str(item.input)).values())

        stakeholder_params.replace({'country': country}, inplace=True)
        stakeholder_params['sectors'] = [[] if item is None else [sector.get(
            item)] for item in stakeholder_params['sectors']]
        stakeholder_params['organization'] = organization_url

        responses['stakeholder_response'] = list(
            map(lambda x: create_item('stakeholder', x), stakeholder_params.to_dict(orient='records')))

    except KeyError:
        pass

    stakeholder = {item.get('stakeholder'): item.get('url')
                   for item in get_items('stakeholder')}

    # workflowlevel1
    try:
        workflowlevel1_mapping = data_groups.get_group('workflowlevel1').set_index(
            'tola', drop=True).drop(['input_endpoint'], axis=1)
        workflowlevel1_import = data_groups.get_group(
            'workflowlevel1')['input_endpoint'].iloc[0]

        workflowlevel1_params = pd.DataFrame()
        for item in workflowlevel1_mapping.itertuples():
            workflowlevel1_params[str(item.Index)] = list(json.loads(
                data.get(workflowlevel1_import)).get(str(item.input)).values())

        workflowlevel1_params.replace({'country': country}, inplace=True)
        workflowlevel1_params['sectors'] = [sector.get(
            item) for item in workflowlevel1_params['sectors']]
        workflowlevel1_params['sub_sectors'] = [sector.get(
            item) for item in workflowlevel1_params['sub_sectors']]
        workflowlevel1_params['organization'] = organization_url

        responses['workflowlevel1_response'] = list(
            map(lambda x: create_item('workflowlevel1', x), workflowlevel1_params.to_dict(orient='records')))

    except KeyError:
        pass

    workflowlevel1 = {item.get('workflowlevel1'): item.get('url')
                      for item in get_items('workflowlevel1')}

    # milestone
    try:
        milestone_mapping = data_groups.get_group('milestone').set_index(
            'tola', drop=True).drop(['input_endpoint'], axis=1)
        milestone_import = data_groups.get_group(
            'milestone')['input_endpoint'].iloc[0]

        milestone_params = pd.DataFrame()
        for item in milestone_mapping.itertuples():
            milestone_params[str(item.Index)] = list(json.loads(
                data.get(milestone_import)).get(str(item.input)).values())

        milestone_params.replace(
            {'workflowlevel1': workflowlevel1}, inplace=True)
        milestone_params['organization'] = organization_url

        responses['milestone_response'] = list(
            map(lambda x: create_item('milestone', x), milestone_params.to_dict(orient='records')))

    except KeyError:
        pass

    milestone = {item.get('milestone'): item.get('url')
                 for item in get_items('milestone')}

    # level
    try:
        level_mapping = data_groups.get_group('level').set_index(
            'tola', drop=True).drop(['input_endpoint'], axis=1)
        level_import = data_groups.get_group(
            'level')['input_endpoint'].iloc[0]

        level_params = pd.DataFrame()
        for item in level_mapping.itertuples():
            level_params[str(item.Index)] = list(json.loads(
                data.get(level_import)).get(str(item.input)).values())

        level_params.replace({'workflowlevel1': workflowlevel1}, inplace=True)
        level_params.replace({'country': country}, inplace=True)
        level_params['organization'] = organization_url
        level_params['description'].replace([None], [""], inplace=True)

        responses['level_response'] = list(
            map(lambda x: create_item('level', x), level_params.to_dict(orient='records')))

    except KeyError:
        pass

    level = {item.get('level'): item.get('url')
             for item in get_items('level')}

    # objective
    try:
        objective_mapping = data_groups.get_group('objective').set_index(
            'tola', drop=True).drop(['input_endpoint'], axis=1)
        objective_import = data_groups.get_group(
            'objective')['input_endpoint'].iloc[0]

        objective_params = pd.DataFrame()
        for item in objective_mapping.itertuples():
            objective_params[str(item.Index)] = list(json.loads(
                data.get(objective_import)).get(str(item.input)).values())

        objective_params.replace(
            {'workflowlevel1': workflowlevel1}, inplace=True)
        objective_params['description'].replace([None], [""], inplace=True)

        responses['objective_response'] = list(
            map(lambda x: create_item('objective', x), objective_params.to_dict(orient='records')))

    except KeyError:
        pass

    objective = {item.get('objective'): item.get('url')
                 for item in get_items('objective')}

    # disaggregationtype
    try:
        disaggregationtype_mapping = data_groups.get_group('disaggregationtype').set_index(
            'tola', drop=True).drop(['input_endpoint'], axis=1)
        disaggregationtype_import = data_groups.get_group(
            'disaggregationtype')['input_endpoint'].iloc[0]

        disaggregationtype_params = pd.DataFrame()
        for item in disaggregationtype_mapping.itertuples():
            disaggregationtype_params[str(item.Index)] = list(json.loads(
                data.get(disaggregationtype_import)).get(str(item.input)).values())
        disaggregationtype_params['organization'] = organization_url
        disaggregationtype_params['description'].replace(
            [None], [""], inplace=True)

        responses['disaggregationtype_response'] = list(
            map(lambda x: create_item('disaggregationtype', x), disaggregationtype_params.to_dict(orient='records')))

    except KeyError:
        pass

    disaggregation_type = {item.get('disaggregationtype'): item.get('url')
                           for item in get_items('disaggregationtype')}

    # disaggregationlabel
    try:
        disaggregationlabel_mapping = data_groups.get_group('disaggregationlabel').set_index(
            'tola', drop=True).drop(['input_endpoint'], axis=1)
        disaggregationlabel_import = data_groups.get_group(
            'disaggregationlabel')['input_endpoint'].iloc[0]

        disaggregationlabel_params = pd.DataFrame()
        for item in disaggregationlabel_mapping.itertuples():
            disaggregationlabel_params[str(item.Index)] = list(json.loads(
                data.get(disaggregationlabel_import)).get(str(item.input)).values())

        disaggregationlabel_params.replace(
            {'disaggregation_type': disaggregation_type}, inplace=True)

        responses['disaggregationlabel_response'] = list(
            map(lambda x: create_item('disaggregationlabel', x), disaggregationlabel_params.to_dict(orient='records')))

    except KeyError:
        pass

    # disaggregationvalue
    try:
        disaggregationlabel_mapping = data_groups.get_group('disaggregationvalue').set_index(
            'tola', drop=True).drop(['input_endpoint'], axis=1)
        disaggregationlabel_import = data_groups.get_group(
            'disaggregationvalue')['input_endpoint'].iloc[0]

        disaggregationlabel_params = pd.DataFrame()
        for item in disaggregationlabel_mapping.itertuples():
            disaggregationlabel_params[str(item.Index)] = list(json.loads(
                data.get(disaggregationlabel_import)).get(str(item.input)).values())

        disaggregationlabel_params.replace(
            {'disaggregation_type': disaggregation_type}, inplace=True)

        responses['disaggregationvalue_response'] = list(
            map(lambda x: create_item('disaggregationvalue', x), disaggregationlabel_params.to_dict(orient='records')))

    except KeyError:
        pass
    
    disaggregation_value = {item.get('disaggregationvalue'): item.get('url')
                           for item in get_items('disaggregationvalue')}

    # indicator
    try:
        indicator_mapping = data_groups.get_group('indicator').set_index(
            'tola', drop=True).drop(['input_endpoint'], axis=1)
        indicator_import = data_groups.get_group(
            'indicator')['input_endpoint'].iloc[0]

        indicator_params = pd.DataFrame()
        for item in indicator_mapping.itertuples():
            indicator_params[str(item.Index)] = list(json.loads(
                data.get(indicator_import)).get(str(item.input)).values())

        indicator_params.replace(
            {'workflowlevel1': workflowlevel1}, inplace=True)
        indicator_params['objectives'] = [[] if item is None else [objective.get(
            item)] for item in indicator_params['objectives']]
        indicator_params['dissagregation'] = [[] if item is None else [disaggregation_type.get(
            item)] for item in indicator_params['dissagregation']]

        responses['indicator_response'] = list(
            map(lambda x: create_item('indicator', x), indicator_params.to_dict(orient='records')))

    except KeyError:
        pass

    indicator = {item.get('name'): item.get('url')
                 for item in get_items('indicator')}

    # siteprofile
    try:
        siteprofile_mapping = data_groups.get_group('siteprofile').set_index(
            'tola', drop=True).drop(['input_endpoint'], axis=1)
        siteprofile_import = data_groups.get_group(
            'siteprofile')['input_endpoint'].iloc[0]

        siteprofile_params = pd.DataFrame()
        for item in siteprofile_mapping.itertuples():
            siteprofile_params[str(item.Index)] = list(json.loads(
                data.get(siteprofile_import)).get(str(item.input)).values())

        siteprofile_params.replace({'country': country}, inplace=True)
        siteprofile_params['contact_number'].replace(
            [np.nan], [None], inplace=True)
        siteprofile_params['organization'] = organization_url

        responses['siteprofile_response'] = list(
            map(lambda x: create_item('siteprofile', x), siteprofile_params.to_dict(orient='records')))

    except KeyError:
        pass

    siteprofile = {item.get('siteprofile'): item.get('url')
                   for item in get_items('siteprofile')}

    # workflowlevel2
    try:
        workflowlevel2_mapping = data_groups.get_group('workflowlevel2').set_index(
            'tola', drop=True).drop(['input_endpoint'], axis=1)
        workflowlevel2_import = data_groups.get_group(
            'workflowlevel2')['input_endpoint'].iloc[0]

        workflowlevel2_params = pd.DataFrame()
        for item in workflowlevel2_mapping.itertuples():
            workflowlevel2_params[str(item.Index)] = list(json.loads(
                data.get(workflowlevel2_import)).get(str(item.input)).values())

        workflowlevel2_params.replace(
            {'workflowlevel1': workflowlevel1}, inplace=True)
        workflowlevel2_params.replace({'milestone': milestone}, inplace=True)
        workflowlevel2_params.replace(
            {'stakeholder': stakeholder}, inplace=True)
        workflowlevel2_params['indicators'] = [[] if item is None else indicator.get(
            item) for item in workflowlevel2_params['indicators']]
        workflowlevel2_params['stakeholder'] = [[] if item is None else [stakeholder.get(
            item)] for item in workflowlevel2_params['stakeholder']]
        workflowlevel2_params['siteprofile'] = [[] if item is None else [siteprofile.get(
            item)] for item in workflowlevel2_params['siteprofile']]

        responses['workflowlevel2_response'] = list(
            map(lambda x: create_item('workflowlevel2', x), workflowlevel2_params.to_dict(orient='records')))

    except KeyError:
        pass

    workflowlevel2 = {item.get('workflowlevel2'): item.get('url')
                      for item in get_items('workflowlevel2')}

    # periodictarget
    try:
        periodictarget_mapping = data_groups.get_group('periodictarget').set_index(
            'tola', drop=True).drop(['input_endpoint'], axis=1)
        periodictarget_import = data_groups.get_group(
            'periodictarget')['input_endpoint'].iloc[0]

        periodictarget_params = pd.DataFrame()
        for item in periodictarget_mapping.itertuples():
            periodictarget_params[str(item.Index)] = list(json.loads(
                data.get(periodictarget_import)).get(str(item.input)).values())

        periodictarget_params.replace(
            {'indicator': indicator}, inplace=True)

        responses['periodictarget_response'] = list(
            map(lambda x: create_item('periodictarget', x), periodictarget_params.to_dict(orient='records')))

    except KeyError:
        pass

    periodic_target = {item.get('periodictarget'): item.get('url')
                       for item in get_items('periodictarget')}

    # collecteddata
    try:
        collecteddata_mapping = data_groups.get_group('collecteddata').set_index(
            'tola', drop=True).drop(['input_endpoint'], axis=1)
        collecteddata_import = data_groups.get_group(
            'collecteddata')['input_endpoint'].iloc[0]

        collecteddata_params = pd.DataFrame()
        for item in collecteddata_mapping.itertuples():
            collecteddata_params[str(item.Index)] = list(json.loads(
                data.get(collecteddata_import)).get(str(item.input)).values())

        collecteddata_params.replace(
            {'periodic_target': periodic_target}, inplace=True)
        collecteddata_params.replace(
            {'indicator': indicator}, inplace=True)
        collecteddata_params.replace(
            {'workflowlevel1': workflowlevel1}, inplace=True)
        collecteddata_params['siteprofile'] = [list() if item is None else [siteprofile.get(
            item)] for item in collecteddata_params['siteprofile']]
        collecteddata_params['disaggregation_value'] = [[] if item is None else [disaggregation_value.get(
            item)] for item in collecteddata_params['disaggregation_value']]
        
        print(collecteddata_params)


        responses['collecteddata_response'] = list(
            map(lambda x: create_item('collecteddata', x), collecteddata_params.to_dict(orient='records')))

    except KeyError:
        pass

    print(responses)

    return ""


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
