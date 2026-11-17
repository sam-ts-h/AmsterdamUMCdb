import pandas as pd
from cohort import client, getCohort
#window before extube for measurements
hoursBefore = 24
#admission time (very long)
admissionHours = 24 * 365

cardiac_variables = {
    "heart_rate": [3027018, 21490872],
    "invasive_sbp": [21490853],
    "invasive_dbp": [21490851],
    "atrial_fibrilation": [313217],
    "cvp": [21490675],
    "lactate": [3047181, 3014111],
    #"transthoracic_echocardiography": [4335825], #gaat om een procedure, niet interessant
    "acute_heart_failure": [4023479],
    "cardiogenic_shock": [198571],
    "ecg_rhythm_abnormality": [4064612, 4065290, 4064458],
    "glucose": [3020491],
    "hemoglobin": [40762351],
    "ck_mb": [3005785],
    "tropine": [3019800, 3048529],
    "potassium": [3023103, 3005456],
    "urea": [43534077],
    "creatinine": [3020564]
}

neurological_variables = {
    "gcs_motor": [3008223],
    "gcs_verbal": [3009094],
    "gcs_eye": [3016335],
    "rass": [36684829],
    "eye_pupillary ": [21491763, 21490963],
    "eye_diameter ": [3026611, 3010321],
    "epileptic_seizure": [4197485],
    "temperature": [21490588, 21490870, 21490586, 3022060,3025163,3025085]
}
demographic_variables = {
    "male": [8507],
    "female": [8532],
    "european": [38003614],
    "african": [38003615],
    "nepalese": [38003595],
    "japanese": [38003584],
    "chinese": [38003579],
    "weight ": [1029318],
    #comorbidity (chronic):
    #ids from feature engineering notebook
    "kidney ": [198124, 37018761],
    "cardiovascular ": [134057, 4028244, 319835, 321588, 321319],
    "artial_fibrilation ": [313217, 4141360],
    "diabetes1 ": [201254],
    "hypertension ": [316866],

}
demographic_columns = {
    "age": {"table": "person", "column": "year_of_birth", "type": "derived"},
}

# SEPSIS / SYSTEMIC INFECTION
sepsis_variables = {
    'sepsis_diagnosis': [132797],
    #from feature engineering notebook, answers Ja Nee Onbekend
    'suspected_sepsis': [44808681],
            #temp Oesophagus, Blaas, Bloed, Rectaal, oraal, oor, axillair
    #oraal 3006322 left out as in feature engineering notebook
    'temperature': [21490588, 21490870, 21490586, 3022060,3025163,3025085],
            #Leuco's (bloed), Leucocyten zelfde concept-id
    'leukocytes': [3010813],
            #lactaat (bloed), Lactaat, laktaat Astrup
    'lactate': [3047181, 3014111],
    #trombocyten (platelets) Thrombo's (bloed), Thrombocyten
    'platelets': [3007461],
    #ik gebruik totaal bilirubine, Bilirubine (bloed), Bili Totaal
    'bilirubin': [3006140, 40757494],
        #Kreatinine (bloed), KREAT enzym. (bloed), Kreatinine
    'creatinine': [3020564],
    #MAP (Mean Arterial Pressure), let op invasieve bloeddruk metingen ABP!!!!
    'map': [21490852],
    #medication
    'vasoactive_support': [2907531, 40072394,40074086,21088391,36411287,19076867, 40038600],
    'blood_culture': [4107893],
    'antibiotics': [43295826,36881808, 40928582,21088706, 40737711,40077149,40731671],
}

