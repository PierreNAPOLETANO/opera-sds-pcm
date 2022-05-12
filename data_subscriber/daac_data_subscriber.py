#!/usr/bin/env python3

# Forked from github.com:podaac/data-subscriber.git


import argparse
import json
import logging
import netrc
import os
import shutil
import sys
from datetime import datetime, timedelta
from http.cookiejar import CookieJar
from multiprocessing.pool import ThreadPool
from urllib import request
from urllib.parse import urlparse

import boto3
import requests
from smart_open import open

from data_subscriber.hls.hls_catalog_connection import get_hls_catalog_connection
from data_subscriber.hls_spatial.hls_spatial_catalog_connection import get_hls_spatial_catalog_connection


class SessionWithHeaderRedirection(requests.Session):
    """
    Borrowed from https://wiki.earthdata.nasa.gov/display/EL/How+To+Access+Data+With+Python
    """

    def __init__(self, username, password, auth_host):
        super().__init__()
        self.auth = (username, password)
        self.auth_host = auth_host

    # Overrides from the library to keep headers when redirected to or from
    # the NASA auth host.
    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        url = prepared_request.url

        if 'Authorization' in headers:
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)
            if (original_parsed.hostname != redirect_parsed.hostname) and \
                    redirect_parsed.hostname != self.auth_host and \
                    original_parsed.hostname != self.auth_host:
                del headers['Authorization']
        return


def run():
    parser = create_parser()
    args = parser.parse_args()

    try:
        validate(args)
    except ValueError as v:
        logging.error(v)
        exit()

    IP_ADDR = "127.0.0.1"
    EDL = "urs.earthdata.nasa.gov"
    CMR = "cmr.earthdata.nasa.gov"
    TOKEN_URL = f"https://{CMR}/legacy-services/rest/tokens"
    NETLOC = urlparse("https://urs.earthdata.nasa.gov").netloc
    HLS_CONN = get_hls_catalog_connection(logging.getLogger(__name__))

    LOGLEVEL = 'DEBUG' if args.verbose else 'INFO'
    logging.basicConfig(level=LOGLEVEL)
    logging.info("Log level set to " + LOGLEVEL)

    logging.info(f"sys.argv = {sys.argv}")

    username, password = setup_earthdata_login_auth(EDL)
    token = get_token(TOKEN_URL, 'daac-subscriber', IP_ADDR, EDL)

    temporal_range = None

    if args.subparser_name != "download":
        HLS_SPATIAL_CONN = get_hls_spatial_catalog_connection(logging.getLogger(__name__))
        granules, temporal_range = query_cmr(args, token, CMR)
        for granule in granules:
            update_url_index(HLS_CONN, granule.get("filtered_urls"), granule.get("granule_id"))
            update_granule_index(HLS_SPATIAL_CONN, granules)

    if args.subparser_name != "query":
        urls = HLS_CONN.get_all_undownloaded()
        session = SessionWithHeaderRedirection(username, password, NETLOC)

        if args.transfer_protocol.lower() == "https":
            upload_url_list_from_https(session, HLS_CONN, urls, args, token)
        else:
            upload_url_list_from_s3(session, HLS_CONN, urls, args)

        logging.info(f"Total files updated: {len(urls)}")

    if temporal_range:
        logging.info(f"Temporal range: {temporal_range}")

    delete_token(TOKEN_URL, token)
    logging.info("END")


