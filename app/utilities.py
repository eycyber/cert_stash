import pandas as pd
from app import logger, args
import os
import dns.resolver
from config import Config
import sys


# Use pandas to connect to the database given in argument
def export_db_to_excel(engine, tablename, outfile):
    logger.debug('Reading {} table from database {} into pandas dataframe'.format(tablename, engine))
    db_dataframe = pd.read_sql_table(table_name=tablename, con=engine)
    logger.debug('Read to dataframe from database into pandas')
    if not os.path.exists('outputs'):
        os.mkdir('outputs')
    logger.info('Generating output in excel format')
    db_dataframe.to_excel('outputs/{}.xlsx'.format(outfile))
    logger.info('Generated {}.xlsx in outputs folder'.format(outfile))


def create_dataframe_from_sql(engine, tablename):
    logger.debug('Reading {} table from database {} into pandas dataframe'.format(tablename, engine))
    db_dataframe = pd.read_sql_table(table_name=tablename, con=engine)
    logger.debug('Read to dataframe from database into pandas')
    return db_dataframe


def export_to_excel(dataframe, outfile):
    logger.debug('Checking if dataframe is None')
    if len(dataframe) > 0:  # Check if dataframe has any data in it
        if not os.path.exists('outputs'):
            os.mkdir('outputs')
        dataframe.to_excel('outputs/{}.xlsx'.format(outfile))
        logger.info('Generated {}.xlsx in outputs folder'.format(outfile))


# Resolved the domains in the dataframe and returns the results in another dataframe
def resolve_domains(dataframe):
    # initiate nameservers for dns resolver
    logger.debug('Initiating resolver object from dnspython')
    ns_resolver = dns.resolver.Resolver(configure=False)
    logger.debug('Setting names servers as in the Config')
    ns_resolver.nameservers = Config.NAME_SERVERS

    # initiate a dataframe to hold dns resolving results
    logger.debug('Initiating dataframe to hold dns resolution results')
    ns_dataframe = pd.DataFrame(
        columns=['name_value', 'IP address', 'CNAME'])
    # initiating other variables to hold answers
    logger.info('Extracting unique items from the data frame into a list')
    uniq_domain_list = dataframe['name_value'].unique()
    # # Debug code for writing unique list to file
    # with open('outputs/unique_list.txt', 'w') as filehandle:
    #     for item in uniq_domain_list:
    #         filehandle.write('\n{}'.format(item))
    # sys.exit('DEBUG: Exit!!')

    logger.debug('Iterating through the unique domain list')
    for item in uniq_domain_list:
        ns_a_result = 'NULL'
        ns_cname_result = 'NULL'
        ip_list = []
        cname_list = []
        domain = item.rstrip()
        logger.debug('Selected domain {}:'.format(domain))
        try:
            ns_a_result = ns_resolver.query(domain, 'A')
            logger.debug('Resolved A record {}:'.format(ns_a_result.response.to_text()))
            for ip in ns_a_result:
                ip_list.append(ip.to_text())
        except:
            logger.debug('Error in resolving A record for {} ... moving on'.format(domain))
        try:
            ns_cname_result = ns_resolver.query(domain, 'CNAME')
            logger.debug('Resolved CNAME record {}:'.format(ns_cname_result.response.to_text()))
            for cname in ns_cname_result:
                cname_list.append(cname.to_text())
        except:
            logger.warning('Error in resolving A record for {} ... moving on'.format(domain))
        logger.debug('Appending row to ns dataframe')
        ns_dataframe = ns_dataframe.append({'name_value': domain,
                                            'IP address': ip_list,
                                            'ns_cname_result': cname_list}, ignore_index=True)
        logger.debug('Appended row to ns dataframe {}'.format(ns_dataframe['name_value']))
    return ns_dataframe
