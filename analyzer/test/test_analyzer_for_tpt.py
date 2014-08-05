import pytest
from InstituteRetentionAnalyzer.analyzer.analyzer_for_tpt import TPTRetention
import pandas as pd
from datetime import datetime

@pytest.fixture
def institute_start_date_df():
	return pd.DataFrame({'institute' : ['Atlanta','Chicago','Phoenix'],'start_date' : [datetime(2014,6,1),datetime(2014,6,15),datetime(2014,6,1)]})

@pytest.fixture
def empty_tpt_analyzer():
	return TPTRetention()

@pytest.fixture
def tpt_analyzer_with_institute_transfer():
	#CM 1 transfered from the Atlanta institute in week 4 to week 2 of Chicago. CM 2 completed all 5 weeks in Chicago
	analyzer = TPTRetention()
	analyzer.cm_history_cleaned = pd.DataFrame({
								'pid'                         : [1,1,1,2],
								'week'                        : [4,2,2,3],
								'history_id'                  : [1,2,3,4],
								'institute'                   : ['Atlanta','Chicago','Chicago','Chicago'],
								'is_notable_institute_record' : [True,True,False,False],
								'is_first_institute'          : [True,False,False,True],
								'is_transfer_out'             : [True,False,False,False],
								'is_transfer_in'              : [False,True,False,False],

								})
	analyzer.exit_data_cleaned = pd.DataFrame({
							'pid'  : [1,2],
							'week' : [None,None],
							'institute': ['Chicago','Chicago'],
							'release_code' : [None,None]
							})

	return analyzer

@pytest.fixture
def tpt_analyzer_with_institute_transfer_and_resignation():
	#CM 1 transfered from the Atlanta institute in week 4 to week 2 of Chicago then resigned in week 4. CM 2 started in Chicago and resigned in week 4
	analyzer = TPTRetention()
	analyzer.cm_history_cleaned = pd.DataFrame({
								'pid'                         : [1,1,1,2],
								'week'                        : [4,2,2,3],
								'history_id'                  : [1,2,3,4],
								'institute'                   : ['Atlanta','Chicago','Chicago','Chicago'],
								'is_notable_institute_record' : [True,True,False,False],
								'is_first_institute'          : [True,False,False,True],
								'is_transfer_out'             : [True,False,False,False],
								'is_transfer_in'              : [False,True,False,False],

								})
	analyzer.exit_data_cleaned = pd.DataFrame({
								'pid'          : [1,2],
								'first_name'   : ['Elliot','William'],
								'last_name'    : ['Stabler','Munch'],
								'week'         : [4,4],
								'institute'    : ['Chicago','Chicago'],
								'release_code' : ['RESIGNED','RESIGNED']
								})
	return analyzer

@pytest.fixture
def tpt_analyzer_with_one_cm_transfer(institute_start_date_df):
	analyzer = TPTRetention()
	analyzer.institute_start_date_df = institute_start_date_df
	analyzer.cm_history_cleaned = pd.DataFrame({
									'pid'                      : [1,1,1],
									'week'                     : [1,2,2],
									'history_record_timestamp' : [datetime(2014,6,1),datetime(2014,6,23),datetime(2014,6,25)],
									'history_id'               : [1,2,3],
									'institute'                : ['Atlanta','Chicago','Chicago'],
								})
	analyzer.exit_data_cleaned = pd.DataFrame({
						'pid'  : [1],
						'week' : [None],
						'institute': ['Chicago'],
						'release_code' : [None]
						})
	return analyzer

@pytest.fixture
def tpt_analyzer_with_cm_that_has_multiple_records_for_first_institute(institute_start_date_df):
	analyzer = TPTRetention()
	analyzer.institute_start_date_df = institute_start_date_df
	analyzer.cm_history_cleaned = pd.DataFrame({
									'pid'                      : [1,2,1,1],
									'week'                     : [1,1,1,2],
									'history_record_timestamp' : [datetime(2014,6,1),datetime(2014,6,1),datetime(2014,6,23),datetime(2014,6,25)],
									'history_id'               : [1,2,3,4],
									'institute'                : ['Atlanta', 'Phoenix', 'Atlanta','Chicago'],
									})
	return analyzer