def create_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subparser_name", required=True)
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="Verbose mode.")

    full_parser = subparsers.add_parser("full")
    full_parser.add_argument("-c", "--collection", dest="collection", required=True,
                             help="The collection for which you want to retrieve data.")
    full_parser.add_argument("-sd", "--start-date", dest="startDate", default=False,
                             help="The ISO date time after which data should be retrieved. For Example, --start-date 2021-01-14T00:00:00Z")
    full_parser.add_argument("-ed", "--end-date", dest="endDate", default=False,
                             help="The ISO date time before which data should be retrieved. For Example, --end-date 2021-01-14T00:00:00Z")
    full_parser.add_argument("-b", "--bounds", dest="bbox", default="-180,-90,180,90",
                             help="The bounding rectangle to filter result in. Format is W Longitude,S Latitude,E Longitude,N Latitude without spaces. Due to an issue with parsing arguments, to use this command, please use the -b=\"-180,-90,180,90\" syntax when calling from the command line. Default: \"-180,-90,180,90\".")
    full_parser.add_argument("-m", "--minutes", dest="minutes", type=int, default=60,
                             help="How far back in time, in minutes, should the script look for data. If running this script as a cron, this value should be equal to or greater than how often your cron runs (default: 60 minutes).")
    full_parser.add_argument("-p", "--provider", dest="provider", default='LPCLOUD',
                             help="Specify a provider for collection search. Default is LPCLOUD.")
    full_parser.add_argument("-s", "--s3bucket", dest="s3_bucket", required=True,
                             help="The s3 bucket where data products will be downloaded.")
    full_parser.add_argument("-x", "--transfer-protocol", dest="transfer_protocol", default='s3',
                             help="The protocol used for retrieving data, HTTPS or default of S3")

    query_parser = subparsers.add_parser("query")
    query_parser.add_argument("-c", "--collection-shortname", dest="collection", required=True,
                              help="The collection shortname for which you want to retrieve data.")
    query_parser.add_argument("-sd", "--start-date", dest="startDate", default=False,
                              help="The ISO date time after which data should be retrieved. For Example, --start-date 2021-01-14T00:00:00Z")
    query_parser.add_argument("-ed", "--end-date", dest="endDate", default=False,
                              help="The ISO date time before which data should be retrieved. For Example, --end-date 2021-01-14T00:00:00Z")
    query_parser.add_argument("-b", "--bounds", dest="bbox", default="-180,-90,180,90",
                              help="The bounding rectangle to filter result in. Format is W Longitude,S Latitude,E Longitude,N Latitude without spaces. Due to an issue with parsing arguments, to use this command, please use the -b=\"-180,-90,180,90\" syntax when calling from the command line. Default: \"-180,-90,180,90\".")
    query_parser.add_argument("-m", "--minutes", dest="minutes", type=int, default=60,
                              help="How far back in time, in minutes, should the script look for data. If running this script as a cron, this value should be equal to or greater than how often your cron runs (default: 60 minutes).")
    query_parser.add_argument("-p", "--provider", dest="provider", default='LPCLOUD',
                              help="Specify a provider for collection search. Default is LPCLOUD.")

    download_parser = subparsers.add_parser("download")
    download_parser.add_argument("-s", "--s3bucket", dest="s3_bucket", required=True,
                                 help="The s3 bucket where data products will be downloaded.")
    download_parser.add_argument("-x", "--transfer-protocol", dest="transfer_protocol", default='s3',
                                 help="The protocol used for retrieving data, HTTPS or default of S3")

    return parser


def validate(args):
    if args.bbox:
        validate_bounds(args.bbox)

    if args.startDate:
        validate_date(args.startDate, "start")

    if args.endDate:
        validate_date(args.endDate, "end")

    if args.minutes:
        validate_minutes(args.minutes)


def validate_bounds(bbox):
    bounds = bbox.split(',')
    value_error = ValueError(
        f"Error parsing bounds: {bbox}. Format is <W Longitude>,<S Latitude>,<E Longitude>,<N Latitude> without spaces ")

    if len(bounds) != 4:
        raise value_error

    for b in bounds:
        try:
            float(b)
        except ValueError:
            raise value_error


def validate_date(date, type='start'):
    try:
        datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        raise ValueError(
            f"Error parsing {type} date: {date}. Format must be like 2021-01-14T00:00:00Z")


def validate_minutes(minutes):
    try:
        int(minutes)
    except ValueError:
        raise ValueError(f"Error parsing minutes: {minutes}. Number must be an integer.")


