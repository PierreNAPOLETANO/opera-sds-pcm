import logging
import time

import conftest
from int_test_util import \
    mock_cnm_r_success_sns, \
    mock_cnm_r_success_sqs, \
    wait_for_cnm_s_success, \
    wait_for_cnm_r_success, \
    wait_for_l3
from subscriber_util import \
    wait_for_query_job, \
    wait_for_download_jobs, \
    invoke_l30_subscriber_query_lambda, \
    update_env_vars_l30_subscriber_query_lambda, \
    reset_env_vars_l30_subscriber_query_lambda, \
    invoke_s30_subscriber_query_lambda, \
    update_env_vars_s30_subscriber_query_lambda, \
    reset_env_vars_s30_subscriber_query_lambda, \
    invoke_slc_subscriber_query_lambda, \
    update_env_vars_slc_subscriber_query_lambda, \
    reset_env_vars_slc_subscriber_query_lambda

config = conftest.config

    
def test_subscriber_l30():
    logging.info("TRIGGERING DATA SUBSCRIBE")

    update_env_vars_l30_subscriber_query_lambda()
    sleep_for(30)

    response = invoke_l30_subscriber_query_lambda()

    reset_env_vars_l30_subscriber_query_lambda()
    sleep_for(30)

    assert response["StatusCode"] == 200

    job_id = response["Payload"].read().decode().strip("\"")
    logging.info(f"{job_id=}")

    logging.info("Sleeping for query job execution...")
    sleep_for(300)

    wait_for_query_job(job_id)

    logging.info("Sleeping for download job execution...")
    sleep_for(300)
    wait_for_download_jobs(job_id)

    logging.info("CHECKING FOR L3 ENTRIES, INDICATING SUCCESSFUL PGE EXECUTION")

    logging.info("Sleeping for PGE execution...")
    sleep_for(300)

    response = wait_for_l3(_id="OPERA_L3_DSWx-HLS_T02LQK_20211228T211639Z_20211228T211639Z_L8_30_v2.0", index="grq_v2.0_l3_dswx_hls")
    assert response.hits[0]["id"] == "OPERA_L3_DSWx-HLS_T02LQK_20211228T211639Z_20211228T211639Z_L8_30_v2.0"

    logging.info("CHECKING FOR CNM-S SUCCESS")

    logging.info("Sleeping for CNM-S execution...")
    sleep_for(150)

    response = wait_for_cnm_s_success(_id="OPERA_L3_DSWx-HLS_T02LQK_20211228T211639Z_20211228T211639Z_L8_30_v2.0", index="grq_v2.0_l3_dswx_hls")
    assert_cnm_s_success(response)

    logging.info("TRIGGER AND CHECK FOR CNM-R SUCCESS")
    mock_cnm_r_success_sns(id="OPERA_L3_DSWx-HLS_T02LQK_20211228T211639Z_20211228T211639Z_L8_30_v2.0")

    logging.info("Sleeping for CNM-R execution...")
    sleep_for(150)

    response = wait_for_cnm_r_success(_id="OPERA_L3_DSWx-HLS_T02LQK_20211228T211639Z_20211228T211639Z_L8_30_v2.0", index="grq_v2.0_l3_dswx_hls")
    assert_cnm_r_success(response)