@pytest.fixture
def tpt_analyzer_with_cm_that_has_start_week_then_transfer(institute_start_date_df):
	analyzer = TPTRetention()
	analyzer.institute_start_date_df = institute_start_date_df
	analyzer.cm_history_cleaned = pd.DataFrame({
									'pid'                      : [1,1,1],
									'week'                     : [1,3,1],
									'history_record_timestamp' : [datetime(2014,6,1),datetime(2014,6,6),datetime(2014,6,19)],
									'history_id'               : [1,2,3],
									'institute'                : ['Phoenix', 'Phoenix','Chicago'],
									})
	analyzer.exit_data_cleaned = pd.DataFrame({
					'pid'  : [1],
					'week' : [None],
					'institute': ['Chicago'],
					'release_code' : [None]
					})
	return analyzer

@pytest.fixture
def tpt_analyzer_with_cm_boundary():
	analyzer = TPTRetention()
	boundary_records = [
		(1,'Atlanta',0,4),
		(1,'Chicago',2,3),
		(2,'Chicago',0,7),
	]
	analyzer.cm_institute_boundaries = pd.DataFrame.from_records(boundary_records,columns=['pid','institute','start_week','end_week'])
	return analyzer

@pytest.fixture
def tpt_analyzer_with_active_cm_by_week():
	analyzer = TPTRetention()
	records = [
		(1,'Atlanta',0),
		(1,'Atlanta',1),
		(1,'Atlanta',2),
		(1,'Atlanta',3),
		(1,'Atlanta',4),
		(1,'Chicago',2),
		(1,'Chicago',3),
		(2,'Chicago',0),
		(2,'Chicago',1),
		(2,'Chicago',2),
		(2,'Chicago',3),
		(2,'Chicago',4),
		(2,'Chicago',5),
		(2,'Chicago',6),
		(2,'Chicago',7),
	]
	analyzer.active_cms_by_week = pd.DataFrame.from_records(records,columns=['pid','institute','week'])
	return analyzer

@pytest.fixture
def tpt_analyzer_with_count_active_by_week():
	analyzer = TPTRetention()
	records = [
		('Atlanta',0,4),
		('Atlanta',1,3),
		('Atlanta',2,2),
	]
	analyzer.count_of_active_cms_by_week = pd.DataFrame.from_records(records,columns=['institute','week','count']).set_index(['institute','week'])
	return analyzer

@pytest.fixture
def tpt_analyzer_with_computations():
	analyzer = TPTRetention()
	analyzer.count_of_active_cms_by_week          = pd.DataFrame({'institute':['Atlanta','Atlanta'],'week':[0,1],'count':[4,2]})
	analyzer.release_code_count_by_institute_week = pd.DataFrame({'institute':['Atlanta'],'week':[1],'count':[1],'release_code':['RESIGNED']})
	analyzer.transfer_in_count_by_institute_week  = pd.DataFrame({'institute':['Atlanta'],'week':[1],'count':[1]})
	analyzer.transfer_out_count_by_institute_week = pd.DataFrame({'institute':['Atlanta'],'week':[1],'count':[1]})
	analyzer.percent_active_by_week               = pd.DataFrame({'institute':['Atlanta','Atlanta'],'week':[0,1],'value':[1,0.5]})
	return analyzer

@pytest.fixture
def tpt_analyzer_with_no_show_input(institute_start_date_df):
	exit_data_cleaned = pd.DataFrame({
		'pid'           : [0,1],
		'release_code'  : ['RESIGNED','NOSHOW'],
		'release_date'  : [datetime(2014,6,1),datetime(2014,6,1)],
		'er_start_date' : [datetime(2014,6,1),datetime(2014,6,1)],
		'institute'     : ["Atlanta","Atlanta"],

									})

	cm_history_cleaned = pd.DataFrame({
		'pid'                      : [0,1],
		'release_code'             : ['RESIGNED','NOSHOW'],
		'history_record_timestamp' : [datetime(2014,6,1),datetime(2014,6,1)],
		'history_id'               : [0,1],
		'institute'                : ["Atlanta","Atlanta"],

									})
	analyzer = TPTRetention(exit_data_cleaned=exit_data_cleaned,institute_start_date_df=institute_start_date_df,cm_history_cleaned=cm_history_cleaned)
	return analyzer


