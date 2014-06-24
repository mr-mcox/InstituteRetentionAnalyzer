from InstituteRetentionAnalyzer.munging.cmpp_file import *
import pandas as pd
import datetime

def test_rename_cmpp_columns():
	orig_df = pd.DataFrame(columns = ["Person Id", "Status", "Date (that CM showed up at institute or that they departed)","First Name","Last Name"])
	new_df = rename_cmpp_columns(orig_df)
	assert(set(new_df.columns) == set(['pid','release_code','release_date','first_name','last_name']))

def test_add_er_pending():
	df = pd.DataFrame({
					'pid'          : [1],
					'release_code' : [None]
					})
	cmpp_df = pd.DataFrame({
					'pid'          : [1],
					'release_code' : ['ER PENDING']
					})
	result = add_er_pending(df,cmpp_df)
	assert(result.set_index('pid').loc[1,'release_code']=="ER PENDING")

def test_no_overwrite_existing_code():
	df = pd.DataFrame({
					'pid'          : [1],
					'release_code' : ['RESIGNED']
					})
	cmpp_df = pd.DataFrame({
					'pid'          : [1],
					'release_code' : ['ER PENDING']
					})
	result = add_er_pending(df,cmpp_df)
	assert(result.set_index('pid').loc[1,'release_code']=="RESIGNED")


def test_no_overwrite_if_not_er_pending():
	df = pd.DataFrame({
					'pid'          : [1],
					'release_code' : [None]
					})
	cmpp_df = pd.DataFrame({
					'pid'          : [1],
					'release_code' : ['Gobledygook']
					})
	result = add_er_pending(df,cmpp_df)
	assert(result.set_index('pid').loc[1,'release_code'] is None)

def test_add_er_pending_includes_date():
	df = pd.DataFrame({
					'pid'          : [1],
					'release_code' : [None],
					'release_date' : [None]
					})
	cmpp_df = pd.DataFrame({
					'pid'          : [1],
					'release_code' : ['ER PENDING'],
					'release_date' : [datetime.datetime(2014,5,25)]
					})
	result = add_er_pending(df,cmpp_df)
	assert(result.set_index('pid').loc[1,'release_date']==datetime.datetime(2014,5,25))