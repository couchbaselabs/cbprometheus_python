from cb_utilities import *
import urllib
import re
import hashlib

def _get_query_metrics(user, passwrd, node_list, cluster_name="", slow_queries=True):
    '''Gets the metrics for the query nodes'''
    # first get the system:completed_request entries for the past minute
    query_info = {}
    query_info['metrics'] = []

    auth = basic_authorization(user, passwrd)
    if slow_queries:
        query_info['metrics'] = _get_completed_query_metrics(auth, node_list, cluster_name)

    for node in node_list:
        try:
            _query_url = "http://{}:8091/pools/default/buckets/@query/nodes/{}:8091/stats".format(
                node.split(":")[0], node.split(":")[0])
            q_json = rest_request(auth, _query_url)
            _node = value_to_string(node)
            for record in q_json['op']['samples']:
                if record != "timestamp":
                    for idx, datapoint in enumerate(q_json['op']['samples'][record]):
                        query_info['metrics'].append(
                            "{} {{cluster=\"{}\", node=\"{}\", "
                            "type=\"query\"}} {} {}".format(
                                record,
                                cluster_name,
                                _node,
                                datapoint,
                                q_json['op']['samples']['timestamp'][idx]))

        except Exception as e:
            print("query base: " + str(e))
    return query_info

