import pandas as pd
class TPTRetention(object):
	"""docstring for TPTRetention"""
	def __init__(self, **kwargs):
		pass

	def count_by_release_code(self):
		assert hasattr(self,'exit_data_cleaned')
		assert set(self.exit_data_cleaned.columns) >= set(['institute','week','release_code','pid'])
		self.release_code_count = pd.DataFrame(self.exit_data_cleaned.groupby(['institute','week','release_code']).count().rename(columns={'pid':'count'})['count'])
		return self

	def fill_extra_weeks(self, df):
		assert set(df.columns) >= set(['institute','week','release_code','pid'])
		week = pd.DataFrame({'common':[1 for x in range(5)],'week':[x + 1 for x in range(5)]})
		cm_df = pd.DataFrame({'pid':df.pid,'common':[1 for x in range(len(df.index))]})
		df2 = pd.merge(week,cm_df)
		del df2['common']

		return df2

	def mark_notable_institute_assignment_records(self):
		assert hasattr(self,'cm_history_cleaned')
		assert set(self.cm_history_cleaned.columns) >= set(['institute','week','history_id','pid'])
		self.cm_history_cleaned['is_notable_institute_record'] = False
		self.cm_history_cleaned['is_transfer_in'] = False
		self.cm_history_cleaned['is_transfer_out'] = False
		df = self.cm_history_cleaned.set_index(['pid','history_id'])
		previous_index = None
		previous_institute = None
		previous_pid = None
		for i in df.index:
			current_institute = df.loc[i,'institute']
			current_pid, current_hist_id = i

			#Check whether we're looking at a new cm, reset institute
			if previous_pid is not None and current_pid != previous_pid:
				previous_institute = None
			if previous_institute is not None and current_institute != previous_institute:
				df.at[previous_index,'is_notable_institute_record'] = True
				df.at[previous_index,'is_transfer_out'] = True
				df.at[i,'is_notable_institute_record'] = True
				df.at[i,'is_transfer_in'] = True
			previous_index = i
			previous_institute = current_institute
			previous_pid = current_pid
		self.cm_history_cleaned = df.reset_index()

	def count_transfers(self):
		assert hasattr(self,'cm_history_cleaned')
		if 'is_transfer_in' not in self.cm_history_cleaned:
			self.mark_notable_institute_assignment_records()
		self.transfer_in_count_by_institute_week = pd.DataFrame({'count':self.cm_history_cleaned.ix[self.cm_history_cleaned.is_transfer_in].groupby(['institute','week']).size()})
		self.transfer_out_count_by_institute_week = pd.DataFrame({'count':self.cm_history_cleaned.ix[self.cm_history_cleaned.is_transfer_out].groupby(['institute','week']).size()})
		return self