def test_subscriber_s30():
    logging.info("TRIGGERING DATA SUBSCRIBE")

    update_env_vars_s30_subscriber_query_lambda()
    sleep_for(30)

    response = invoke_s30_subscriber_query_lambda()

    reset_env_vars_s30_subscriber_query_lambda()
    sleep_for(30)

    assert response["StatusCode"] == 200

    job_id = response["Payload"].read().decode().strip("\"")
    logging.info(f"{job_id=}")

    logging.info("Sleeping for query job execution...")
    sleep_for(150)

    wait_for_query_job(job_id)

    logging.info("Sleeping for download job execution...")
    sleep_for(150)
    wait_for_download_jobs(job_id)

    logging.info("CHECKING FOR L3 ENTRIES, INDICATING SUCCESSFUL PGE EXECUTION")

    logging.info("Sleeping for PGE execution...")
    sleep_for(150)

    response = wait_for_l3(_id="OPERA_L3_DSWx-HLS_T15TUF_20200526T165849Z_20200526T165849Z_S2A_30_v2.0", index="grq_v2.0_l3_dswx_hls")
    assert response.hits[0]["id"] == "OPERA_L3_DSWx-HLS_T15TUF_20200526T165849Z_20200526T165849Z_S2A_30_v2.0"

    logging.info("CHECKING FOR CNM-S SUCCESS")

    logging.info("Sleeping for CNM-S execution...")
    sleep_for(150)

    response = wait_for_cnm_s_success(_id="OPERA_L3_DSWx-HLS_T15TUF_20200526T165849Z_20200526T165849Z_S2A_30_v2.0", index="grq_v2.0_l3_dswx_hls")
    assert_cnm_s_success(response)

    logging.info("TRIGGER AND CHECK FOR CNM-R SUCCESS")
    mock_cnm_r_success_sns(id="OPERA_L3_DSWx-HLS_T15TUF_20200526T165849Z_20200526T165849Z_S2A_30_v2.0")

    logging.info("Sleeping for CNM-R execution...")
    sleep_for(150)

    response = wait_for_cnm_r_success(_id="OPERA_L3_DSWx-HLS_T15TUF_20200526T165849Z_20200526T165849Z_S2A_30_v2.0", index="grq_v2.0_l3_dswx_hls")
    assert_cnm_r_success(response)


