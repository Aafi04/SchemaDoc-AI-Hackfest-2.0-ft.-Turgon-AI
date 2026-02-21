-- Application Query Logs
SELECT val_x FROM legacy_metrics WHERE val_x > 0.9; -- for monitoring CPU Load
SELECT * FROM legacy_metrics WHERE flag_y = 1; -- just to check if system is deprecated or not
