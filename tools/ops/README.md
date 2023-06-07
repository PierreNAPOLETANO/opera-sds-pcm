# OPERA SDS PCM Tools

# Audit tool

The audit tools can be used to compare input products and output product quantities.
1. hls_audit.py - input: HLS, output: DSWx-HLS
2. slc_audit.py - input: SLC, outptus: CSLC_S1 and RTC_S1 

See `*audit.py --help`, documentation comments, and source code for more details.

## Getting Started

### Prerequisites

1. Git.
2. Python (see `.python-version`).
3. A clone of the `opera-sds-pcm` repo.

### Installation on local system

1. Create a python virtual environment.
    1. RECOMMENDED: move `pip.conf` into the resulting `venv/` directory.
2. Activate the virtual environment and install the script dependencies referenced in the imports section as needed.
    1. RECOMMENDED: install dependencies listed in the relevant section of `setup.py` using the following command `pip install '.[audit]'`

### Running locally 

1. Configure `.env` as needed.
1. Run `python *audit.py` from the same directory.


### Sample .env
```
ES_USER=<username>
ES_HOST=<mozart ip>
ES_BASE_URL=https://${ES_HOST}/grq_es/
```

### Installation on Mozart
1. `pip install python-dotenv`

### Running on Mozart
1. Configure `/export/home/hysdsops/mozart/ops/opera-pcm/tools/.env` as needed
2. Run `python /export/home/hysdsops/mozart/ops/opera-pcm/tools/ops/hls_audit.py` or
    `python /export/home/hysdsops/mozart/ops/opera-pcm/tools/ops/slc_audit.py`


### Sample commands on Mozart
```
$ cd ~/mozart/ops/opera-pcm/tools/ops
$ python hls_audit.py -h
$ python hls_audit.py --start-datetime 2023-06-01T00:00:00 --end-datetime 2023-06-06T23:59:59
```
### Sample outputs
```
$ python /export/home/hysdsops/mozart/ops/opera-pcm/tools/ops/hls_audit.py 
2023-06-07 19:43:08 WARNING root:hls_audit.py:              <module>: 29 - Setting password via dotenv is not recommended. Leave empty to be prompted to enter password.
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>: 80 - sys.argv=['/export/home/hysdsops/mozart/ops/opera-pcm/tools/ops/hls_audit.py']
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:110 - Data queried or downloaded (files): len(search_results)=14
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:118 - Data queried or downloaded (granules): len(queried_or_downloaded_granules)=2
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:132 - Data downloaded (files): len(search_results)=14
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:140 - Data downloaded (granules): len(downloaded_granules)=2
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:144 - Missing download (files): len(missing_download_files)=0
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:152 - Missing download (granules): len(missing_download_granules)=0
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:167 - Data ingested (L30): len(search_results)=0
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:176 - Data ingested (S30): len(search_results)=2
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:179 - Data ingested (total) (files): len(all_ingested_files)=14
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:186 - Data ingested (total) (granules): len(all_ingested_granules)=2
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:189 - Missing data ingest (files): len(missing_data_ingest_files)=0
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:197 - Missing data ingest (granules): len(missing_data_ingest_granules)=0
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:217 - Data produced by PGE(s) (DSWx): 2
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:219 - Data processed through PGE(s): 14
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:222 - Inputs Missing PGE: len(missing_pge_files)=0
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:230 - Inputs Missing PGE: len(missing_pge_granules)=0
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:250 - Inputs Missing successful CNM-S (files): len(missing_cnm_s_files)=0
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:252 - Inputs Missing successful CNM-S (granules): len(missing_cnm_s_granules)=0
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:263 - Inputs Missing successful CNM-R (files): len(missing_cnm_r_files)=14
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:265 - Inputs Missing successful CNM-R (granules): len(missing_cnm_r_granules)=2
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:277 - ALL Unpublished (files): len(all_unpublished_files)=14
2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:284 - pstr(all_unpublished_granules)={'HLS.S30.T57NVH.2022017T000429.v2.0', 'HLS.S30.T57NUH.2022017T000429.v2.0'}

2023-06-07 19:43:08    INFO root:hls_audit.py:              <module>:285 - ALL Unpublished (granules): len(all_unpublished_granules)=2
```

# CMR Audit tool

The CMR audit tool can be used to compare input products and output product IDs and quantities.
1. cmr_audit_hls.py - input: HLS (LP DAAC), output: DSWx-HLS (PO DAAC)
2. cmr_audit_slc.py - input: SLC (ASF DAAC), outptus: CSLC_S1 and RTC_S1 (ASF DAAC)

See `cmr_audit*.py --help`, documentation comments, and source code for more details.

## Getting Started

### Prerequisites

1. Git.
1. Python (see `.python-version`).
1. A clone of the `opera-sds-pcm` repo.

### Installation on local system

1. Create a python virtual environment.
    1. RECOMMENDED: move `pip.conf` into the resulting `venv/` directory.
2. Activate the virtual environment and install the script dependencies referenced in the imports section as needed.
    1. RECOMMENDED: install dependencies listed in the relevant section of `setup.py` using the following command `pip install '.[cmr_audit]'`

### Running locally

1. Run `python cmr_audit*.py` from the same directory.


### Installation on Mozart

Not required

### Running on Mozart
1. Execute sample commands below


### Sample commands on Mozart
```
$ cd ~/mozart/ops/opera-pcm/tools/ops/cmr_audit
$ python cmr_audit_hls.py -h
$ python cmr_audit_hls.py --start-datetime 2023-06-01T00:00:00 --end-datetime 2023-06-02T00:00:00 
$ python cmr_audit_hls.py --start-datetime 2023-06-01T00:00:00 --end-datetime 2023-06-02T00:00:00  --format txt
$ python cmr_audit_hls.py --start-datetime 2023-06-01T00:00:00 --end-datetime 2023-06-02T00:00:00  --output missing_granule.json --format json
```

# CNM Check tool

The CNM check tool outputs the CNM statuses for a given JSON list of HLS granules.

## Getting Started

### Prerequisites

1. Git.
1. Python (see `.python-version`).
1. A clone of the `opera-sds-pcm` repo.

### Installation on local system

1. Create a python virtual environment.
    1. RECOMMENDED: move `pip.conf` into the resulting `venv/` directory.
2. Activate the virtual environment and install the script dependencies referenced in the imports section as needed.
    1. RECOMMENDED: install dependencies listed in the relevant section of `setup.py` using the following command `pip install '.[cnm_check]'`

### Running locally

1. Run `python cnm_check.py <input_file>` from the same directory.


### Installation on Mozart

Not required

### Running on Mozart
1. Configure `~/mozart/ops/opera-pcm/tools/.env` as needed
2. Run `python ~/mozart/ops/opera-pcm/tools/ops/cnm_check.py` 


### Sample commands
```
$ python ~/mozart/ops/opera-pcm/tools/ops/cnm_check.py -h

more sample commands

```