def setup_earthdata_login_auth(endpoint):
    # ## Authentication setup
    #
    # This function will allow Python scripts to log into any Earthdata Login
    # application programmatically.  To avoid being prompted for
    # credentials every time you run and also allow clients such as curl to log in,
    # you can add the following to a `.netrc` (`_netrc` on Windows) file in
    # your home directory:
    #
    # ```
    # machine urs.earthdata.nasa.gov
    #     login <your username>
    #     password <your password>
    # ```
    #
    # Make sure that this file is only readable by the current user
    # or you will receive an error stating
    # "netrc access too permissive."
    #
    # `$ chmod 0600 ~/.netrc`
    #
    # You'll need to authenticate using the netrc method when running from
    # command line with [`papermill`](https://papermill.readthedocs.io/en/latest/).
    # You can log in manually by executing the cell below when running in the
    # notebook client in your browser.*

    """
    Set up the request library so that it authenticates against the given
    Earthdata Login endpoint and is able to track cookies between requests.
    This looks in the .netrc file first and if no credentials are found,
    it prompts for them.

    Valid endpoints include:
        urs.earthdata.nasa.gov - Earthdata Login production
    """
    username = password = ""
    try:
        username, _, password = netrc.netrc().authenticators(endpoint)
    except (FileNotFoundError):
        logging.error("There's no .netrc file")
    except (TypeError):
        logging.error("The endpoint isn't in the netrc file")

    manager = request.HTTPPasswordMgrWithDefaultRealm()
    manager.add_password(None, endpoint, username, password)
    auth = request.HTTPBasicAuthHandler(manager)

    jar = CookieJar()
    processor = request.HTTPCookieProcessor(jar)
    opener = request.build_opener(auth, processor)
    opener.addheaders = [('User-agent', 'daac-subscriber')]
    request.install_opener(opener)

    return username, password


def get_token(url: str, client_id: str, user_ip: str, endpoint: str) -> str:
    username, _, password = netrc.netrc().authenticators(endpoint)
    xml = f"<?xml version='1.0' encoding='utf-8'?><token><username>{username}</username><password>{password}</password><client_id>{client_id}</client_id><user_ip_address>{user_ip}</user_ip_address></token>"
    headers = {'Content-Type': 'application/xml', 'Accept': 'application/json'}
    resp = requests.post(url, headers=headers, data=xml)
    response_content = json.loads(resp.content)
    token = response_content['token']['id']

    return token