def _get_completed_query_metrics(auth, node_list, cluster_name=""):
    '''Queries system:completed_requests on the specific query node'''
    metrics = []

    # n1ql statement to find all of the the completed requests from the past 60 seconds (if any)
    n1ql_stmt = """SELECT IFMISSING(preparedText, statement) as statement, requestId AS request_id,
        service_time_ms, elapsed_time_ms, queue_time_ms, request_time_ms,
        resultCount AS result_count, resultSize AS result_size, query_selectivity_percent,
        scan_results, fetches
    FROM system:completed_requests
    LET request_time_ms = STR_TO_MILLIS(REPLACE(requestTime, " +0000 UTC", "Z")),
        service_time_ms = ROUND(STR_TO_DURATION(serviceTime) / 1e6),
        elapsed_time_ms = ROUND(STR_TO_DURATION(elapsedTime) / 1e6),
        queue_time_ms = ROUND(
          (STR_TO_DURATION(elapsedTime) - STR_TO_DURATION(serviceTime)) / 1e6
        , 3),
        query_selectivity_percent = ROUND(IFNULL(
          (
            resultCount /
            IFMISSING(phaseCounts.`indexScan`, 0)
          ) * 100,
        0), 2),
        scan_results = IFMISSING(phaseCounts.`indexScan`, 0),
        fetches = IFMISSING(phaseCounts.`fetch`, 0)
    WHERE node = NODE_NAME()
        AND UPPER(IFMISSING(preparedText, statement)) NOT LIKE 'INFER %'
        AND UPPER(IFMISSING(preparedText, statement)) NOT LIKE 'ADVISE %'
        AND UPPER(IFMISSING(preparedText, statement)) NOT LIKE '% INDEX%'
        AND UPPER(IFMISSING(preparedText, statement)) NOT LIKE '% SYSTEM:%'
        AND request_time_ms >= ROUND(NOW_MILLIS(), 0) - 60000"""

    # strip new lines and convert two or more spaces to a single space
    # and then url encode the statement
    n1ql_stmt = urllib.urlencode({ "statement": re.sub(" +", " ", n1ql_stmt.strip("\r\n")) })

    for node in node_list:
        try:
            _query_url = "http://{}:8093/query/service?{}".format(
                node.split(":")[0],
                n1ql_stmt
            )
            q_json = rest_request(auth, _query_url)
            _node = value_to_string(node)
            for record in q_json['results']:
                statement = record['statement'].replace('"','\\"').replace('\n', ' ')
                # generate a hash of the statement so that if the user wants the statement
                # can be disregarded and the hash can still be used to group repeat statements
                statement_signature = hashlib.sha1(statement).hexdigest()
                # stat: consolidated by service_time_ms
                metrics.append(
                    "{} {{cluster=\"{}\", node=\"{}\", "
                    "queue_time_ms=\"{}\", "
                    "elapsed_time_ms=\"{}\", "
                    "result_count=\"{}\", "
                    "result_size=\"{}\", "
                    "query_selectivity_percent=\"{}\", "
                    "scan_results=\"{}\", "
                    "fetches=\"{}\", "
                    "request_id=\"{}\", "
                    "signature=\"{}\", "
                    "statement=\"{}\", "
                    "type=\"completed-query\"}} {} {}".format(
                        "completed_request",
                        cluster_name,
                        _node,
                        record['queue_time_ms'],
                        record['elapsed_time_ms'],
                        record['result_count'],
                        record['result_size'],
                        record['query_selectivity_percent'],
                        record['scan_results'],
                        record['fetches'],
                        record['request_id'],
                        statement_signature,
                        statement,
                        record['service_time_ms'],
                        record['request_time_ms']
                    )
                )
                # stat: service_time_ms
                metrics.append(
                    "{} {{cluster=\"{}\", node=\"{}\", "
                    "request_id=\"{}\", "
                    "signature=\"{}\", "
                    "statement=\"{}\", "
                    "type=\"completed-request\"}} {} {}".format(
                        "completed_request_service_time_ms",
                        cluster_name,
                        _node,
                        record['request_id'],
                        statement_signature,
                        statement,
                        record['service_time_ms'],
                        record['request_time_ms']
                    )
                )
                # stat: queue_time_ms
                metrics.append(
                    "{} {{cluster=\"{}\", node=\"{}\", "
                    "request_id=\"{}\", "
                    "signature=\"{}\", "
                    "statement=\"{}\", "
                    "type=\"completed-request\"}} {} {}".format(
                        "completed_request_queue_time_ms",
                        cluster_name,
                        _node,
                        record['request_id'],
                        statement_signature,
                        statement,
                        record['queue_time_ms'],
                        record['request_time_ms']
                    )
                )
                # stat: elapsed_time_ms
                metrics.append(
                    "{} {{cluster=\"{}\", node=\"{}\", "
                    "request_id=\"{}\", "
                    "signature=\"{}\", "
                    "statement=\"{}\", "
                    "type=\"completed-request\"}} {} {}".format(
                        "completed_request_elapsed_time_ms",
                        cluster_name,
                        _node,
                        record['request_id'],
                        statement_signature,
                        statement,
                        record['elapsed_time_ms'],
                        record['request_time_ms']
                    )
                )
                # stat: result_count
                metrics.append(
                    "{} {{cluster=\"{}\", node=\"{}\", "
                    "request_id=\"{}\", "
                    "signature=\"{}\", "
                    "statement=\"{}\", "
                    "type=\"completed-request\"}} {} {}".format(
                        "completed_request_result_count",
                        cluster_name,
                        _node,
                        record['request_id'],
                        statement_signature,
                        statement,
                        record['result_count'],
                        record['request_time_ms']
                    )
                )
                # stat: result_size_bytes
                metrics.append(
                    "{} {{cluster=\"{}\", node=\"{}\", "
                    "request_id=\"{}\", "
                    "signature=\"{}\", "
                    "statement=\"{}\", "
                    "type=\"completed-request\"}} {} {}".format(
                        "completed_request_result_size_bytes",
                        cluster_name,
                        _node,
                        record['request_id'],
                        statement_signature,
                        statement,
                        record['result_size'],
                        record['request_time_ms']
                    )
                )
                # stat: query_selectivity_percent
                metrics.append(
                    "{} {{cluster=\"{}\", node=\"{}\", "
                    "request_id=\"{}\", "
                    "signature=\"{}\", "
                    "statement=\"{}\", "
                    "type=\"completed-request\"}} {} {}".format(
                        "completed_request_query_selectivity_percent",
                        cluster_name,
                        _node,
                        record['request_id'],
                        statement_signature,
                        statement,
                        record['query_selectivity_percent'],
                        record['request_time_ms']
                    )
                )
                # stat: scan_results
                metrics.append(
                    "{} {{cluster=\"{}\", node=\"{}\", "
                    "request_id=\"{}\", "
                    "signature=\"{}\", "
                    "statement=\"{}\", "
                    "type=\"completed-request\"}} {} {}".format(
                        "completed_request_scan_results",
                        cluster_name,
                        _node,
                        record['request_id'],
                        statement_signature,
                        statement,
                        record['scan_results'],
                        record['request_time_ms']
                    )
                )
                # stat: fetches
                metrics.append(
                    "{} {{cluster=\"{}\", node=\"{}\", "
                    "request_id=\"{}\", "
                    "signature=\"{}\", "
                    "statement=\"{}\", "
                    "type=\"completed-request\"}} {} {}".format(
                        "completed_request_fetches",
                        cluster_name,
                        _node,
                        record['request_id'],
                        statement_signature,
                        statement,
                        record['fetches'],
                        record['request_time_ms']
                    )
                )
        except Exception as e:
            print("completed query: " + str(e))
    return metrics