def test_subscriber_slc():
    logging.info("TRIGGERING DATA SUBSCRIBE")

    update_env_vars_slc_subscriber_query_lambda()
    sleep_for(30)

    response = invoke_slc_subscriber_query_lambda()

    reset_env_vars_slc_subscriber_query_lambda()
    sleep_for(30)

    assert response["StatusCode"] == 200

    job_id = response["Payload"].read().decode().strip("\"")
    logging.info(f"{job_id=}")

    logging.info("Sleeping for query job execution...")
    sleep_for(300)

    wait_for_query_job(job_id)

    logging.info("Sleeping for download job execution...")
    sleep_for(300)
    wait_for_download_jobs(job_id, index="slc_catalog")

    logging.info("CHECKING FOR L3 ENTRIES, INDICATING SUCCESSFUL PGE EXECUTION")

    logging.info("Sleeping for PGE execution...")
    sleep_for(300)

    # CSLC

    # 18-IW1, 18-IW2, 18-IW3
    response = wait_for_l3(_id="OPERA_L2_CSLC-S1A_IW_T064-135518-IW1_VV_20221117T004741Z_v0.1_20221117T004756Z", index="grq_v0.1_l2_cslc_s1")
    assert response.hits[0]["id"] == "OPERA_L2_CSLC-S1A_IW_T064-135518-IW1_VV_20221117T004741Z_v0.1_20221117T004756Z"
    response = wait_for_l3(_id="OPERA_L2_CSLC-S1A_IW_T064-135518-IW2_VV_20221117T004741Z_v0.1_20221117T004756Z", index="grq_v0.1_l2_cslc_s1")
    assert response.hits[0]["id"] == "OPERA_L2_CSLC-S1A_IW_T064-135518-IW2_VV_20221117T004741Z_v0.1_20221117T004756Z"
    response = wait_for_l3(_id="OPERA_L2_CSLC-S1A_IW_T064-135518-IW3_VV_20221117T004741Z_v0.1_20221117T004756Z", index="grq_v0.1_l2_cslc_s1")
    assert response.hits[0]["id"] == "OPERA_L2_CSLC-S1A_IW_T064-135518-IW3_VV_20221117T004741Z_v0.1_20221117T004756Z"

    # 19-IW1, 19-IW2, 19-IW3
    response = wait_for_l3(_id="OPERA_L2_CSLC-S1A_IW_T064-135519-IW1_VV_20221117T004741Z_v0.1_20221117T004756Z", index="grq_v0.1_l2_cslc_s1")
    assert response.hits[0]["id"] == "OPERA_L2_CSLC-S1A_IW_T064-135519-IW1_VV_20221117T004741Z_v0.1_20221117T004756Z"
    response = wait_for_l3(_id="OPERA_L2_CSLC-S1A_IW_T064-135519-IW2_VV_20221117T004741Z_v0.1_20221117T004756Z", index="grq_v0.1_l2_cslc_s1")
    assert response.hits[0]["id"] == "OPERA_L2_CSLC-S1A_IW_T064-135519-IW2_VV_20221117T004741Z_v0.1_20221117T004756Z"
    response = wait_for_l3(_id="OPERA_L2_CSLC-S1A_IW_T064-135519-IW3_VV_20221117T004741Z_v0.1_20221117T004756Z", index="grq_v0.1_l2_cslc_s1")
    assert response.hits[0]["id"] == "OPERA_L2_CSLC-S1A_IW_T064-135519-IW3_VV_20221117T004741Z_v0.1_20221117T004756Z"

    # 20-IW1, 20-IW2, 20-IW3
    response = wait_for_l3(_id="OPERA_L2_CSLC-S1A_IW_T064-135520-IW1_VV_20221117T004741Z_v0.1_20221117T004756Z", index="grq_v0.1_l2_cslc_s1")
    assert response.hits[0]["id"] == "OPERA_L2_CSLC-S1A_IW_T064-135520-IW1_VV_20221117T004741Z_v0.1_20221117T004756Z"
    response = wait_for_l3(_id="OPERA_L2_CSLC-S1A_IW_T064-135520-IW2_VV_20221117T004741Z_v0.1_20221117T004756Z", index="grq_v0.1_l2_cslc_s1")
    assert response.hits[0]["id"] == "OPERA_L2_CSLC-S1A_IW_T064-135520-IW2_VV_20221117T004741Z_v0.1_20221117T004756Z"
    response = wait_for_l3(_id="OPERA_L2_CSLC-S1A_IW_T064-135520-IW3_VV_20221117T004741Z_v0.1_20221117T004756Z", index="grq_v0.1_l2_cslc_s1")
    assert response.hits[0]["id"] == "OPERA_L2_CSLC-S1A_IW_T064-135520-IW3_VV_20221117T004741Z_v0.1_20221117T004756Z"

    # RTC

    # 70-IW1, 70-IW3
    response = wait_for_l3(_id="OPERA_L2_RTC-S1_T069-147170-IW1_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert response.hits[0]["id"] == "OPERA_L2_RTC-S1_T069-147170-IW1_20221117T004741Z_20221117T004756Z_S1A_30_v0.1"
    response = wait_for_l3(_id="OPERA_L2_RTC-S1_T069-147170-IW3_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert response.hits[0]["id"] == "OPERA_L2_RTC-S1_T069-147170-IW3_20221117T004741Z_20221117T004756Z_S1A_30_v0.1"

    # 71-IW1, 71-IW2, 71-IW3
    response = wait_for_l3(_id="OPERA_L2_RTC-S1_T069-147171-IW1_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert response.hits[0]["id"] == "OPERA_L2_RTC-S1_T069-147171-IW1_20221117T004741Z_20221117T004756Z_S1A_30_v0.1"
    response = wait_for_l3(_id="OPERA_L2_RTC-S1_T069-147171-IW2_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert response.hits[0]["id"] == "OPERA_L2_RTC-S1_T069-147171-IW2_20221117T004741Z_20221117T004756Z_S1A_30_v0.1"
    response = wait_for_l3(_id="OPERA_L2_RTC-S1_T069-147171-IW3_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert response.hits[0]["id"] == "OPERA_L2_RTC-S1_T069-147171-IW3_20221117T004741Z_20221117T004756Z_S1A_30_v0.1"

    # 72-IW1, 72-IW2, 72-IW3
    response = wait_for_l3(_id="OPERA_L2_RTC-S1_T069-147172-IW1_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert response.hits[0]["id"] == "OPERA_L2_RTC-S1_T069-147172-IW1_20221117T004741Z_20221117T004756Z_S1A_30_v0.1"
    response = wait_for_l3(_id="OPERA_L2_RTC-S1_T069-147172-IW2_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert response.hits[0]["id"] == "OPERA_L2_RTC-S1_T069-147172-IW2_20221117T004741Z_20221117T004756Z_S1A_30_v0.1"
    response = wait_for_l3(_id="OPERA_L2_RTC-S1_T069-147172-IW3_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert response.hits[0]["id"] == "OPERA_L2_RTC-S1_T069-147172-IW3_20221117T004741Z_20221117T004756Z_S1A_30_v0.1"

    # 73-IW1
    response = wait_for_l3(_id="OPERA_L2_RTC-S1_T069-147173-IW1_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert response.hits[0]["id"] == "OPERA_L2_RTC-S1_T069-147173-IW1_20221117T004741Z_20221117T004756Z_S1A_30_v0.1"

    logging.info("CHECKING FOR CNM-S SUCCESS")

    logging.info("Sleeping for CNM-S execution...")
    sleep_for(300)

    response = wait_for_cnm_s_success(_id="OPERA_L2_CSLC-S1A_IW_T064-135518-IW1_VV_20221117T004741Z_v0.1_20221117T004756Z", index="grq_v0.1_l2_cslc_s1")
    assert_cnm_s_success(response)

    # 70-IW1, 70-IW3
    response = wait_for_cnm_s_success(_id="OPERA_L2_RTC-S1_T069-147170-IW1_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert_cnm_s_success(response)
    response = wait_for_cnm_s_success(_id="OPERA_L2_RTC-S1_T069-147170-IW3_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert_cnm_s_success(response)

    # 71-IW1, 71-IW2, 71-IW3
    response = wait_for_cnm_s_success(_id="OPERA_L2_RTC-S1_T069-147171-IW1_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert_cnm_s_success(response)
    response = wait_for_cnm_s_success(_id="OPERA_L2_RTC-S1_T069-147171-IW2_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert_cnm_s_success(response)
    response = wait_for_cnm_s_success(_id="OPERA_L2_RTC-S1_T069-147171-IW3_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert_cnm_s_success(response)

    # 72-IW1, 72-IW2, 72-IW3
    response = wait_for_cnm_s_success(_id="OPERA_L2_RTC-S1_T069-147172-IW1_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert_cnm_s_success(response)
    response = wait_for_cnm_s_success(_id="OPERA_L2_RTC-S1_T069-147172-IW2_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert_cnm_s_success(response)
    response = wait_for_cnm_s_success(_id="OPERA_L2_RTC-S1_T069-147172-IW3_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert_cnm_s_success(response)

    # 73-IW1
    response = wait_for_cnm_s_success(_id="OPERA_L2_RTC-S1_T069-147173-IW1_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert_cnm_s_success(response)

    logging.info("TRIGGER AND CHECK FOR CNM-R SUCCESS")
    mock_cnm_r_success_sqs(id="OPERA_L2_CSLC-S1A_IW_T064-135518-IW1_VV_20221117T004741Z_v0.1_20221117T004756Z")

    # 70-IW1, 70-IW3
    mock_cnm_r_success_sqs(id="OPERA_L2_RTC-S1_T069-147170-IW1_20221117T004741Z_20221117T004756Z_S1A_30_v0.1")
    mock_cnm_r_success_sqs(id="OPERA_L2_RTC-S1_T069-147170-IW3_20221117T004741Z_20221117T004756Z_S1A_30_v0.1")

    # 71-IW1, 71-IW2, 71-IW3
    mock_cnm_r_success_sqs(id="OPERA_L2_RTC-S1_T069-147171-IW1_20221117T004741Z_20221117T004756Z_S1A_30_v0.1")
    mock_cnm_r_success_sqs(id="OPERA_L2_RTC-S1_T069-147171-IW2_20221117T004741Z_20221117T004756Z_S1A_30_v0.1")
    mock_cnm_r_success_sqs(id="OPERA_L2_RTC-S1_T069-147171-IW3_20221117T004741Z_20221117T004756Z_S1A_30_v0.1")

    # 72-IW1, 72-IW2, 72-IW3
    mock_cnm_r_success_sqs(id="OPERA_L2_RTC-S1_T069-147172-IW1_20221117T004741Z_20221117T004756Z_S1A_30_v0.1")
    mock_cnm_r_success_sqs(id="OPERA_L2_RTC-S1_T069-147172-IW2_20221117T004741Z_20221117T004756Z_S1A_30_v0.1")
    mock_cnm_r_success_sqs(id="OPERA_L2_RTC-S1_T069-147172-IW3_20221117T004741Z_20221117T004756Z_S1A_30_v0.1")

    # 73-IW1
    mock_cnm_r_success_sqs(id="OPERA_L2_RTC-S1_T069-147173-IW1_20221117T004741Z_20221117T004756Z_S1A_30_v0.1")

    logging.info("Sleeping for CNM-R execution...")
    sleep_for(300)

    response = wait_for_cnm_r_success(_id="OPERA_L2_CSLC-S1A_IW_T064-135518-IW1_VV_20221117T004741Z_v0.1_20221117T004756Z", index="grq_v0.1_l2_cslc_s1")
    assert_cnm_r_success(response)

    # 70-IW1, 70-IW3
    response = wait_for_cnm_r_success(_id="OPERA_L2_RTC-S1_T069-147170-IW1_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert_cnm_r_success(response)
    response = wait_for_cnm_r_success(_id="OPERA_L2_RTC-S1_T069-147170-IW3_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert_cnm_r_success(response)

    # 71-IW1, 71-IW2, 71-IW3
    response = wait_for_cnm_r_success(_id="OPERA_L2_RTC-S1_T069-147171-IW1_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert_cnm_r_success(response)
    response = wait_for_cnm_r_success(_id="OPERA_L2_RTC-S1_T069-147171-IW2_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert_cnm_r_success(response)
    response = wait_for_cnm_r_success(_id="OPERA_L2_RTC-S1_T069-147171-IW3_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert_cnm_r_success(response)

    # 72-IW1, 72-IW2, 72-IW3
    response = wait_for_cnm_r_success(_id="OPERA_L2_RTC-S1_T069-147172-IW1_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert_cnm_r_success(response)
    response = wait_for_cnm_r_success(_id="OPERA_L2_RTC-S1_T069-147172-IW2_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert_cnm_r_success(response)
    response = wait_for_cnm_r_success(_id="OPERA_L2_RTC-S1_T069-147172-IW3_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert_cnm_r_success(response)

    # 73-IW1
    response = wait_for_cnm_r_success(_id="OPERA_L2_RTC-S1_T069-147173-IW1_20221117T004741Z_20221117T004756Z_S1A_30_v0.1", index="grq_v0.1_l2_rtc_s1")
    assert_cnm_r_success(response)


def assert_cnm_s_success(response):
    assert response.hits.hits[0]["_source"]["daac_CNM_S_status"] == "SUCCESS"
    assert response.hits.hits[0]["_source"]["daac_CNM_S_timestamp"] is not None


def assert_cnm_r_success(response):
    assert response.hits.hits[0]["_source"]["daac_delivery_status"] == "SUCCESS"
    assert response.hits.hits[0]["_source"]["daac_identifier"] is not None

    assert response.hits.hits[0]["_source"]["daac_received_timestamp"] is not None
    assert response.hits.hits[0]["_source"]["daac_submission_timestamp"] is not None
    assert response.hits.hits[0]["_source"]["daac_collection"] is not None
    assert response.hits.hits[0]["_source"]["daac_process_complete_timestamp"] is not None

    # CNM-R ingestion metadata
    assert response.hits.hits[0]["_source"]["daac_catalog_id"] is not None
    assert response.hits.hits[0]["_source"]["daac_catalog_url"] is not None


def sleep_for(sec=None):
    logging.info(f"Sleeping for {sec} seconds...")
    time.sleep(sec)
    logging.info("Done sleeping.")
