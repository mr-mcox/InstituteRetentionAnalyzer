import pandas as pd
from InstituteRetentionAnalyzer.analyzer.filter import *

def test_filter_for_started():
		df = pd.DataFrame({
					'pid'  : [1,2],
					'week' : [0,1]
					})
		result = filter_for_started(df)
		assert((result.week > 0).all())

def test_filter_for_started_or_active():
		df = pd.DataFrame({
					'pid'  : [1,2],
					'week' : [0,None]
					})
		result = filter_for_started(df)
		assert len(result.index) == 1
		assert ( (result.week > 0) |  result.week.isnull() ).all()