# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import pandas as pd
import geopandas as gp
import time

# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ############################################################################################################# #

# Using list comprehension, create list of all .csv files in working directory
csv_list = [x for x in os.listdir() if x.endswith(".csv")]

# All dataframes here have identical column names and thus can be easily concatenated
master_df = pd.concat([pd.read_csv(i, sep=";") for i in csv_list], ignore_index=True)
df_no_dupes = master_df.drop_duplicates("BSN")

# Summarize total schools and schools of each type by PLZ
schools_summary = pd.DataFrame(df_no_dupes.groupby("PLZ").size()).rename(columns={0: "Anzahl"})
schools_by_type = pd.DataFrame(df_no_dupes.groupby(["PLZ", "Schultyp"]).size()).rename(columns={0: "Anzahl"})

# Turn index into column
schools_summary.reset_index(inplace=True)
schools_by_type.reset_index(inplace=True)
schools_summary = schools_summary.astype({'PLZ': 'int16'})  # Dtype set as int16 for later merge compatibility

# Identify PLZ codes with the least and most schools
# idxmin() and idxmax() find only the first occurrence, the below syntax finds all
minmax_schools = schools_summary['Anzahl'].agg(['min', 'max'])
plz_min = schools_summary[schools_summary['Anzahl'] == minmax_schools[0]]['PLZ'].to_numpy()
plz_max = schools_summary[schools_summary['Anzahl'] == minmax_schools[1]]['PLZ'].to_numpy()

print(f"The most schools ({minmax_schools[1]}) are located in ZIP code(s) {plz_max}")
print(f"The fewest schools ({minmax_schools[0]}) are located in ZIP code(s) {plz_min}")
print("--------------------------------------------------------")

# Show schools summarised by type and ZIP code
print(schools_by_type)

# Read shapefile with geopandas, merge with schools summary
# Name and type change necessary for merge compatibility
bezirke = gp.read_file("plz.shp").rename(columns={'plz': 'PLZ'}).astype({'PLZ': 'int16'})
plz_join = bezirke.merge(schools_summary, on='PLZ', how='left')

# Write all output files into an output directory
if "Output" not in os.listdir():
    os.mkdir("Output")
    df_no_dupes.to_csv(path_or_buf='Output/alle_schulen.csv', sep=";", index=False)
    schools_summary.to_csv(path_or_buf='Output/Schulen_Zusammenfassung.csv', sep=";", index=False)
    plz_join.to_file("Output/Schulen_nach_PLZ.shp")

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")
