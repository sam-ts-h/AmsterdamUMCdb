#train test split on person_id a patient can have more extubations so dont crossover pleaseplease
import os
import pandas as pd
from google.cloud import bigquery


onlyFirstExtubation = True
failureHours = 168
minAge = 18 #Cant change as its recorded in cohorts inthe db
#episodes shorter are left out
minVentilationHours = 24
#tube off shorter than this is same episode
mergeGapHours = 1
#no-tube record must come within this many hours after last tube record otherwise not extubation
extubationGapHours = 4

#login terminal commadns
#brew install --cask google-cloud-sdk   # skip if already installedd
#gcloud auth application-default login
#gcloud auth application-default set-quota-project liquid-folio-513114-d9

projectId = "liquid-folio-513114-d9"
datasetId = "amsterdamumcdb.version1_5_0"
location = "eu"

os.environ["GOOGLE_CLOUD_PROJECT"] = projectId

#default dataset
#fail above 20gb to be sure and not burn everythin
jobConfig = bigquery.QueryJobConfig(default_dataset=datasetId, maximum_bytes_billed=20*1024**3)
client = bigquery.Client(project=projectId, location=location, default_query_job_config=jobConfig)

def getCohort():
    #Foound ventilation mode in measurements it shows what mode of ventilation is done
    ventilationModeConceptId = 3004921

    #values of ventilatie mode (set) - hope this si correct but maybe ask prof? Or in PP
    invasiveModes = ["PS/CPAP", "PC", "PC (No trig)", "PS/CPAP (trig)", "VC", "NAVA", "SIMV(PC)+PS", "SIMV(VC)+PS", "Bi Vente", "VC (No trig)", "VC (trig)", "PRVC (No trig)", "PRVC", "VS", "PRVC (trig)"]

    #admissions with oxygen through a tracheostoma or a speaking cannula/valve <- maybe exclude as easier lets say in PP very clear so prof can see if correct
    tracheostomySql = """
    SELECT DISTINCT visit_occurrence_id FROM observation
    WHERE provider_id IS NOT NULL AND observation_source_value = 'Toedieningsweg' AND TRIM(value_source_value) IN ('Trach.stoma', 'Spreekcanule', 'Spreekklepje')
    """

    #NEW now we do current group invasive ventilation no tracheostomy no cardiac surgery no planned surgery
    # (see above table cardiac mostly planned others have few planned so a bit of a bummer but cant delete those)
    #admissions with a tube in device_exposure
    ventilatedSql = f"""
    SELECT DISTINCT visit_occurrence_id, person_id
    FROM device_exposure
    WHERE device_source_value = 'Tube'
    AND visit_occurrence_id NOT IN (SELECT visit_occurrence_id FROM ({tracheostomySql}) WHERE visit_occurrence_id IS NOT NULL)
    AND visit_occurrence_id NOT IN (
    SELECT visit_occurrence_id FROM visit_occurrence
    WHERE provider_id = 1 -- cardiochirurgie
    )
    AND visit_occurrence_id NOT IN (
    SELECT visit_occurrence_id FROM observation
    WHERE provider_id IS NOT NULL
    AND observation_concept_id = 37154585
    AND observation_source_value = 'NICE Opname type'
    AND TRIM(value_source_value) = 'Geplande chirurgie'
    AND visit_occurrence_id IS NOT NULL
    )
    """

    #tube start and end of our group
    tubeRecordsSql = f"""
    WITH ventilated AS ({ventilatedSql})
    SELECT device_exposure.person_id, device_exposure.visit_occurrence_id,
    device_exposure.device_exposure_start_datetime AS startTime, device_exposure.device_exposure_end_datetime AS endTime
    FROM device_exposure
    JOIN ventilated ON ventilated.visit_occurrence_id = device_exposure.visit_occurrence_id
    WHERE device_exposure.device_source_value = 'Tube'
    ORDER BY device_exposure.person_id, startTime
    """
    tubeRecords = client.query(tubeRecordsSql).to_dataframe()

    #oxygen route records of our group mostly used later and more often maybe pp
    oxygenRecordsSql = f"""
    WITH ventilated AS ({ventilatedSql})
    SELECT observation.person_id, observation.visit_occurrence_id, observation.observation_datetime, TRIM(observation.value_source_value) AS route
    FROM observation
    JOIN ventilated ON ventilated.visit_occurrence_id = observation.visit_occurrence_id
    WHERE observation.provider_id IS NOT NULL
    AND observation.observation_source_value = 'Toedieningsweg'
    """
    oxygenRecords = client.query(oxygenRecordsSql).to_dataframe()

    #death per patient in our group
    deathsSql = f"""
    WITH ventilated AS ({ventilatedSql})
    SELECT DISTINCT death.person_id, death.death_datetime
    FROM death
    JOIN ventilated ON ventilated.person_id = death.person_id
    """
    patientDeaths = client.query(deathsSql).to_dataframe()

    #beleid records with time, to know the policy at each extubation
    policyRecordsSql = f"""
    WITH ventilated AS ({ventilatedSql})
    SELECT observation.person_id, observation.observation_datetime AS policyTime, TRIM(observation.value_source_value) AS policy
    FROM observation
    JOIN ventilated ON ventilated.visit_occurrence_id = observation.visit_occurrence_id
    WHERE observation.provider_id IS NOT NULL AND observation.observation_concept_id = 1761496 AND observation.observation_source_value = 'Beleid'
    """
    policyRecords = client.query(policyRecordsSql).to_dataframe()

    #tube episodes within one admission, tube off shorter than mergeGapHours stays the same episode
    #!!!!Within 1 hour reintubation real? maybe ask?
    episodeList = []
    for row in tubeRecords.itertuples():
        sameAdmission = len(episodeList) > 0 and episodeList[-1]["visit_occurrence_id"] == row.visit_occurrence_id
        if sameAdmission and row.startTime - episodeList[-1]["endTime"] < pd.Timedelta(hours=mergeGapHours):
            episodeList[-1]["endTime"] = max(episodeList[-1]["endTime"], row.endTime)
        else:
            episodeList.append({
                "person_id": row.person_id,
                "visit_occurrence_id": row.visit_occurrence_id,
                "startTime": row.startTime,
                "endTime": row.endTime,
            })
    episodes = pd.DataFrame(episodeList)

    #per extubation the time until the patient is back on a tube (reintubation), if ever
    episodes["reintubationTime"] = episodes.groupby("person_id")["startTime"].shift(-1)

    #tube ventilator or oxygen through the tube (kunstneus/ waterset/ dl-tube) and noTube = oxygen without a tube
    noTubeRecords = oxygenRecords[~oxygenRecords["route"].isin(["Kunstneus", "Waterset", "DL-tube"])]
    noTubeRecords = noTubeRecords[["visit_occurrence_id", "observation_datetime"]].rename(columns={"observation_datetime": "noTubeTime"})
    noTubeRecords["visit_occurrence_id"] = noTubeRecords["visit_occurrence_id"].astype("int64")

    #first no-tube record after the tube ends in the same admission
    episodes = pd.merge_asof(episodes.sort_values("endTime"), noTubeRecords.sort_values("noTubeTime"), left_on="endTime", right_on="noTubeTime",
        by="visit_occurrence_id", direction="forward", tolerance=pd.Timedelta(hours=extubationGapHours))

    #extubation only if a no-tube record follows soon in the same admission, otherwise died/left icu intubated/unknown. and ventilated long enough
    extubated = episodes["noTubeTime"].notna()
    longEnough = episodes["endTime"] - episodes["startTime"] >= pd.Timedelta(hours=minVentilationHours)
    extubations = episodes[extubated & longEnough].rename(columns={"endTime": "extubationTime"})
    extubations["hoursToReintubation"] = (extubations["reintubationTime"] - extubations["extubationTime"]).dt.total_seconds() / 3600

    #time from extubation to death
    extubationOutcomes = extubations.merge(patientDeaths, on="person_id", how="left")
    extubationOutcomes["hoursToDeath"] = (extubationOutcomes["death_datetime"] - extubationOutcomes["extubationTime"]).dt.total_seconds() / 3600

    #policy at moment of extubation is last beleid record before
    policyRecords["person_id"] = policyRecords["person_id"].astype("int64")
    extubationOutcomes = extubationOutcomes.sort_values("extubationTime")
    policyRecords = policyRecords.sort_values("policyTime")
    extubationOutcomes = pd.merge_asof(extubationOutcomes, policyRecords, left_on="extubationTime", right_on="policyTime", by="person_id", direction="backward")
    extubationOutcomes["policy"] = extubationOutcomes["policy"].fillna("none")

    #Below table shows sadly we cant say if died without reintubation that it was paliative as group 3
    # does not have biggest share. (Also small groups as a lot has been fixed already due to above criteria)

    #comfort care at extubation leave out
    goldStandard = extubationOutcomes[extubationOutcomes["policy"] != "III"].copy()

    #failure defined as back on a tube or death within 7 days. 48h version as one paper does that maybe to look at sensitive cases more?
    goldStandard["failure"] = (goldStandard["hoursToReintubation"] <= failureHours) | (goldStandard["hoursToDeath"] <= failureHours)

    #attempt number within the admission 1 = first extubation etc I removed ones above 5 lets name it in PP were few records and seems unrealistic (or pat with tracheactomy as is easy to remove)
    goldStandard = goldStandard.sort_values(["visit_occurrence_id", "extubationTime"])
    goldStandard["attemptNumber"] = goldStandard.groupby("visit_occurrence_id").cumcount() + 1

    #patients with 5 or more extubations one admission left out notd realistic weaning course I think PP
    goldStandard = goldStandard[~goldStandard["person_id"].isin(
        goldStandard[goldStandard["attemptNumber"] >= 5]["person_id"])]

    if onlyFirstExtubation:
        goldStandard = goldStandard[goldStandard["attemptNumber"] == 1]
        
    #only what model needs rest is outcome info so might  leak into model
    return goldStandard[["person_id", "visit_occurrence_id", "startTime", "extubationTime", "attemptNumber", "failure"]]