@pytest.fixture
def tpt_analyzer_with_deferred_input(institute_start_date_df):
	exit_data_cleaned = pd.DataFrame({
		'pid'           : [0,1],
		'release_code'  : ['RESIGNED','DEFERRED'],
		'release_date'  : [datetime(2014,6,1),datetime(2014,6,1)],
		'er_start_date' : [datetime(2014,6,1),datetime(2014,6,1)],
		'institute'     : ["Atlanta","Atlanta"],

									})

	cm_history_cleaned = pd.DataFrame({
		'pid'                      : [0,1],
		'release_code'             : ['RESIGNED','DEFERRED'],
		'history_record_timestamp' : [datetime(2014,6,1),datetime(2014,6,1)],
		'history_id'               : [0,1],
		'institute'                : ["Atlanta","Atlanta"],

									})
	analyzer = TPTRetention(exit_data_cleaned=exit_data_cleaned,institute_start_date_df=institute_start_date_df,cm_history_cleaned=cm_history_cleaned)
	return analyzer

@pytest.fixture
def tpt_analyzer_with_history_without_step(institute_start_date_df):
	cm_history_cleaned = pd.DataFrame({
		'pid'                      : [0,1],
		'release_code'             : ['RESIGNED','NOSHOW'],
		'history_record_timestamp' : [datetime(2014,6,1),datetime(2014,6,1)],
		'history_id'               : [0,1],
		'institute'                : ["Atlanta","Atlanta"],
		'step'	                   : ['INSTREG',None]
									})
	analyzer = TPTRetention(institute_start_date_df=institute_start_date_df,cm_history_cleaned=cm_history_cleaned)
	return analyzer

@pytest.fixture
def tpt_analyzer_with_cms_who_started_early(institute_start_date_df):
	exit_data_cleaned = pd.DataFrame({
		'pid'           : [0,1,2],
		'release_code'  : [None,"RESIGNED","NOSHOW"],
		'release_date'  : [None,datetime(2014,6,10),datetime(2014,5,30)],
		'er_start_date' : [None,datetime(2014,6,10),datetime(2014,5,30)],
		'institute'     : ["Atlanta","Atlanta","Atlanta"],

									})

	cm_history_cleaned = pd.DataFrame({
		'pid'                      : [0,0,1,2],
		'history_record_timestamp' : [datetime(2014,5,1),datetime(2014,5,3),datetime(2014,5,3),datetime(2014,5,3)],
		'history_id'               : [0,1,2,3],
		'institute'                : ["Atlanta","Atlanta","Atlanta","Atlanta"],
		'step'	                   : ['PREISNT','INSTREG','INSTREG','PREISNT']

									})
	analyzer = TPTRetention(exit_data_cleaned=exit_data_cleaned,institute_start_date_df=institute_start_date_df,cm_history_cleaned=cm_history_cleaned)
	return analyzer

@pytest.fixture
def tpt_analyzer_with_cm_who_went_to_institute_last_year(institute_start_date_df):
	exit_data_cleaned = pd.DataFrame({
		'pid'           : [0],
		'release_code'  : [None],
		'release_date'  : [datetime(2014,6,10)],
		'er_start_date' : [datetime(2014,6,10)],
		'institute'     : ["Atlanta"],

									})

	cm_history_cleaned = pd.DataFrame({
		'pid'                      : [0],
		'history_record_timestamp' : [datetime(2013,5,1)],
		'history_id'               : [0],
		'institute'                : ["Atlanta"],
		'step'	                   : ['INSTREG']

									})
	analyzer = TPTRetention(exit_data_cleaned=exit_data_cleaned,institute_start_date_df=institute_start_date_df,cm_history_cleaned=cm_history_cleaned)
	return analyzer

