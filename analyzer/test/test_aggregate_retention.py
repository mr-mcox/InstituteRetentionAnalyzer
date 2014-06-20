from InstituteRetentionAnalyzer.analyzer.aggregate_retention import *
import pandas as pd

def test_exit_by_institute_and_week():
		df = pd.DataFrame({
					'pid'  : [1,2,3],
					'week' : [1,2,2],
					'institute': ['Chicago','Atlanta','Atlanta'],
					'release_code' : ['RESIGNED','RESIGNED','RESIGNED',]
					})
		result = count_by_release_code(df)
		assert(result.loc[('Chicago',1,'RESIGNED'),'count']==1)
		assert(result.loc[('Atlanta',2,'RESIGNED'),'count']==2)

def test_count_week_zero():
		df = pd.DataFrame({
				'pid'  : [1,2,3],
				'week' : [1,2,2],
				'institute': ['Chicago','Atlanta','Atlanta'],
				'release_code' : ['RESIGNED','RESIGNED','RESIGNED',]
				})
		result = count_week_zero(df)
		assert(result.loc['Chicago','count']==1)
		assert(result.loc['Atlanta','count']==2)

def test_fill_extra_weeks():
		df = pd.DataFrame({
			'pid'  : [1,2,3],
			'week' : [None,1,2],
			'institute': ['Atlanta','Atlanta','Atlanta'],
			'release_code' : [None,'RESIGNED','RESIGNED',]
			})
		result = fill_extra_weeks(df)
		assert(len(result.ix[(result.pid == 1) & (result.week ==1)].index)>=1)
		assert(len(result.ix[(result.pid == 2) & (result.week ==1)].index)>=1)