# PULMONARY DISEASE
pulmonary_variables = {
    'pneumonia': [
        255848,   # Pneumonia
        4309106,  # Aspiration pneumonia
        257315,   # Bacterial pneumonia
        4049965,  # Fungal pneumonia
        261326,   # Viral pneumonia
        4190647,  # Pneumocystosis pneumonia
    ],
    'copd': [257004],
    'pao2': [3027315], #deze nog checken of het echt arteriele bloedgassen zijn
    'fio2': [3024882], #zuurstoffractie op fentilator

    'respiratory_rate': [3024171,  # Monitor
        3007646,  # Ventilator totaal
        ],
    "respiratory_rate_spontaneous": [3026892],
    #Uitgeademde teugvolume ; VTe,  # Expired tidal volume
    "tidal_volume": [21490789, 3015016,  ],
    # Gemeten ingeademd teugvolume
    "tidal_volume_inspired": [3016166],
    "tidal_volume_set": [3012410], #Het ingestelde teugvolume

    # Indirecte indicator: hoe vaak worden de luchtwegen uitgezogen?
    "airway_suctioning": [4239191, 4043669, 4336460],
    "secretions": [4089228], #Hoeveelheid Sputum, let op dat is source code: 8894, want kleur heeft zelde concept id
    "sputum_appearance": [4080582], #de structuur van het slijm


    'mechanical_ventilation': [3004921],
    # RSBI = respiratory_rate / tidal_volume_in_liters (later berekenen)
    # PaO2/FiO2 = pao2 / fio2_fraction (later berekenen)
    # ventilation_duration = tijd tussen begin invasieve beademing en predictietijdstip
}

#table per var:
measurementVariables = [
    "heart_rate", "invasive_sbp", "invasive_dbp", "cvp", "lactate", "glucose", "hemoglobin", "ck_mb", "tropine", "potassium", "urea", "creatinine",
    "gcs_motor", "gcs_verbal", "gcs_eye", "rass", "eye_pupillary ", "eye_diameter ", "temperature",
    "leukocytes", "platelets", "bilirubin", "map",
    "pao2", "fio2", "respiratory_rate", "respiratory_rate_spontaneous", "tidal_volume", "tidal_volume_inspired", "tidal_volume_set", "sputum_appearance", "mechanical_ventilation",
]
observationVariables = [
    "secretions", "suspected_sepsis",
]
conditionVariables = [
    "atrial_fibrilation", "acute_heart_failure", "cardiogenic_shock",
    "epileptic_seizure",
    "sepsis_diagnosis",
    "pneumonia", "copd",
    "kidney ", "cardiovascular ", "artial_fibrilation ", "diabetes1 ", "hypertension ",
]
drugVariables = [
    "vasoactive_support", "antibiotics",
]
procedureVariables = [
    "airway_suctioning",
]
personVariables = [
    "male", "female", "european", "african", "nepalese", "japanese", "chinese",
]
allVariables = {**cardiac_variables, **neurological_variables, **demographic_variables, **sepsis_variables, **pulmonary_variables}

#feature engineering notebook mapping answers to id with meaning
answerNumbers = {
    "gcs_motor": {
        45880468: 6,
        45880467: 5,
        45882047: 4,
        45879885: 3,
        45878993: 2,
        45878992: 1,
    },
    "gcs_verbal": {
        45877602: 5,
        45883906: 4,
        45877601: 3,
        45883352: 2,
        45877384: 1,
    },
    "gcs_eye": {
        45880466: 4,
        45876254: 3,
        45880465: 3,
        45884209: 2,
        45883351: 2,
        45877537: 1,
    },
    "rass": {
        45880051: -5,
        45879434: -4,
        1990543: -3,
        46237183: -2,
        45877871: -1,
        45884808: 0,
        45881739: 1,
        46237198: 2,
        45877463: 4,
    },
    "eye_pupillary ": {
        21498502: 1,
        21498863: 0,
    },
    "eye_diameter ": {
        45881054: 1,
        45884805: 2,
        45880155: 3,
        45877193: 4,
        45883038: 5,
        45883904: 6,
        45877461: 7,
        45884806: 8,
    },
    "secretions": {
        "Geen": 0,
        "Gering": 1,
        "Normaal": 2,
        "Ruim": 3,
        "Veel": 4,
    },
    "sputum_appearance": {
        "Waterig": 0,
        "Kleverig": 1,
        "Taai": 2,
    },
    #onbekend stays empty
    "suspected_sepsis": {
        "Ja": 1,
        "Nee": 0,
    },
}

# answer text to category
answerCategories = {
    "mechanical_ventilation": {
        "PC": "controlled",
        "PC (No trig)": "controlled",
        "VC": "controlled",
        "VC (No trig)": "controlled",
        "VC (trig)": "controlled",
        "PRVC": "controlled",
        "PRVC (No trig)": "controlled",
        "PRVC (trig)": "controlled",
        "SIMV(PC)+PS": "controlled",
        "SIMV(VC)+PS": "controlled",
        "Bi Vente": "controlled",
        "PS/CPAP": "support",
        "PS/CPAP (trig)": "support",
        "NAVA": "support",
        "VS": "support",
    },
    "secretions": {
        "Wit": "wit",
        "Geel": "geel",
        "Groen": "groen",
        "Purulent": "purulent",
    },
}