@pytest.fixture
def tpt_analyzer_with_sample_data_for_list():
	#CM 1 transfered from the Atlanta institute in week 4 to week 2 of Chicago then resigned in week 4. CM 2 started in Chicago and is is active
	analyzer = TPTRetention()
	analyzer.cm_history_cleaned = pd.DataFrame({
								'pid'                         : [1,1,1,2],
								'first_name'                  : ['Elliot','Elliot','Elliot','William'],
								'last_name'                   : ['Stabler','Stabler','Stabler','Munch'],
								'week'                        : [4,2,2,3],
								'history_id'                  : [1,2,3,4],
								'institute'                   : ['Atlanta','Chicago','Chicago','Chicago'],
								'is_notable_institute_record' : [True,True,False,False],
								'is_first_institute'          : [True,False,False,True],
								'is_transfer_out'             : [True,False,False,False],
								'is_transfer_in'              : [False,True,False,False],

								})
	analyzer.exit_data_cleaned = pd.DataFrame({
								'pid'          : [1,2],
								'first_name'   : ['Elliot','William'],
								'last_name'    : ['Stabler','Munch'],
								'week'         : [4,4],
								'release_date'  : [datetime(2014,6,10),None],
								'institute'    : ['Chicago','Chicago'],
								'release_code' : ['RESIGNED',None]
								})
	return analyzer

def test_exit_by_institute_and_week(empty_tpt_analyzer):
		analyzer = empty_tpt_analyzer
		analyzer.exit_data_cleaned = pd.DataFrame({
										'pid'  : [1,2,3],
										'week' : [1,2,2],
										'institute': ['Chicago','Atlanta','Atlanta'],
										'release_code' : ['RESIGNED','RESIGNED','RESIGNED',]
										})
		analyzer.count_by_release_code()
		assert(analyzer.release_code_count_by_institute_week.loc[('Chicago',1,'RESIGNED'),'count']==1)
		assert(analyzer.release_code_count_by_institute_week.loc[('Atlanta',2,'RESIGNED'),'count']==2)

def test_fill_extra_weeks(empty_tpt_analyzer):
		df = pd.DataFrame({
			'pid'  : [1,2,3],
			'week' : [None,1,2],
			'institute': ['Atlanta','Atlanta','Atlanta'],
			'release_code' : [None,'RESIGNED','RESIGNED',]
			})
		result = empty_tpt_analyzer.fill_extra_weeks(df)
		assert(len(result.ix[(result.pid == 1) & (result.week ==1)].index)>=1)
		assert(len(result.ix[(result.pid == 2) & (result.week ==1)].index)>=1)

def test_mark_notable_institute_assignment_records_for_one_cm(tpt_analyzer_with_one_cm_transfer):
	analyzer = tpt_analyzer_with_one_cm_transfer
	analyzer.mark_notable_institute_assignment_records()
	df = analyzer.cm_history_cleaned.set_index(['pid','history_id']).sortlevel()
	assert(df.loc[(1,1),'is_notable_institute_record'])
	assert(df.loc[(1,2),'is_notable_institute_record'])
	assert( not df.loc[(1,3),'is_notable_institute_record'])

def test_mark_notable_institute_assignment_records_for_multiple_cms(empty_tpt_analyzer, institute_start_date_df):
	analyzer = empty_tpt_analyzer
	analyzer.institute_start_date_df = institute_start_date_df
	analyzer.cm_history_cleaned = pd.DataFrame({
									'pid'        : [1,1,2],
									'week'       : [1,2,2],
									'history_id' : [1,2,3],
									'history_record_timestamp' : [datetime(2014,6,1),datetime(2014,6,1),datetime(2014,6,1)],
									'institute'  : ['Chicago','Atlanta','Phoenix'],
									})
	analyzer.mark_notable_institute_assignment_records()
	df = analyzer.cm_history_cleaned.set_index(['pid','history_id']).sortlevel()
	assert(df.loc[(1,1),'is_notable_institute_record'])
	assert(df.loc[(1,2),'is_notable_institute_record'])
	assert( not df.loc[(2,3),'is_notable_institute_record'])

def test_mark_transfer_in(tpt_analyzer_with_one_cm_transfer):
	analyzer = tpt_analyzer_with_one_cm_transfer
	analyzer.mark_notable_institute_assignment_records()
	df = analyzer.cm_history_cleaned.set_index(['pid','history_id']).sortlevel()
	assert(not df.loc[(1,1),'is_transfer_in'])
	assert(df.loc[(1,2),'is_transfer_in'])

def test_mark_transfer_out(tpt_analyzer_with_one_cm_transfer):
	analyzer = tpt_analyzer_with_one_cm_transfer
	analyzer.mark_notable_institute_assignment_records()
	df = analyzer.cm_history_cleaned.set_index(['pid','history_id']).sortlevel()
	assert(df.loc[(1,1),'is_transfer_out'])
	assert( not df.loc[(1,2),'is_transfer_out'])