#per extubation per variable how many records
#variables dict you send before{"lactate": [3047181, 3014111]}
def getCoverage(goldStandard, variables, hoursBefore=24):
    #all concept ids of all variables in one list for the sql
    conceptIdList = []
    for ids in variables.values():
        for conceptId in ids:
            conceptIdList.append(str(conceptId))
    conceptIds = ", ".join(conceptIdList)
    cohortRowList = []
    for row in goldStandard.itertuples():
        cohortRowList.append(f"STRUCT({row.visit_occurrence_id} AS visitId, {row.attemptNumber} AS attemptNumber, TIMESTAMP '{row.extubationTime.isoformat()}' AS extubationTime)")
    cohortRows = ", ".join(cohortRowList)

    #records without a value left out
    coverageSql = f"""
    WITH cohort AS (SELECT * FROM UNNEST([{cohortRows}])),
    records AS (
      SELECT visit_occurrence_id, measurement_concept_id AS conceptId, measurement_datetime AS startTime, measurement_datetime AS endTime
      FROM measurement
      WHERE provider_id IS NOT NULL AND measurement_concept_id IN ({conceptIds})
      AND (value_as_number IS NOT NULL OR value_as_concept_id > 0 OR value_source_value IS NOT NULL)
      UNION ALL
      SELECT visit_occurrence_id, observation_concept_id, observation_datetime, observation_datetime
      FROM observation
      WHERE provider_id IS NOT NULL AND observation_concept_id IN ({conceptIds})
      AND (value_as_number IS NOT NULL OR value_as_concept_id > 0 OR value_as_string IS NOT NULL OR value_source_value IS NOT NULL)
      UNION ALL
      SELECT visit_occurrence_id, condition_concept_id, condition_start_datetime, condition_end_datetime
      FROM condition_occurrence
      WHERE provider_id IS NOT NULL AND condition_concept_id IN ({conceptIds})
      UNION ALL
      SELECT visit_occurrence_id, drug_concept_id, drug_exposure_start_datetime, drug_exposure_end_datetime
      FROM drug_exposure
      WHERE provider_id IS NOT NULL AND drug_concept_id IN ({conceptIds})
      UNION ALL
      SELECT visit_occurrence_id, procedure_concept_id, procedure_datetime, procedure_datetime
      FROM procedure_occurrence
      WHERE provider_id IS NOT NULL AND procedure_concept_id IN ({conceptIds})
    )
    SELECT cohort.visitId AS visit_occurrence_id, cohort.attemptNumber, records.conceptId, COUNT(*) AS records
    FROM cohort
    JOIN records ON records.visit_occurrence_id = cohort.visitId
    AND records.startTime <= cohort.extubationTime
    AND (records.endTime IS NULL OR records.endTime >= TIMESTAMP_SUB(cohort.extubationTime, INTERVAL {hoursBefore} HOUR))
    GROUP BY visit_occurrence_id, attemptNumber, conceptId
    """
    counts = client.query(coverageSql).to_dataframe()

    #one column per variable
    coverage = goldStandard[["person_id", "visit_occurrence_id", "attemptNumber"]]
    for name, ids in variables.items():
        variableCounts = counts[counts["conceptId"].isin(ids)].groupby(["visit_occurrence_id", "attemptNumber"])["records"].sum().rename(name)
        coverage = coverage.merge(variableCounts, on=["visit_occurrence_id", "attemptNumber"], how="left")
        coverage[name] = coverage[name].fillna(0).astype(int)
    return coverage
