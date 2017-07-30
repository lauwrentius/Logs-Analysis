#!/usr/bin/env python
# -*- coding: utf-8 -*-


#
# Script for Database Log Analysis
#

import psycopg2
import os
import datetime

# Database name
DB_NAME = "news"
# Log Report Output Filename
FILENAME = "log-report.txt"

# List of questions for the log reports
QUESTION_ARR = [
    '1. What are the most popular three articles of all time?',
    '2. Who are the most popular article authors of all time?',
    '3. On which days did more than 1% of requests lead to errors?']

# Queries to be executed
QUERY_ARR = [
    # Query 1
    ('SELECT articles.title, subq.views '
     'FROM articles '
     'LEFT JOIN '
     '(SELECT path, count(ip) as views '
     'FROM log '
     'WHERE status=\'200 OK\' '
     'GROUP BY path) as subq '
     'ON subq.path=CONCAT(\'/article/\',articles.slug) '
     'ORDER BY subq.views DESC LIMIT 3;'),

    ('SELECT  subq2.name, count(subq2.path) as views '
     'FROM'
     '(SELECT log.path, log.ip, subq1.slug, subq1.title, subq1.name '
     'FROM log '
     'RIGHT JOIN '
     '(SELECT articles.slug, articles.title, authors.name '
     'FROM articles JOIN authors ON articles.author=authors.id) as subq1 '
     'ON log.path=CONCAT(\'/article/\',subq1.slug) '
     'WHERE status=\'200 OK\') as subq2 '
     'GROUP BY subq2.name ORDER BY views DESC;'),

    ('SELECT subq.day, ROUND((100.0*subq.err/subq.total),2) as error '
     'FROM '
     '(SELECT date_trunc(\'day\', time) as day, '
     'count(id) as total, '
     'sum(case when status!=\'200 OK\' then 1 else 0 end) as err '
     'FROM log '
     'GROUP BY day) as subq '
     'WHERE ROUND((100.0*subq.err/subq.total),2) >1;')]


def execute_query(queries):
    """
    Connects to the database and execute the queries`.

    Args:
        queries: Array of queries for execution.

    Returns:
        Query results in array.
    """

    db = psycopg2.connect(database=DB_NAME)
    c = db.cursor()
    ret = []

    for i in queries:
        c.execute(i)
        ret.append(c.fetchall())
    db.close()

    return ret


def output_to_file(text_format):
    """
    Outputs a body of text to a file

    Args:
        text_format: The body of text for output.
    """

    f = open('./' + FILENAME, 'w')
    f.write(text_format)
    f.close()


def format_query1(query_result):
    """
    Formats the query result to be more readable (for question 1&2)

    Args:
        query_result: The Query result in array format.

    Returns:
        The formatted result in string.
    """

    ret = ''
    for i in query_result:
        ret += ('• {} - {} views\n').format(i[0], str(i[1]))
    return ret


def format_query2(query_result):
    """
    Formats the query result to be more readable (for question 3)

    Args:
        query_result: The Query result in array format.

    Returns:
        The formatted result in string.
    """

    ret = ''
    for i in query_result:
        date_str = i[0].strftime('%B %d, %Y')
        ret += ('• {} - {}% errors\n').format(date_str, str(i[1]))
    return ret


def format_report(query_result):
    """
    Formats the report and congregate with the questions

    Args:
        query_result: The Query result in array format.

    Returns:
        The formatted report in string.
    """

    result = ''
    for i in range(len(QUESTION_ARR)):
        result += QUESTION_ARR[i] + '\n'

        if(i != 2):
            result += format_query1(query_result[i]) + '\n\n'
        else:
            result += format_query2(query_result[i]) + '\n\n'

    return result


# Executes the script
if __name__ == "__main__":
    query_result = execute_query(QUERY_ARR)
    text_format = format_report(query_result)
    output_to_file(text_format)