#feature engineering notebook ranges
validRanges = {
    "respiratory_rate": {"low": 4, "high": 80},
    "tidal_volume": {"low": 50, "high": 2000},
    "tidal_volume_inspired": {"low": 50, "high": 2000},
    "fio2": {"low": 0.21, "high": 1},
    "pao2": {"low": 20, "high": 600},
    "temperature": {"low": 30, "high": 42},
    "leukocytes": {"low": 0.1, "high": 200},
    "lactate": {"low": 0.1, "high": 30},
    "platelets": {"low": 1, "high": 1500},
    "bilirubin": {"low": 1, "high": 1000},
    "creatinine": {"low": 5, "high": 2000},
    "map": {"low": 30, "high": 180},
    "invasive_sbp": {"low": 40, "high": 250},
    "invasive_dbp": {"low": 20, "high": 150},
    "glucose": {"low": 1.5, "high": 30},
    "hemoglobin": {"low": 2, "high": 15},
    "ck_mb": {"low": 0, "high": 100},
    "potassium": {"low": 1, "high": 8},
    "urea": {"low": 0.5, "high": 50},
}

#units per var
unitConversions = {
    "tidal_volume": {
        "ml": 1,
        "l": 1000,
    },
    "tidal_volume_inspired": {
        "ml": 1,
    },
    "pao2": {
        "mmhg": 1,
        "kpa": 7.50062,
    },
    "invasive_sbp": {
        "mmhg": 1,
    },
    "invasive_dbp": {
        "mmhg": 1,
    },
    "heart_rate": {
        "/min": 1,
    },
}

# feature engineering notebook source vars we keep
validSourceValues = {
    "heart_rate": ["IABP HF", "PiCCO HF Hartfrequentie", "Hartfrequentie"],
    "airway_suctioning": ["Aantal Bronchiaaltoilet"],
}

extubationKeys = ["visit_occurrence_id", "attemptNumber"]

def getRecords(goldStandard, names, hours):
    #concept ids per table
    tableIds = {}
    for table, tableVariables in [("measurement", measurementVariables), ("observation", observationVariables), ("condition_occurrence", conditionVariables), ("drug_exposure", drugVariables), ("procedure_occurrence", procedureVariables)]:
        idList = ["NULL"]
        for name in names:
            if name in tableVariables:
                for conceptId in allVariables[name]:
                    idList.append(str(conceptId))
        tableIds[table] = ", ".join(idList)
    cohortRowList = []
    for row in goldStandard.itertuples():
        cohortRowList.append(f"STRUCT({row.visit_occurrence_id} AS visitId, {row.attemptNumber} AS attemptNumber, TIMESTAMP '{row.extubationTime.isoformat()}' AS extubationTime)")
    cohortRows = ", ".join(cohortRowList)
    recordsSql = f"""
    WITH cohort AS (SELECT * FROM UNNEST([{cohortRows}])),
    records AS (
      SELECT visit_occurrence_id, measurement_concept_id AS conceptId, measurement_source_value AS sourceValue, measurement_datetime AS startTime, measurement_datetime AS endTime,
        value_as_number AS number, value_as_concept_id AS answer, TRIM(value_source_value) AS answerText, unit_source_value AS unit
      FROM measurement
      WHERE provider_id IS NOT NULL AND measurement_concept_id IN ({tableIds["measurement"]})
      UNION ALL
      SELECT visit_occurrence_id, observation_concept_id, observation_source_value, observation_datetime, observation_datetime,
        value_as_number, value_as_concept_id, TRIM(value_source_value), unit_source_value
      FROM observation
      WHERE provider_id IS NOT NULL AND observation_concept_id IN ({tableIds["observation"]})
      UNION ALL
      SELECT visit_occurrence_id, condition_concept_id, condition_source_value, COALESCE(condition_start_datetime, TIMESTAMP(condition_start_date)), condition_end_datetime,
        NULL, NULL, NULL, NULL
      FROM condition_occurrence
      WHERE provider_id IS NOT NULL AND condition_concept_id IN ({tableIds["condition_occurrence"]})
      UNION ALL
      SELECT visit_occurrence_id, drug_concept_id, drug_source_value, drug_exposure_start_datetime, drug_exposure_end_datetime,
        NULL, NULL, NULL, NULL
      FROM drug_exposure
      WHERE provider_id IS NULL AND drug_concept_id IN ({tableIds["drug_exposure"]})
      UNION ALL
      SELECT visit_occurrence_id, procedure_concept_id, procedure_source_value, procedure_datetime, procedure_datetime,
        quantity, NULL, NULL, NULL
      FROM procedure_occurrence
      WHERE provider_id IS NOT NULL AND procedure_concept_id IN ({tableIds["procedure_occurrence"]})
    )
    SELECT cohort.visitId AS visit_occurrence_id, cohort.attemptNumber, records.conceptId, records.sourceValue, records.startTime AS time,
      records.number, records.answer, records.answerText, records.unit
    FROM cohort
    JOIN records ON records.visit_occurrence_id = cohort.visitId
    AND records.startTime <= cohort.extubationTime
    AND (records.endTime IS NULL OR records.endTime >= TIMESTAMP_SUB(cohort.extubationTime, INTERVAL {hours} HOUR))
    """
    records = client.query(recordsSql).to_dataframe()
    #concept id to var name
    conceptNames = {}
    for name in names:
        for conceptId in allVariables[name]:
            conceptNames[conceptId] = name
    records["name"] = records["conceptId"].map(conceptNames)
    return records