def test_mark_transfer_out_with_modified_week(tpt_analyzer_with_one_cm_transfer):
	analyzer = tpt_analyzer_with_one_cm_transfer
	analyzer.mark_notable_institute_assignment_records()
	df = analyzer.cm_history_cleaned.set_index(['pid','history_id']).sortlevel()
	assert(df.loc[(1,1),'week']==4)


def test_count_transfer_in_by_institute_week(tpt_analyzer_with_one_cm_transfer):
	analyzer = tpt_analyzer_with_one_cm_transfer
	analyzer.mark_notable_institute_assignment_records()
	analyzer.count_transfers()
	assert(analyzer.transfer_in_count_by_institute_week.loc[('Chicago',2),'count']==1)

def test_count_transfer_out_by_institute_week(tpt_analyzer_with_one_cm_transfer):
	analyzer = tpt_analyzer_with_one_cm_transfer
	analyzer.mark_notable_institute_assignment_records()
	analyzer.count_transfers()
	assert(analyzer.transfer_out_count_by_institute_week.loc[('Atlanta',4),'count']==1)

def test_mark_first_institute_of_record(empty_tpt_analyzer,institute_start_date_df):
	analyzer = empty_tpt_analyzer
	analyzer.institute_start_date_df = institute_start_date_df
	analyzer.cm_history_cleaned = pd.DataFrame({
									'pid'        : [1,1,1,2],
									'week'       : [-1,2,2,1],
									'history_id' : [1,2,3,4],
									'history_record_timestamp' : [datetime(2014,6,1),datetime(2014,6,1),datetime(2014,6,1),datetime(2014,6,1)],
									'institute'  : ['Chicago','Atlanta','Atlanta','Atlanta'],
									})
	analyzer.mark_notable_institute_assignment_records()
	df = analyzer.cm_history_cleaned.set_index(['pid','history_id']).sortlevel()
	assert(df.loc[(1,2),'is_first_institute'])
	assert(df.loc[(2,4),'is_first_institute'])
	assert(len(df.ix[df.is_first_institute].index)==2)

def test_useful_institute_records(tpt_analyzer_with_institute_transfer):
	analyzer = tpt_analyzer_with_institute_transfer
	analyzer.find_useful_institute_records()
	df = analyzer.useful_institute_records.set_index(['pid','week']).sortlevel()
	assert(df.loc[(1,2),'institute']=="Chicago")
	assert(df.loc[(1,4),'institute']=="Atlanta")
	assert(df.loc[(2,3),'institute']=="Chicago")

def test_cm_institute_boundaries_with_first_record_transfer_out(tpt_analyzer_with_institute_transfer):
	analyzer = tpt_analyzer_with_institute_transfer
	analyzer.create_cm_institute_boundaries()
	df = analyzer.cm_institute_boundaries
	df = df.set_index(['pid','institute','start_week','end_week'])
	assert(df.index.isin([(1,'Atlanta',0,3)]).sum()==1)

def test_cm_institute_boundaries_with_transfer_in(tpt_analyzer_with_institute_transfer):
	analyzer = tpt_analyzer_with_institute_transfer
	analyzer.create_cm_institute_boundaries()
	df = analyzer.cm_institute_boundaries
	df = df.set_index(['pid','institute','start_week','end_week'])
	print(df)
	assert(df.index.isin([(1,'Chicago',2,7)]).sum()==1)

def test_cm_institute_boundaries_for_normal(tpt_analyzer_with_institute_transfer):
	analyzer = tpt_analyzer_with_institute_transfer
	analyzer.create_cm_institute_boundaries()
	df = analyzer.cm_institute_boundaries
	df = df.set_index(['pid','institute','start_week','end_week'])
	print(df)
	assert(df.index.isin([(2,'Chicago',0,7)]).sum()==1)

def test_cm_institute_boundaries_for_resignation(tpt_analyzer_with_institute_transfer_and_resignation):
	analyzer = tpt_analyzer_with_institute_transfer_and_resignation
	analyzer.create_cm_institute_boundaries()
	df = analyzer.cm_institute_boundaries
	df = df.set_index(['pid','institute','start_week','end_week'])
	print(df)
	assert(df.index.isin([(2,'Chicago',0,3)]).sum()==1)

