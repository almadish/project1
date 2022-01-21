import os
import csv
import random
import pytest
import pandas as pd
from solution import *

random.seed(45)

def remove_null_records(expected_users_data):
  expected_users_data_non_null = list()
  for record in expected_users_data:
    flag = False
    for value in record.values():
      if value == "NULL":
        flag = True
        break
    if not flag:
      expected_users_data_non_null.append(record)
  return expected_users_data_non_null

def remove_invalid_handles(expected_users_data):
  data_valid_handles = []
  for record in expected_users_data:
    if record['handle'].isalnum():
      data_valid_handles.append(record)
  return data_valid_handles


users_data_filepath = os.path.join(os.getcwd(), "data/users.csv")
expected_users_df = pd.read_csv(users_data_filepath)
expected_users_df_non_null = expected_users_df.dropna()

expected_users_data = list(csv.DictReader(open(users_data_filepath, "r")))
expected_users_data_non_null = remove_null_records(expected_users_data)

@pytest.fixture
def state():
  return random.choice(expected_users_df["state"].unique())

@pytest.fixture
def affinity_type():
  return random.choice([x for x in expected_users_df.columns if 'affinity' in x])

@pytest.fixture
def old_domain():
  return "@dmoz.org"

@pytest.fixture
def new_domain():
  return "@dmoz.com"

@pytest.fixture
def save_path():
  return os.path.join(os.getcwd(), "data/users_clean.csv")

class Tests:
  def test_get_csv_data_shape(self):
    actual_users_data = get_csv_data(users_data_filepath)
    assert actual_users_data != None
    assert len(actual_users_data) == expected_users_df.shape[0]
    assert all([len(x) == expected_users_df.shape[1] for x in actual_users_data])

  def test_remove_rows_with_null_valued_fields_shape(self):
    returned_data = remove_rows_with_null_valued_fields(expected_users_data)
    true_num_fields = len(expected_users_data[0])
    assert returned_data != None
    assert len(returned_data) == len(expected_users_data_non_null)
    assert all([len(x) == true_num_fields for x in returned_data])

  def test_remove_rows_with_null_valued_fields_value(self):
    returned_data = remove_rows_with_null_valued_fields(expected_users_data)
    assert returned_data != None
    count = 0
    for record in returned_data:
      for value in record.values():
        if value == 'NULL':
          count += 1
    assert count == 0

  def test_remove_rows_with_invalid_handles_shape(self):
    returned_data = remove_rows_with_invalid_handles(expected_users_data)
    true_data = remove_invalid_handles(expected_users_data)
    check_len = len(true_data[0])
    assert returned_data != None
    assert len(returned_data) == len(true_data)
    assert all([len(x) == check_len for x in returned_data])

  def test_remove_rows_with_invalid_handles_value(self):
    returned_data = remove_rows_with_invalid_handles(expected_users_data)
    true_data = remove_invalid_handles(expected_users_data)
    assert returned_data != None
    assert len(returned_data) == len(true_data)
    assert returned_data == true_data
    count = 0
    for record in returned_data:
      if not record['handle'].isalnum():
        count += 1
      
    assert count == 0

  def test_remove_rows_under_affinity_id_level_shape(self, affinity_type):
    threshold = int(random.choice(expected_users_df_non_null[~expected_users_df_non_null[affinity_type].isnull()][affinity_type].unique()))
    actual_users_data_removed_affinity_threshold = remove_rows_over_affinity_id_level(expected_users_data_non_null, affinity_type, threshold)
    expected_users_df_non_null[affinity_type] = expected_users_df_non_null[affinity_type].astype(int)
    expected_users_df_removed_affinity_threshold = expected_users_df_non_null[expected_users_df_non_null[affinity_type] <= threshold]

    assert actual_users_data_removed_affinity_threshold != None
    assert len(actual_users_data_removed_affinity_threshold) == expected_users_df_removed_affinity_threshold.shape[0]
    assert all([len(x) == expected_users_df_removed_affinity_threshold.shape[1] for x in actual_users_data_removed_affinity_threshold])

  def test_remove_rows_over_affinity_id_level_value(self, affinity_type):
    threshold = int(random.choice(
      expected_users_df_non_null[~expected_users_df_non_null[affinity_type].isnull()][affinity_type].unique()))
    returned_data = remove_rows_over_affinity_id_level(expected_users_data_non_null, affinity_type, threshold)

    count = 0
    for record in returned_data:
      if int(record[affinity_type]) > threshold:
        count += 1
    assert returned_data != None
    assert count == 0

  def test_replace_email_domain_shape(self, old_domain, new_domain):
    actual_users_data_replaced_email = replace_email_domain(expected_users_data, old_domain, new_domain)
    expected_users_df["email"] = expected_users_df["email"].str.replace(old_domain, new_domain)

    assert actual_users_data_replaced_email != None
    assert len(actual_users_data_replaced_email) == expected_users_df.shape[0]
    assert all([len(x) == expected_users_df.shape[1] for x in actual_users_data_replaced_email])

  def test_replace_email_domain_value(self, old_domain, new_domain):
    actual_users_data_replaced_email = replace_email_domain(expected_users_data, old_domain, new_domain)

    count = 0
    for record in actual_users_data_replaced_email:
      if old_domain in record["email"]:
        count += 1
    assert actual_users_data_replaced_email != None
    assert count == 0

  def test_save_csv_data(self, save_path):
    assert os.path.exists(save_path)
    assert os.stat(save_path).st_size > 100

  def test_get_average_and_median_affinity_id(self, affinity_type):
    returned_average, returned_median = get_average_and_median_affinity_id(expected_users_data_non_null, affinity_type)
    expected_affinity_average = expected_users_df_non_null[affinity_type].mean()
    expected_affinity_median = expected_users_df_non_null[affinity_type].median()
    assert returned_average != None
    assert returned_median != None
    assert returned_average == expected_affinity_average
    assert returned_median == expected_affinity_median