def cleanRecords(records):
    records = records.copy()
    #fio2 is percentage so normal
    isFio2 = records["name"] == "fio2"
    records.loc[isFio2, "number"] = records.loc[isFio2, "number"] / 100
    for name, unitFactors in unitConversions.items():
        #other units out now
        isName = records["name"] == name
        knownUnit = records["unit"].str.lower().isin(unitFactors.keys())
        records = records[~isName | knownUnit].copy()
        isName = records["name"] == name
        factors = records.loc[isName, "unit"].str.lower().map(unitFactors)
        records.loc[isName, "number"] = records.loc[isName, "number"] * factors
    for name, validRange in validRanges.items():
        isName = records["name"] == name
        inRange = records["number"].between(validRange["low"], validRange["high"])
        records = records[~isName | inRange]
    for name, sourceValues in validSourceValues.items():
        isName = records["name"] == name
        knownSource = records["sourceValue"].isin(sourceValues)
        records = records[~isName | knownSource]
    return records

def getNumerical(records):
    numerical = records[extubationKeys].drop_duplicates()
    for name in records["name"].unique():
        nameRecords = records[records["name"] == name].sort_values("time")
        numbers = nameRecords.groupby(extubationKeys)["number"]
        aggregates = pd.DataFrame({
            f"{name}_last": numbers.last(),
            f"{name}_min": numbers.min(),
            f"{name}_max": numbers.max(),
            f"{name}_mean": numbers.mean(),
            f"{name}_count": numbers.count(),
            f"{name}_trend": numbers.last() - numbers.first(),
        })
        numerical = numerical.merge(aggregates.reset_index(), on=extubationKeys, how="left")
    return numerical

def getOrdinal(records):
    numberRecordList = []
    for name, answers in answerNumbers.items():
        nameRecords = records[records["name"] == name].copy()
        numberFromConcept = nameRecords["answer"].map(answers)
        numberFromText = nameRecords["answerText"].map(answers)
        nameRecords["number"] = numberFromConcept.fillna(numberFromText)
        numberRecordList.append(nameRecords)
    numberRecords = pd.concat(numberRecordList)
    numberRecords = numberRecords[numberRecords["number"].notna()]
    numberRecords["number"] = numberRecords["number"].astype(float)
    return getNumerical(numberRecords)

