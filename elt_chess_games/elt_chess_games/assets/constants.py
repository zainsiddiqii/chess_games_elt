from datetime import datetime

GCS_FILE_PATH_TEMPLATE = 'chess_games/{}_{}.ndjson'
START_DATE = '2020-12-01'
END_DATE = datetime.now().strftime('%Y-%m-%d')