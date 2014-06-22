import pandas as pd
from InstituteRetentionAnalyzer.munging.reformat_bobj import rename_bobj_columns
from InstituteRetentionAnalyzer.munging.cmpp_file import rename_cmpp_columns
from InstituteRetentionAnalyzer.analyzer.analyzer_for_tpt import TPTRetention

exit_data_cleaned       = rename_bobj_columns(pd.read_excel('institute_retention_and_transfers.xlsx','release_status'))
cm_history_cleaned      = rename_bobj_columns(pd.read_excel('institute_retention_and_transfers.xlsx','multiple_institutes'))
cmpp_data_cleaned       = rename_cmpp_columns(pd.read_excel('cm.master.tracker.xlsx','Total'))
institute_start_date_df = pd.read_excel('institute_start_date.xlsx',0)

analyzer = TPTRetention(
		exit_data_cleaned = exit_data_cleaned,
		cm_history_cleaned      = cm_history_cleaned,
		cmpp_data_cleaned       = cmpp_data_cleaned,
		institute_start_date_df = institute_start_date_df
	)

# analyzer.count_transfers()
# analyzer.count_by_release_code()
# analyzer.count_active_cms_by_week()

# analyzer.count_of_active_cms_by_week.to_csv('count_active_by_week.csv')
# analyzer.release_code_count_by_institute_week.to_csv('count_exit_by_week.csv')
# analyzer.transfer_in_count_by_institute_week.to_csv('count_transfer_in_by_week.csv')
# analyzer.transfer_out_count_by_institute_week.to_csv('count_transfer_out_by_week.csv')

analyzer.create_formatted_table()
analyzer.formated_retention_table.to_csv('formatted_retention_table.csv')