def getCategories(records):
    categories = records[extubationKeys].drop_duplicates()
    for name, answerGroups in answerCategories.items():
        nameRecords = records[records["name"] == name].sort_values("time")
        nameRecords["category"] = nameRecords["answerText"].map(answerGroups)
        nameRecords = nameRecords[nameRecords["category"].notna()].copy()
        aggregates = pd.DataFrame({
            f"{name}_last_category": nameRecords.groupby(extubationKeys)["category"].last(),
        })
        #share of records per cat
        for category in pd.unique(list(answerGroups.values())):
            nameRecords["isCategory"] = nameRecords["category"] == category
            aggregates[f"{name}_{category}_share"] = nameRecords.groupby(extubationKeys)["isCategory"].mean()
        categories = categories.merge(aggregates.reset_index(), on=extubationKeys, how="left")
        categories[f"{name}_last_category"] = categories[f"{name}_last_category"].astype("category")
    return categories

def getFlags(records):
    #1 if record
    flags = records[extubationKeys].drop_duplicates()
    for name in records["name"].unique():
        nameExtubations = records[records["name"] == name][extubationKeys].drop_duplicates()
        nameExtubations[name] = 1
        flags = flags.merge(nameExtubations, on=extubationKeys, how="left")
        flags[name] = flags[name].fillna(0).astype(int)
    return flags

def getExtraFeatures(features, records):
    #from feature engineering notebook::
    features["gcs_total"] = features["gcs_motor_last"] + features["gcs_verbal_last"] + features["gcs_eye_last"]
    comorbidityColumns = ["kidney ", "cardiovascular ", "artial_fibrilation ", "diabetes1 ", "hypertension "]
    features["comorbidity_count"] = features[comorbidityColumns].sum(axis=1)
    features["has_comorbidity"] = (features["comorbidity_count"] > 0).astype(int)
    #from comments in pulmonary_variables::
    features["rsbi"] = features["respiratory_rate_last"] / (features["tidal_volume_last"] / 1000)
    features["pf_ratio"] = features["pao2_last"] / features["fio2_last"]
    features["ventilation_hours"] = (features["extubationTime"] - features["startTime"]).dt.total_seconds() / 3600

    records = records.sort_values("time")
    suctioning = records[records["name"] == "airway_suctioning"]
    seizures = records[records["name"] == "epileptic_seizure"]
    modes = records[records["name"] == "mechanical_ventilation"]
    #pupils per side right /left have own concept id
    reactions = records[records["name"] == "eye_pupillary "].copy()
    reactions["number"] = reactions["answer"].map(answerNumbers["eye_pupillary "])
    sizes = records[records["name"] == "eye_diameter "].copy()
    sizes["number"] = sizes["answer"].map(answerNumbers["eye_diameter "])
    extra = pd.DataFrame({
        "airway_suctioning_sum": suctioning.groupby(extubationKeys)["number"].sum(),
        "epileptic_seizure_count": seizures.groupby(extubationKeys)["conceptId"].count(),
        "mechanical_ventilation_last_mode": modes.groupby(extubationKeys)["answerText"].last(),
        "pupil_right_reactive_last": reactions[reactions["conceptId"] == 21490963].groupby(extubationKeys)["number"].last(),
        "pupil_left_reactive_last": reactions[reactions["conceptId"] == 21491763].groupby(extubationKeys)["number"].last(),
        "pupil_right_size_last": sizes[sizes["conceptId"] == 3010321].groupby(extubationKeys)["number"].last(),
        "pupil_left_size_last": sizes[sizes["conceptId"] == 3026611].groupby(extubationKeys)["number"].last(),
    })
    #1 both reactive 0 one unreactive empty if unknown
    extra["pupil_both_reactive"] = float("nan")
    extra.loc[(extra["pupil_right_reactive_last"] == 1) & (extra["pupil_left_reactive_last"] == 1), "pupil_both_reactive"] = 1
    extra.loc[(extra["pupil_right_reactive_last"] == 0) | (extra["pupil_left_reactive_last"] == 0), "pupil_both_reactive"] = 0
    extra["pupil_any_unreactive"] = 1 - extra["pupil_both_reactive"]
    extra["pupil_size_mean"] = (extra["pupil_right_size_last"] + extra["pupil_left_size_last"]) / 2
    extra["pupil_size_difference"] = (extra["pupil_right_size_last"] - extra["pupil_left_size_last"]).abs()

    features = features.merge(extra.reset_index(), on=extubationKeys, how="left")
    features["epileptic_seizure_count"] = features["epileptic_seizure_count"].fillna(0).astype(int)
    features["mechanical_ventilation_last_mode"] = features["mechanical_ventilation_last_mode"].astype("category")
    return features