def query_cmr(args, token, CMR):
    PAGE_SIZE = 2000
    time_range_is_defined = args.startDate or args.endDate

    data_within_last_timestamp = args.startDate if time_range_is_defined else (
            datetime.utcnow() - timedelta(minutes=args.minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")

    request_url = f"https://{CMR}/search/granules.umm_json"
    params = {
        'scroll': "false",
        'page_size': PAGE_SIZE,
        'sort_key': "-start_date",
        'provider': args.provider,
        'ShortName': args.collection,
        'updated_since': data_within_last_timestamp,
        'token': token,
        'bounding_box': args.bbox,
    }

    temporal_range = get_temporal_range(data_within_last_timestamp, args.endDate,
                                        datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
    if time_range_is_defined:
        params['temporal'] = temporal_range
        logging.debug("Temporal Range: " + temporal_range)

    product_granules, search_after = request_search(request_url, params)

    while search_after:
        granules, search_after = request_search(request_url, params, search_after=search_after)
        product_granules.extend(granules)

    logging.info(f"Found {str(len(product_granules))} total granules")
    for granule in product_granules:
        granule['filtered_urls'] = filter_on_extension(granule, args)

    return product_granules, temporal_range


def get_temporal_range(start, end, now):
    start = start if start is not False else None
    end = end if end is not False else None

    if start is not None and end is not None:
        return "{},{}".format(start, end)
    if start is not None and end is None:
        return "{},{}".format(start, now)
    if start is None and end is not None:
        return "1900-01-01T00:00:00Z,{}".format(end)

    raise ValueError("One of start-date or end-date must be specified.")


def request_search(request_url, params, search_after=None):
    response = requests.get(request_url, params=params, headers={'CMR-Search-After': search_after}) \
        if search_after else requests.get(request_url, params=params)
    results = response.json()
    items = results.get('items')
    next_search_after = response.headers.get('CMR-Search-After')

    if items and 'umm' in items[0]:
        return [{"granule_id": item.get("umm").get("GranuleUR"),
                 "provider": item.get("meta").get("provider-id"),
                 "production_datetime": item.get("umm").get("DataGranule").get("ProductionDateTime"),
                 "short_name": item.get("umm").get("Platforms")[0].get("ShortName"),
                 "bounding_box": [geo_item
                                  for geo_item
                                  in item.get("umm").get("SpatialExtent").get("HorizontalSpatialDomain")
                                      .get("Geometry").get("GPolygons")[0].get("Boundary").get("Points")],
                 "related_urls": [url_item.get("URL") for url_item in item.get("umm").get("RelatedUrls")]}
                for item in items], next_search_after
    else:
        return [], None


def filter_on_extension(granule, args):
    EXTENSION_LIST_MAP = {"L30": ["B02", "B03", "B04", "B05", "B06", "B07", "Fmask"],
                          "S30": ["B02", "B03", "B04", "B8A", "B11", "B12", "Fmask"],
                          "TIF": ["tif"]}
    filter_extension = "TIF"

    for extension in EXTENSION_LIST_MAP:
        if extension.upper() in args.collection.upper():
            filter_extension = extension.upper()
            break

    return [f
            for f in granule.get("related_urls")
            for extension in EXTENSION_LIST_MAP.get(filter_extension)
            if extension in f]


def convert_datetime(datetime_obj, strformat="%Y-%m-%dT%H:%M:%S.%fZ"):
    if isinstance(datetime_obj, datetime):
        return datetime_obj.strftime(strformat)
    return datetime.strptime(str(datetime_obj), strformat)


def update_url_index(ES_CONN, urls, granule_id):
    for url in urls:
        ES_CONN.process_url(url, granule_id)


def update_granule_index(ES_SPATIAL_CONN, granule):
    ES_SPATIAL_CONN.process_granule(granule)


def upload_url_list_from_https(session, ES_CONN, downloads, args, token):
    num_successes = num_failures = num_skipped = 0
    filtered_downloads = [f for f in downloads if "https://" in f]

    for url in filtered_downloads:
        try:
            if ES_CONN.product_is_downloaded(url):
                logging.info(f"SKIPPING: {url}")
                num_skipped = num_skipped + 1
            else:
                result = https_transfer(url, args.s3_bucket, session, token)
                if "failed_download" in result:
                    raise Exception(result["failed_download"])
                else:
                    logging.debug(str(result))

                ES_CONN.mark_product_as_downloaded(url)
                logging.info(f"{str(datetime.now())} SUCCESS: {url}")
                num_successes = num_successes + 1
        except Exception as e:
            logging.error(f"{str(datetime.now())} FAILURE: {url}")
            num_failures = num_failures + 1
            logging.error(e)

    logging.info(f"Files downloaded: {str(num_successes)}")
    logging.info(f"Duplicate files skipped: {str(num_skipped)}")
    logging.info(f"Files failed to download: {str(num_failures)}")


def https_transfer(url, bucket_name, session, token, staging_area="", chunk_size=25600):
    file_name = os.path.basename(url)
    bucket = bucket_name[len("s3://"):] if bucket_name.startswith("s3://") else bucket_name

    key = os.path.join(staging_area, file_name)
    upload_start_time = datetime.utcnow()
    headers = {"Echo-Token": token}

    try:
        with session.get(url, headers=headers, stream=True) as r:
            if r.status_code != 200:
                r.raise_for_status()
            logging.info("Uploading {} to Bucket={}, Key={}".format(file_name, bucket_name, key))
            with open("s3://{}/{}".format(bucket, key), "wb") as out:
                pool = ThreadPool(processes=10)
                pool.map(upload_chunk,
                         [{'chunk': chunk, 'out': out} for chunk in r.iter_content(chunk_size=chunk_size)])
                pool.close()
                pool.join()
        upload_end_time = datetime.utcnow()
        upload_duration = upload_end_time - upload_start_time
        upload_stats = {
            "file_name": file_name,
            "file_size (in bytes)": r.headers.get('Content-Length'),
            "upload_duration (in seconds)": upload_duration.total_seconds(),
            "upload_start_time": convert_datetime(upload_start_time),
            "upload_end_time": convert_datetime(upload_end_time)
        }
        return upload_stats
    except (ConnectionResetError, requests.exceptions.HTTPError) as e:
        return {"failed_download": e}


def upload_chunk(chunk_dict):
    logging.debug("Uploading {} byte(s)".format(len(chunk_dict['chunk'])))
    chunk_dict['out'].write(chunk_dict['chunk'])


def upload_url_list_from_s3(session, ES_CONN, downloads, args):
    aws_creds = get_aws_creds(session)
    s3 = boto3.Session(aws_access_key_id=aws_creds['accessKeyId'],
                       aws_secret_access_key=aws_creds['secretAccessKey'],
                       aws_session_token=aws_creds['sessionToken'],
                       region_name='us-west-2').client("s3")

    tmp_dir = "/tmp/data_subscriber"
    os.makedirs(tmp_dir, exist_ok=True)

    num_successes = num_failures = num_skipped = 0
    filtered_downloads = [f for f in downloads if "s3://" in f]

    for url in filtered_downloads:
        try:
            if ES_CONN.product_is_downloaded(url):
                logging.info(f"SKIPPING: {url}")
                num_skipped = num_skipped + 1
            else:
                result = s3_transfer(url, args.s3_bucket, s3, tmp_dir)
                if "failed_download" in result:
                    raise Exception(result["failed_download"])
                else:
                    logging.debug(str(result))

                ES_CONN.mark_product_as_downloaded(url)
                logging.info(f"{str(datetime.now())} SUCCESS: {url}")
                num_successes = num_successes + 1
        except Exception as e:
            logging.error(f"{str(datetime.now())} FAILURE: {url}")
            num_failures = num_failures + 1
            logging.error(e)

    logging.info(f"Files downloaded: {str(num_successes)}")
    logging.info(f"Duplicate files skipped: {str(num_skipped)}")
    logging.info(f"Files failed to download: {str(num_failures)}")

    shutil.rmtree(tmp_dir)


def get_aws_creds(session):
    with session.get("https://data.lpdaac.earthdatacloud.nasa.gov/s3credentials") as r:
        if r.status_code != 200:
            r.raise_for_status()

        return r.json()


def s3_transfer(url, bucket_name, s3, tmp_dir, staging_area=""):
    file_name = os.path.basename(url)

    source = url[len("s3://"):].partition('/')
    source_bucket = source[0]
    source_key = source[2]

    target_bucket = bucket_name[len("s3://"):] if bucket_name.startswith("s3://") else bucket_name
    target_key = os.path.join(staging_area, file_name)

    try:
        s3.download_file(source_bucket, source_key, f"{tmp_dir}/{target_key}")

        target_s3 = boto3.resource("s3")
        target_s3.Bucket(target_bucket).upload_file(f"{tmp_dir}/{target_key}", target_key)

        return {"successful_download": target_key}
    except Exception as e:
        return {"failed_download": e}


def delete_token(url: str, token: str) -> None:
    try:
        headers = {'Content-Type': 'application/xml', 'Accept': 'application/json'}
        url = '{}/{}'.format(url, token)
        resp = requests.request('DELETE', url, headers=headers)
        if resp.status_code == 204:
            logging.info("CMR token successfully deleted")
        else:
            logging.error("CMR token deleting failed.")
    except:
        logging.error("Error deleting the token")
    exit(0)


if __name__ == '__main__':
    run()
