from scripts.network_analysis import retrieve_spreadsheet_records, extract_record_entities
from scripts.network_analysis import generate_graph, add_entities, add_record_links
from scripts.data_wrangling import *

category_records = retrieve_spreadsheet_records(record_type='categories')

entity_records = retrieve_spreadsheet_records(record_type='entities')
entity_records = lowercase_headers(entity_records)

categorized_persons = retrieve_spreadsheet_records("categories")
categorized_persons = lowercase_headers(categorized_persons)
# we convert these into a dataframe for easier selection
cat_p_df = pd.DataFrame(categorized_persons)
cat_p_df['fullname'] = cat_p_df.apply(lambda row: get_entity_name(entity=row), axis=1)

relationship_records = retrieve_spreadsheet_records(record_type='relationships')
entity_roles = {get_entity_name(record): [record['prs_role1'], record['prs_role2'], record['prs_role3']] for record in entity_records}
for k in entity_roles:
    nr = [e for e in entity_roles[k] if e != '']
    entity_roles[k]= nr

entity_category = {get_entity_name(entity = record): record.get('prs_category') or 'unknown' for record in entity_records}

periods = {
    1950:{'start': 1950, 'end': 1959},
    1960:{'start': 1960, 'end': 1969},
    1970:{'start': 1970, 'end': 1985},
}