def getFeatures(goldStandard):
    #24h
    recentNames = measurementVariables + ["secretions"] + drugVariables + procedureVariables + ["atrial_fibrilation", "epileptic_seizure"]
    #anytime before extubation in the admission
    admissionNames = [
        "acute_heart_failure", "cardiogenic_shock",
        "sepsis_diagnosis", "suspected_sepsis",
        "pneumonia", "copd",
        "kidney ", "cardiovascular ", "artial_fibrilation ", "diabetes1 ", "hypertension ",
    ]
    recentRecords = cleanRecords(getRecords(goldStandard, recentNames, hoursBefore))
    admissionRecords = cleanRecords(getRecords(goldStandard, admissionNames, admissionHours))
    allRecords = pd.concat([recentRecords, admissionRecords])
    flagNames = conditionVariables + drugVariables
    isFlag = allRecords["name"].isin(flagNames)
    isOrdinal = allRecords["name"].isin(answerNumbers.keys())
    isCategory = allRecords["name"].isin(answerCategories.keys())
    numerical = getNumerical(allRecords[~isFlag & ~isOrdinal & ~isCategory])
    ordinal = getOrdinal(allRecords)
    categories = getCategories(allRecords)
    flags = getFlags(allRecords[isFlag])

    features = goldStandard.copy()
    for part in [numerical, ordinal, categories, flags]:
        features = features.merge(part, on=extubationKeys, how="left")
    #no record means no diagnosis or medication
    for name in flags.columns.drop(extubationKeys):
        features[name] = features[name].fillna(0).astype(int)
    #no record means 0 measurements
    for column in features.columns:
        if column.endswith("_count"):
            features[column] = features[column].fillna(0).astype(int)

    #gender ethnicity and age from person table
    personIdList = []
    for personId in goldStandard["person_id"].unique():
        personIdList.append(str(personId))
    personSql = f"""
    SELECT person_id, gender_concept_id, race_concept_id, year_of_birth FROM person WHERE person_id IN ({", ".join(personIdList)})
    """
    persons = client.query(personSql).to_dataframe()
    for name in personVariables:
        conceptId = allVariables[name][0]
        isConcept = (persons["gender_concept_id"] == conceptId) | (persons["race_concept_id"] == conceptId)
        persons[name] = isConcept.astype(int)
    features = features.merge(persons.drop(columns=["gender_concept_id", "race_concept_id"]), on="person_id", how="left")
    #age at extubation as in notebook
    features["age"] = features["extubationTime"].dt.year - features["year_of_birth"]
    features = features.drop(columns="year_of_birth")

    return getExtraFeatures(features, recentRecords)

modelGroups = {
    "cardiac": cardiac_variables,
    "neuro": neurological_variables,
    "sepsis": sepsis_variables,
    "pulmonary": pulmonary_variables,
}
#engineered so we need to add it explicitly to groups
extraGroups = {
    "neuro": ["gcs_total", "pupil_right_reactive_last", "pupil_left_reactive_last", "pupil_right_size_last", "pupil_left_size_last", "pupil_both_reactive", "pupil_any_unreactive", "pupil_size_mean", "pupil_size_difference"],
    "pulmonary": ["rsbi", "pf_ratio"],
    #no records in last 24h so as yes/no over the admission in every model
    "demographic": ["age", "comorbidity_count", "has_comorbidity", "ventilation_hours", "acute_heart_failure", "cardiogenic_shock"],
}

#cohort columns for everyone
cohortColumns = ["person_id", "visit_occurrence_id", "startTime", "extubationTime", "attemptNumber", "failure"]

def getGroupColumns(features):
    demographicColumns = list(extraGroups["demographic"])
    for column in features.columns:
        for name in demographic_variables:
            if column == name or column.startswith(name + "_"):
                demographicColumns.append(column)
                break
    groupColumns = {}
    for group, variables in modelGroups.items():
        columns = list(demographicColumns) + extraGroups.get(group, [])
        for column in features.columns:
            for name in variables:
                #tidal_volume_inspired_last starts with tidal_volume. only add once
                if column in columns:
                    break
                if column == name or column.startswith(name + "_"):
                    columns.append(column)
                    break
        groupColumns[group] = columns
    groupColumns["all"] = list(features.columns.drop(cohortColumns))
    return groupColumns