def test_cm_institute_boundaries_for_transfer_and_resignation(tpt_analyzer_with_institute_transfer_and_resignation):
	analyzer = tpt_analyzer_with_institute_transfer_and_resignation
	analyzer.create_cm_institute_boundaries()
	df = analyzer.cm_institute_boundaries
	df = df.set_index(['pid','institute','start_week','end_week'])
	print(df)
	assert(df.index.isin([(1,'Atlanta',0,3)]).sum()==1)
	assert(df.index.isin([(1,'Chicago',2,3)]).sum()==1)

def test_cm_institute_boundaries_for_first_institute_then_transfer(tpt_analyzer_with_cm_that_has_start_week_then_transfer):
	analyzer = tpt_analyzer_with_cm_that_has_start_week_then_transfer
	analyzer.create_cm_institute_boundaries()
	df = analyzer.cm_institute_boundaries
	df = df.set_index(['pid','institute','start_week','end_week'])
	print(df)
	# assert(False)
	assert(df.index.isin([(1,'Phoenix',0,2)]).sum()==1)
	assert(df.index.isin([(1,'Chicago',1,7)]).sum()==1)

def test_create_weeks_active(tpt_analyzer_with_cm_boundary):
	analyzer = tpt_analyzer_with_cm_boundary
	analyzer.create_active_cms_by_week()
	df = analyzer.active_cms_by_week.set_index(['pid','institute']).sortlevel()
	print(df)
	assert(df.index.isin([(1,'Atlanta')]).sum()==5)
	assert(df.index.isin([(1,'Chicago')]).sum()==2)
	assert(df.index.isin([(2,'Chicago')]).sum()==8)
	df = analyzer.active_cms_by_week.set_index(['pid','institute','week']).sortlevel()
	assert(df.index.isin([(1,'Atlanta',0)]).sum()==1)
	assert(df.index.isin([(1,'Atlanta',4)]).sum()==1)

def test_count_active_by_week(tpt_analyzer_with_active_cm_by_week):
	analyzer = tpt_analyzer_with_active_cm_by_week
	analyzer.count_active_cms_by_week()
	df = analyzer.count_of_active_cms_by_week
	assert(df.loc[('Atlanta',0),'count']==1)
	assert(df.loc[('Chicago',2),'count']==2)
	assert(df.loc[('Chicago',4),'count']==1)

def test_count_active_by_week_from_cm_records(tpt_analyzer_with_institute_transfer_and_resignation):
	analyzer = tpt_analyzer_with_institute_transfer_and_resignation
	analyzer.count_active_cms_by_week()
	df = analyzer.count_of_active_cms_by_week
	assert(df.loc[('Atlanta',0),'count']==1)
	assert(df.loc[('Chicago',2),'count']==2)
	assert(df.loc[('Chicago',0),'count']==1)

def test_cm_with_multiple_records_for_first_institute_only_has_one_institute(tpt_analyzer_with_cm_that_has_multiple_records_for_first_institute):
	analyzer = tpt_analyzer_with_cm_that_has_multiple_records_for_first_institute
	analyzer.mark_notable_institute_assignment_records()
	df = analyzer.cm_history_cleaned
	assert(len(df.ix[(df.pid==1) & (df.is_first_institute)].index)==1)

def test_percent_active_by_week(tpt_analyzer_with_count_active_by_week):
	analyzer = tpt_analyzer_with_count_active_by_week
	analyzer.compute_percent_active_by_week()
	df = analyzer.percent_active_by_week
	assert(df.loc[('Atlanta',0),'value']==1)
	assert(df.loc[('Atlanta',1),'value']==0.75)
	assert(df.loc[('Atlanta',2),'value']==0.5)

def test_create_formatted_table(tpt_analyzer_with_computations):
	analyzer = tpt_analyzer_with_computations
	analyzer.create_formatted_table()
	print(analyzer.formated_retention_table)
	df = analyzer.formated_retention_table
	print("df columns are " + str(df.columns))
	assert(df.loc[('Atlanta',1,'active_percent'),[0,1]].loc['value',1]==0.5)
	assert(df.loc[('Atlanta',3,'RESIGNED'),[0,1]].loc['value',1]==1)

