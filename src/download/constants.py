#---------- COVID ---------------------------------------
COVID_BASE_URL = "https://onemocneni-aktualne.mzcr.cz/"
COVID_API = "api/v2/covid-19/"
COVID_URL = COVID_BASE_URL + COVID_API
#---------- COVID ---------------------------------------

#---------- Citizen --------------------------------------z
CITIZEN_URL = "https://www.czso.cz/csu/czso/obyvatelstvo-podle-petiletych-vekovych-skupin-a-pohlavi-v-krajich-a-okresech"
CITIZEN_FILE_NAME = "citizen.csv"

#---------- Citizen --------------------------------------

# ------------------- COVID string constants in metadata-----------
EPIDEMIC_STATS = "Epidemiologické charakteristiky"
TESTING = "Testování"
VACCINATION = "Očkování"
OTHER = "Různé"
# OTHER is not supported anymore OTHER
STATS = [EPIDEMIC_STATS,TESTING,VACCINATION]
# ------------------- COVID string constants in metadata----------