def test_filter_out_no_shows(tpt_analyzer_with_no_show_input):
	analyzer = tpt_analyzer_with_no_show_input
	assert(len(analyzer.exit_data_cleaned.ix[analyzer.exit_data_cleaned.release_code=='NOSHOW'].index)==0)

def test_filter_out_deferred(tpt_analyzer_with_deferred_input):
	analyzer = tpt_analyzer_with_deferred_input
	assert(len(analyzer.exit_data_cleaned.ix[analyzer.exit_data_cleaned.release_code=='DEFERRED'].index)==0)

def test_cms_not_in_exit_code_removed_from_history(tpt_analyzer_with_no_show_input):
	analyzer = tpt_analyzer_with_no_show_input
	assert(set(analyzer.exit_data_cleaned.pid.unique())==set(analyzer.cm_history_cleaned.pid.unique()))

def test_remove_cms_from_history_without_step(tpt_analyzer_with_history_without_step):
	analyzer = tpt_analyzer_with_history_without_step
	assert(analyzer.cm_history_cleaned.step.isnull().sum()==0)

def test_change_history_start_week_where_cm_appears_active(tpt_analyzer_with_cms_who_started_early):
	analyzer = tpt_analyzer_with_cms_who_started_early
	df = analyzer.cm_history_cleaned.set_index('history_id')
	assert(df.index.isin([0]).sum()==0)
	assert(df.loc[1,'week']==1)

def test_change_history_start_week_where_cm_later_resigned(tpt_analyzer_with_cms_who_started_early):
	analyzer = tpt_analyzer_with_cms_who_started_early
	df = analyzer.cm_history_cleaned.set_index('history_id')
	assert(df.loc[2,'week']==1)

def test_cm_no_show_doesnt_show(tpt_analyzer_with_cms_who_started_early):
	analyzer = tpt_analyzer_with_cms_who_started_early
	df = analyzer.cm_history_cleaned.set_index('pid')
	assert(df.index.isin([2]).sum()==0)

def test_cm_who_went_to_institute_last_year_wont_show_up(tpt_analyzer_with_cm_who_went_to_institute_last_year):
	analyzer = tpt_analyzer_with_cm_who_went_to_institute_last_year
	df = analyzer.cm_history_cleaned.set_index('pid')
	assert(df.index.isin([0]).sum()==0)

def test_count_active_by_week_national(tpt_analyzer_with_active_cm_by_week):
	analyzer = tpt_analyzer_with_active_cm_by_week
	analyzer.count_active_cms_by_week()
	df = analyzer.count_of_active_cms_by_week
	assert(df.loc[('National',0),'count']==2)
	assert(df.loc[('National',3),'count']==3)
	assert(df.loc[('National',5),'count']==1)

def test_cm_departure_list(tpt_analyzer_with_sample_data_for_list):
	analyzer = tpt_analyzer_with_sample_data_for_list
	analyzer.count_by_release_code()
	df = analyzer.list_of_exited_cms
	assert( set(df.columns) >= set(['pid','first_name','last_name','institute','release_date','release_code','week']))
	assert(len(df.index)==1)

def test_cm_transfer_out_list(tpt_analyzer_with_sample_data_for_list):
	analyzer = tpt_analyzer_with_sample_data_for_list
	analyzer.count_transfers()
	df = analyzer.list_of_transfer_cms
	assert( set(df.columns) >= set(['pid','first_name','last_name','institute','week','transfer_type']))
	assert(len(df.index)==2)
	assert(len(df.ix[(df.pid==1)&(df.transfer_type=='transfer_out')].index)==1)
	assert(len(df.ix[(df.pid==1)&(df.transfer_type=='transfer_in')].index)==1)

def test_cm_week_0_list(tpt_analyzer_with_sample_data_for_list):
	analyzer = tpt_analyzer_with_sample_data_for_list
	analyzer.compute_percent_active_by_week()
	df = analyzer.list_of_week_0_cms.set_index(['pid'])
	assert( set(df.columns) >= set(['first_name','last_name','institute']))
	assert( df.loc[1,'institute']=='Atlanta')
	assert( df.loc[2,'institute']=='Chicago')