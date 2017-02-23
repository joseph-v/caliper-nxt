import time
import logging
import os

#Import for parser code
import importlib
import re
import sys
import yaml
import types
import string
import errno

from avocado.core.plugin_interfaces import JobPre, JobPost
#from avocado.plugins.parser.tests_setting import BaseCfg

import ConfigParser


#===============================================================
# Configuration class for caliper input and output
#===============================================================
COMBINED_LOG_FILE = 'final_parsing_logs.yaml'
TEST_CONFIG_DIR = '/home/joseph/avocado/caliper_results/test_configs'
#PARSER_LOG_DIR = '/home/joseph/avocado/caliper_results/parser_logs'
#PARSER_SCRIPTS_DIR = '/home/joseph/avocado/caliper_results/parser'

#===============================================================
# Config class
#===============================================================
class Config():
    def __init__(self, config_file, caliper_output):
        # configuration file from caliper run command
        self.config_file = config_file
        # output path from caliper run command
        self.caliper_output = caliper_output

        self.utils = Utils()
        input_config, input_section = self.utils.read_config_file(self.config_file)
        # Extract input configurations from config file
        self.config_files = input_config.options(input_section[0])
        # Extract test configurations from config file
        self.test_configs = input_config.options(input_section[1])


#===============================================================
# Scoring tools
#===============================================================
import math

def geometric_mean(values):
    try:
        values = [float(value) for value in values
                if (value != 0 and value is not None)]
    except ValueError:
        return None

    n = len(values)
    if n == 0:
        return 0
    return math.exp(sum([math.log(x) for x in values]) / n)


class Scores_method:
    score = 0

    def __init__(score):
        score = score

    @staticmethod
    def exp_score_compute(score, base, index):
        # the algorithm is (x/n)**index, n equals to 10**base
        exp_score = math.pow(
                            score / (math.pow(10, base)),
                            index)
        return exp_score

    @staticmethod
    def compute_speed_score(score, base):
        # the algorithm is score/10**(base)
        tmp_score = score / math.pow(10, base)
        return tmp_score

#===============================================================
# Utility tools
#===============================================================

# TODO: make this class singleton

class Utils():
    name = 'Utils'
    description = 'Utilities for Caliper parser'

    # def __init__(self):
    #     print "Initialize Utils"

    def read_config_file(self, filename):
        config = ConfigParser.ConfigParser()
        config.read(filename)
        sections = config.sections()
        return (config, sections)

    def file_copy(self, des_file, source_file, style):
        des_fp = open(des_file, style)
        source_fp = open(source_file, 'r')
        content = source_fp.read()
        des_fp.write(content)
        source_fp.close()
        des_fp.close()

    """
    For 'android', we read 'common_cases_def.cfg' and 'common_case_def.cfg';
    For 'arm', read the 'common_case_def.cfg' and 'arm_cases_def.cfg';
    For 'x86', read the 'common_case_def.cfg' and 'server_cases_def.cfg'.
    """

    def get_cases_def_files(self, option, test_config_dir):
        cfg_files = []
        cases_tail = "_cases_def.cfg"
        common_cfg = "common" + cases_tail
        common_cfg_path = os.path.join(test_config_dir, common_cfg)
        cfg_files.append(common_cfg_path)
        if (option == 'arm_32'):
            other_cfg = "arm" + cases_tail
        elif (option == 'android'):
            other_cfg = "android" + cases_tail
        elif (option == 'arm_64'):
            other_cfg = "server" + cases_tail
        else:
            other_cfg = 'server' + cases_tail
        other_cfg_path = os.path.join(test_config_dir, other_cfg)
        cfg_files.append(other_cfg_path)
        return cfg_files

    def get_fault_tolerance_config(self, section, key, config_dir):
        flag = 0
        #logging.debug(caliper_path.config_files.config_dir)
        #cfg_file = os.path.join(caliper_path.config_files.config_dir,
        #                                'execution_contl.cfg')
        cfg_file = os.path.join(config_dir, 'execution_contl.cfg')
        # try:
        #     tolerence_cfg = BaseCfg(cfg_file)
        #     value = tolerence_cfg.get_value(section, key)
        # except Exception:
        #     raise
        # else:
        #     if (value.startswith("True") or value.startswith("true")):
        #         flag = 1
        #     elif (value.startswith("False") or value.startswith('false')):
        #         flag = 0
        #     elif value == '':
        #         flag = 1
        #     else:
        #         logging.info("Wrong configuration in config/execution_contl.cfg")
        #         flag = 0
        #     return flag

    def get_host_name(self, host):
        return 'htsat-slave2-com'
        # try:
        #     arch_result = host.run("/bin/uname -a")
        # except error.CmdError, e:
        #     raise error.ServRunError(e.args[0], e.args[1])
        # else:
        #     returncode = arch_result.exit_status
        #     if returncode == 0:
        #         output = arch_result.stdout
        #         try:
        #             machine_name = settings.get_value('CLIENT', 'Platform_name', type=str)
        #         except:
        #             machine_name = output.split(" ")[1]
        #         return machine_name
        #     else:
        #         msg = "Caliper does not support this kind of arch machine"
        #         raise error.ServUnsupportedArchError(msg)


#===============================================================
# Write tool utility
#===============================================================

class  Write_Tool():

    name = 'Tools'
    description = 'Tools for Caliper parser'

    # def __init__(self):
    #     print 'Init of write tool'

    def compute_score(self, score_way, result_fp):
        # this part should be improved
        func_args = score_way.split()
        score_method = func_args[0]
        if len(func_args) < 2:
            logging.info("The configuration of run the benchmark is wrong")
            return -5
        result_score = 0
        base = string.atof(func_args[1])
        if len(func_args) >= 3:
            index = string.atof(func_args[2])
        if score_method == "exp_score_compute":
            if result_fp == 0:
                result_score = 0
            else:
                try:
                    result_score = Scores_method.exp_score_compute(result_fp,
                                                                   base, index)
                    logging.debug("After computing, the result is %f" %
                                  result_score)
                except Exception, e:
                    raise e
        else:
            if score_method == "compute_speed_score":
                if result_fp == 0:
                    result_score = 0
                else:
                    try:
                        result_score = Scores_method.compute_speed_score(
                            result_fp,
                            base)
                    except Exception, e:
                        raise e
        return result_score


    def write_yaml_func(self, yaml_file, tmp, result, kind):
        return self.write_yaml_perf(yaml_file, tmp, result, kind)

    def write_dic(self, result, tmp, score_way, yaml_file, file_flag):
        flag = 0
        for key in result.keys():
            if type(result[key]) == dict:
                sub_dic = result[key]
                tmp.append(key)
                flag = self.write_sin_dic(sub_dic, tmp, score_way, yaml_file, file_flag)
                tmp.remove(key)
            else:
                logging.debug("There is wrong with the parser")
                flag = -1
                return flag
        flag = 1
        return flag


    def write_sin_dic(self, result, tmp, score_way, yaml_file, file_flag):
        flag = 0
        for key in result.keys():
            if type(result[key]) == list:
                sublist = result[key]
                geo_mean = geometric_mean(sublist)
            elif type(result[key]) is types.StringType:
                geo_mean = string.atof(result[key])
            elif type(result[key]) is types.FloatType:
                geo_mean = result[key]
            elif type(result[key]) is types.IntType:
                geo_mean = result[key]
            else:
                return -4
            tmp.append(key)

            if file_flag == 2:
                geo_mean = self.compute_score(score_way, geo_mean)

            flag1 = self.write_yaml_perf(yaml_file, tmp, geo_mean, file_flag)

            tmp.remove(key)
            if not flag1:
                return flag1
        flag = 1
        return flag


    def write_multi_dic(self, result, tmp, score_way, yaml_file, flag_file):
        flag = 0
        for key in result.keys():
            if type(result[key]) == dict:
                try:
                    sub_dic = result[key]
                    tmp.append(key)
                    flag = self.write_dic(sub_dic, tmp, score_way, yaml_file, flag_file)
                    tmp.remove(key)
                except Exception:
                    flag = -1
            else:
                logging.info("There is wrong with the parser")
                flag = -1
            if flag != 1:
                return flag
        flag = 1
        return flag

    def round_perf(self, score):
        if (score < 0.1):
            score = round(score, 3)
        elif (score < 10):
            score = round(score, 2)
        else:
            score = round(score, 1)
        return score


    def write_yaml_perf(self, yaml_file, tmp, result, kind=1):
        flag = 0
        try:
            if not os.path.exists(yaml_file):
                os.mknod(yaml_file)
                if yaml_file.endswith("_score.yaml"):
                    file_name = yaml_file.split('/')[-1]
                    file_name = file_name.split("_score")[0] + ".yaml"
                    abs_path = yaml_file.split('/')
                    abs_path[-1] = file_name
                    file_name = "/".join(abs_path)
                    with open(yaml_file,'w') as fp:
                        tp = open(file_name)
                        dic = yaml.load(tp)
                        dic_new = {}
                        dic_new['Configuration'] = {}
                        dic_new['Configuration'] = dic['Configuration']
                        dic_new['name'] = {}
                        dic_new['name'] = dic['name']
                        fp.write(yaml.dump(dic_new,default_flow_style=False))
        except:
            pass
        fp = open(yaml_file)
        result = self.round_perf(result)
        x = yaml.load(fp)
        try:
            RES = 'results'
            if not x:
                x = {}
            if RES not in x:
                x[RES] = {}
            if not x[RES]:
                x[RES] = {}
            if tmp[0] not in x[RES]:
                x[RES][tmp[0]] = {}
            if tmp[1] not in x[RES][tmp[0]]:
                x[RES][tmp[0]][tmp[1]] = {}
            if tmp[2] not in x[RES][tmp[0]][tmp[1]]:
                x[RES][tmp[0]][tmp[1]][tmp[2]] = {}
            if kind == 1:
                if tmp[3] not in x[RES][tmp[0]][tmp[1]][tmp[2]]:
                    x[RES][tmp[0]][tmp[1]][tmp[2]][tmp[3]] = {}
                x[RES][tmp[0]][tmp[1]][tmp[2]][tmp[3]] = result
                flag = 1
            else:
                if kind == 2:
                    if 'Point_Scores' not in x[RES][tmp[0]][tmp[1]][tmp[2]]:
                        x[RES][tmp[0]][tmp[1]][tmp[2]]['Point_Scores'] = {}
                    if not x[RES][tmp[0]][tmp[1]][tmp[2]]['Point_Scores']:
                        x[RES][tmp[0]][tmp[1]][tmp[2]]['Point_Scores'] = {}
                    if tmp[3] not in \
                        x[RES][tmp[0]][tmp[1]][tmp[2]]['Point_Scores']:
                        x[RES][tmp[0]][tmp[1]][tmp[2]]['Point_Scores'][tmp[3]] =\
                                                                            result
                        flag = 1
                    x[RES][tmp[0]][tmp[1]][tmp[2]]['Point_Scores'][tmp[3]] = result
                    flag = 1
        except BaseException, e:
            logging.debug("There is wrong when write the data in file %s." % yaml)
            logging.debug(e)
            flag = -1
        else:
            fp.close()
            with open(yaml_file, 'w') as outfile:
                outfile.write(yaml.dump(x, default_flow_style=False))
            outfile.close()
            flag = 1
        return flag

















# ===============================================================
#  Implement ouput_log to parsed_log
#  ===============================================================

class LogConverter():
    name = 'Converter'
    description = 'Converts test output logs to parsed log'

    def __init__(self):
        self.utils = Utils()

    def parser_case(self, kind_bench, bench_name, parser_file, parser, infile, outfile):
        if not os.path.exists(infile):
            return -1
        result = 0
        fp = open(outfile, 'a+')

        current_dir = os.path.dirname(sys.modules[__name__].__file__)
        parser_dir = os.path.abspath(os.path.join(current_dir, 'parser_scripts'))
        rel_path = "parser_scripts/" + parser_file

        # FRONT_TMP_DIR = os.path.join(CALIPER_DIR, 'frontend')

        # the parser function defined in the config file is to filter the output.
        # get the abspth of the parser.py which is defined in the config files.
        # changed by Elaine Aug 8-10

        # JVP: Commented below as we give full path of parser

        if not parser_file:
            pwd_file = bench_name + "_parser.py"
            parser_file = os.path.join(parser_dir, pwd_file)
        else:
            parser_file = os.path.join(parser_dir, parser_file)

        # rel_path = os.path.relpath(parser_file,
        #                            os.path.dirname(current_dir))
        #rel_path = os.path.relpath(parser_file)
        parser_path = rel_path.split(".py")[0]
        parser_name = parser_path.replace(os.sep, '.')

        #parser_name = 'parser_scripts.' + parser_file

        # rel_path = os.path.relpath(parser_file, os.path.dirname(AVOCADO_DIR))
        # parser_path = rel_path.split(".")[0]
        # parser_name = parser_path.replace(os.sep, '.')

        #parser_dir_path = PARSER_LOG_DIR
        #parser_file = os.path.join(parser_dir_path, parser_file)

        result = 0
        if os.path.isfile(parser_file):
            try:
                # import the parser module import_module
                parser_module = importlib.import_module(parser_name)
            except ImportError, e:
                logging.info(e)
                return -3
            try:
                methodToCall = getattr(parser_module, parser)
            except Exception, e:
                logging.info(e)
                return -4
            else:
                infp = open(infile, "r")
                outfp = open(outfile, 'a+')
                contents = infp.read()

            if bench_name == "ltp":
                result = methodToCall(contents, outfp)
            else:

                for content in re.findall("BEGIN TEST(.*?)\[status\]", contents,
                                          re.DOTALL):
                    try:
                        # call the parser function to filter the output
                        logging.debug("Begining to parser the result of the case")
                        if not parser == 'hardware_info_parser':
                            result = methodToCall(content, outfp)
                        else:
                            host_name = self.utils.get_host_name('dummy')
                            yaml_dir = os.path.join(os.path.join(self.output_dir, 'results'),'yaml')

                            result = methodToCall(content, outfp, host_name, yaml_dir)
                    except Exception, e:
                        logging.info(e)
                        return -5
            outfp.close()
            infp.close()
        fp.close()
        return result

    def parse_one_test(self, test_sub_dir, caliper_output_dir, bench_name,
                       run_file, parser_file, dic):
        """
        function: run one benchmark which was selected in the configuration files
        """

#        tests_cfg_dir = self.test_configs
        tests_cfg_dir = TEST_CONFIG_DIR

        try:
            # get the abspath, which is filename of run config for the benchmark
            # JVP individual test case configuration -- to be copied
            bench_conf_file = os.path.join(
                tests_cfg_dir,
                test_sub_dir, run_file)

            # get the config sections for the benchmrk
            configRun, sections_run = self.utils.read_config_file(
                bench_conf_file)

        except AttributeError as e:
            raise AttributeError

        except Exception:
            raise

        LTP_TEST = "ltp"

        # logging.debug("the sections to run are: %s" % sections_run)
        # print "DEBUG: Caliper: sections to run are: %s" % sections_run

        exec_dir = os.path.join(caliper_output_dir, 'output_logs')
        if not os.path.exists(exec_dir):
            #os.mkdir(exec_dir)
            try:
                os.mkdir(exec_dir)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    print 'Directory exists'
                elif e.errno != errno.EACCES:
                    print 'Access violation'
                else:
                    print 'Something else happened'

        log_bench = os.path.join(exec_dir, bench_name)
        logfile = log_bench + "_output.log"



        if bench_name != LTP_TEST:
            if not os.path.exists(logfile):
                return -1

        tmp_log_file = log_bench + "_output_tmp.log"
        #exec_dir = os.path.join(caliper_output_dir, 'parser_logs')
        parser_result_file = log_bench + "_parser.log"
        tmp_parser_file = log_bench + "_parser_tmp.log"
        if os.path.exists(parser_result_file):
            os.remove(parser_result_file)
        # output_logs_names = glob.glob(Folder.exec_dir+"/*output.log")

        # for each command in run config file, read the config for the benchmark
        for i in range(0, len(sections_run)):
            dic[bench_name][sections_run[i]] = {}

            flag = 0
            try:
                category = configRun.get(sections_run[i], 'category')
                scores_way = configRun.get(sections_run[i], 'scores_way')
                parser = configRun.get(sections_run[i], 'parser')
                command = configRun.get(sections_run[i], 'command')
            except Exception:
                # logging.debug("no value for the %s" % sections_run[i])
                #print "DEBUG: Caliper: sections to run are: %s" % sections_run[i]
                continue

            if bench_name == LTP_TEST:
                subsection = sections_run[i].split(" ")[1]
                subsection_file = log_bench + "_" + subsection + "_output.log"
                if not os.path.exists(subsection_file):
                    continue
            if os.path.exists(tmp_parser_file):
                os.remove(tmp_parser_file)
            # parser the result in the tmp_log_file, the result is the output of
            # running the command

            try:
                logging.debug("Parsering the result of command: %s" % command)
                if bench_name == LTP_TEST:
                    outfp = open(tmp_parser_file, "w")
                    outfp.write("%s" % (subsection))
                    outfp.close()
                    parser_result = self.parser_case(test_sub_dir, bench_name, parser_file,
                                                     parser, subsection_file,
                                                     tmp_parser_file)
                else:
                    outfp = open(logfile, 'r')
                    infp = open(tmp_log_file, 'w')
                    infp.write(re.findall("test start\s+%+(.*?)%+\s+test_end", outfp.read(), re.DOTALL)[i])

                    infp.close()
                    outfp.close()
                    parser_result = self.parser_case(test_sub_dir, bench_name, parser_file,
                                                     parser, tmp_log_file,
                                                     tmp_parser_file)
                dic[bench_name][sections_run[i]]["type"] = type(parser_result)
                dic[bench_name][sections_run[i]]["value"] = parser_result

            except Exception, e:
                logging.info("Error while parsing the result of \" %s \""
                             % sections_run[i])
                logging.info(e)
                if os.path.exists(tmp_parser_file):
                    os.remove(tmp_parser_file)
                if os.path.exists(tmp_log_file):
                    os.remove(tmp_log_file)
            else:
                self.utils.file_copy(parser_result_file, tmp_parser_file, "a+")
                if os.path.exists(tmp_parser_file):
                    os.remove(tmp_parser_file)
                if os.path.exists(tmp_log_file):
                    os.remove(tmp_log_file)
                if (parser_result <= 0):
                    continue

    # Implementation of parse
    def parse_logs(self, config_filename, caliper_output_dir):

        # TODO: use config object here JVP
        self.output_dir = caliper_output_dir
        input_config, input_section = self.utils.read_config_file(config_filename)
        config_files = input_config.options(input_section[0])

        dic = {}
        for i in range(0, len(config_files)):
            # for i in range(0, len(config_files)):
            # run benchmarks selected in each configuration file
            # config_file = os.path.join(caliper_path.CALIPER_PRE, config_files[i])
            config_file = input_config.get(input_section[0], config_files[i])
            # config_file = os.path.join(config_files[i])
            config, sections = self.utils.read_config_file(config_file)

            # logging.debug(sections)
            print "DEBUG: Caliper: Sections =%s" % sections

            # get if it is the 'common' or 'arm' or 'android'
            classify = config_files[i].split("/")[-1].strip().split("_")[0]

            # logging.debug(classify)
            print "DEBUG: Caliper: classify =%s" % classify

            print "DEBUG: Caliper: sections size =", len(sections)

            for i in range(0, len(sections)):
                dic[sections[i]] = {}
                # try to resolve the configuration of the configuration file
                try:
                    run_file = config.get(sections[i], 'run')
                    parser = config.get(sections[i], 'parser')
                except Exception:
                    raise AttributeError("The is no option value of parser")

                logging.info("Parsing %s" % sections[i])
                bench = os.path.join(classify, sections[i])

                try:
                    result = self.parse_one_test(bench, caliper_output_dir,
                                                 sections[i], run_file, parser, dic)
                except Exception:
                    logging.info("Running %s Exception" % sections[i])

                    # JVP: TO DO : Handle this exception

                    # crash_handle.main()
                    # print_format()
                    # run_flag = Utils.get_fault_tolerance_config(
                    #    'fault_tolerance', 'run_error_continue', )
                    # if run_flag == 1:
                    #    continue
                    # else:
                    #    return result
                else:
                    logging.info("Parsing %s Finished" % sections[i])
                    # print_format()
        # outfp = open(os.path.join(caliper_path.folder_ope.workspace,
        #                          caliper_path.folder_ope.name.strip()
        #                          +"/final_parsing_logs.yaml"),'w')
        outfp = open(os.path.join(caliper_output_dir,
                                  COMBINED_LOG_FILE), 'w')
        outfp.write(yaml.dump(dic, default_flow_style=False))
        outfp.close()
        return 0



#===============================================================
# Calculate score from parsed log
#===============================================================

class CalculateScore():

    name = 'Parser'
    description = 'Calculate score from parsed log'

    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.utils = Utils()
        self.write_results = Write_Tool()

    def deal_dic_for_yaml(self, result, tmp, score_way, yaml_file, flag):

        if (len(tmp) == 2):
            status = self.write_results.write_dic(result, tmp, score_way,
                                             yaml_file, flag)
        elif (len(tmp) == 3):
            status = self.write_results.write_sin_dic(result, tmp, score_way, yaml_file, flag)
        else:
            status = self.write_results.write_multi_dic(result, tmp, score_way,
                                                   yaml_file, flag)
        return status


    def compute_func(self, result, tmp, score_way, result_yaml, flag=1):
        flag1 = 0

        if flag == 2:
            result = result * 100
        try:
            flag1 = self.write_results.write_yaml_func(result_yaml,
                                                  tmp, result,
                                                  flag)
        except BaseException:
            logging.debug("There is wrong when computing the score")
        return flag1


    def compute_perf(self, result, tmp, score_way, result_yaml, flag=1):
        result_flag = 1
        score_flag = 2

        if type(result) is types.StringType:
            if re.search('\+', result):
                result = result.replace('\+', 'e')
            result_fp = string.atof(result)
        elif type(result) is types.FloatType:
            result_fp = result
        elif type(result) is types.IntType:
            result_fp = result
        elif (type(result) == dict and (len(tmp) > 0 and len(tmp) < 4)):
            return self.deal_dic_for_yaml(result, tmp, score_way,
                                          result_yaml, flag)
        else:
            return -4

        if flag == 2:
            result_fp = self.write_results.compute_score(score_way, result_fp)
        flag1 = 0
        try:
            flag1 = self.write_results.write_yaml_perf(result_yaml, tmp,
                                                  result_fp, flag)
        except BaseException:
            logging.debug("There is wrong when compute the score.")
        return flag1


    def compute_case_score(self, result, category, score_way, target, flag):
        tmp = category.split()
        length = len(tmp)

        #

        # TODO: remove dirctory calculation
        results_dir = os.path.join(self.output_dir, 'results')
        yaml_dir = os.path.join(results_dir, 'yaml')

        target_name = self.utils.get_host_name(target)
        result_yaml_name = target_name + '.yaml'
        score_yaml_name = target_name + '_score.yaml'

        if flag == 1:
            result_yaml = os.path.join(yaml_dir, result_yaml_name)
        else:
            result_yaml = os.path.join(yaml_dir, score_yaml_name)

        if (length == 4 and tmp[0] == 'Functional'):
            return self.compute_func(result, tmp, score_way, result_yaml, flag)
        elif ((length != 0 and length <= 4) and tmp[0] == 'Performance'):
            return self.compute_perf(result, tmp, score_way, result_yaml, flag)
        else:
            return -4


    def collate_logs(self, flag):
        # according the method in the config file, compute the score
        # dic = yaml.load(open(caliper_path.folder_ope.final_parser, 'r'))
        final_parserd_file = os.path.join(self.output_dir, COMBINED_LOG_FILE)
        dic = yaml.load(open(final_parserd_file, 'r'))

        #utils = Utils()

        # Need to correctly identify options ARM/ARM32/Server
        options = ''

        print "DEBUG: Caliper: test_config_dir =%s" % TEST_CONFIG_DIR
        config_files = self.utils.get_cases_def_files(options, TEST_CONFIG_DIR)
        print "DEBUG: Caliper: config_files =%s" % config_files

        for i in range(0, len(config_files)):
            config_file = os.path.join(config_files[i])
            config, sections = self.utils.read_config_file(config_file)
            classify = config_files[i].split("/")[-1].strip().split("_")[0]
            for j in range(0, len(sections)):
                try:
                    run_file = config.get(sections[j], 'run')
                    parser = config.get(sections[j], 'parser')
                except Exception:
                    raise AttributeError("The is no option value of Computing")

                # print_format()
                if flag == 1:
                    # logging.info("Generation raw yaml for %s" % sections[j])
                    print "Generation raw yaml for %s" % sections[j]
                else:
                    print "Computing Score for %s" % sections[j]
                    # logging.info("Computing Score for %s" % sections[j])
                bench = os.path.join(classify, sections[j])
                try:
                    # get the abspath, which is filename of run config for the benchmark
                    bench_conf_file = os.path.join(TEST_CONFIG_DIR, bench, run_file)
                    # get the config sections for the benchmrk
                    configRun, sections_run = self.utils.read_config_file(
                        bench_conf_file)
                except AttributeError as e:
                    raise AttributeError
                except Exception:
                    raise
                for k in range(0, len(sections_run)):
                    try:
                        category = configRun.get(sections_run[k], 'category')
                        scores_way = configRun.get(sections_run[k], 'scores_way')
                        command = configRun.get(sections_run[k], 'command')
                    except Exception:
                        logging.debug("no value for the %s" % sections_run[k])
                        logging.info(e)
                        continue
                    try:
                        logging.debug("Computing the score of the result of command: %s"
                                      % command)

                        # JVP: needs to remove this target_exec_dir
                        target_exec_dir = os.path.join(self.output_dir, 'results')
                        flag_compute = self.compute_case_score(dic[sections[j]][sections_run[k]]["value"], category,
                                                               scores_way, target_exec_dir, flag)
                    except Exception, e:
                        #print "DEBUG: Caliper: ERROR WHile Computing %s ...." % sections_run[k]
                        logging.info("Error while computing the result of \"%s\"" % sections_run[k])
                        logging.info(e)
                        continue
                    else:
                        if not flag_compute and dic[bench][sections_run[k]["value"]]:
                            logging.info("Error while computing the result\
                                            of \"%s\"" % command)

#===============================================================
# Main PARSER class
#===============================================================

class Parser(JobPre, JobPost):

    name = 'Parser'
    description = 'Parses caliper output to YAML output'

    def __init__(self):
        self.log = logging.getLogger("avocado.app")

    def copy_test_outputs(self, directory):
        """Copy stdout of test to a common folder for parser to process"""

        # Walk directory to get all the stdout for the parsing
        for root, dirs, files in os.walk(directory):
            for name in files:
                if name == 'stdout':
                    full_filename = os.path.join(root, name)
                    full_dirname = os.path.basename(os.path.dirname(full_filename))

                    part_name = re.split('_', re.split(':', full_dirname)[0])
                    part_name2 = part_name[len(part_name) - 1]
                    benchmark_name = re.split('\.', part_name2)[0]

                    #handle special cases where test contains '_'
                    if benchmark_name == 'info':
                        benchmark_name = "hardware_" + benchmark_name

                    from shutil import copyfile
                    copyfile(full_filename,
                             os.path.join(self.output_logs_dir, benchmark_name + "_output.log"))

                    print 'DEBUG: Caliper:Copied file %s_output.log ' % benchmark_name

    def process_logs(self, job):

        try:
            directory = os.path.join(job.logdir, 'test-results')
            self.copy_test_outputs(directory)
        except Exception:
            print 'DEBUG: Caliper:ERROR while COPY output logs ...'

        try:
            self.converter = LogConverter()
            self.converter.parse_logs(self.config_file, self.caliper_output)
        except Exception:
            print 'DEBUG: Caliper:ERROR while PARSE ...'


        try:
            self.scorer = CalculateScore(self.caliper_output)
            self.scorer.collate_logs(1)
        except Exception:
            print 'DEBUG: Caliper:ERROR while SCORE 1 ...'


        try:
            self.scorer.collate_logs(2)
        except Exception:
            print 'DEBUG: Caliper:ERROR while SCORE 2 ...'


        print 'DEBUG: Caliper:PARSING is Done ...'

    def create_output_dir(self):
        self.output_logs_dir = os.path.join(self.caliper_output, 'output_logs')
        self.results_dir = os.path.join(self.caliper_output, 'results')
        self.yaml_dir = os.path.join(self.results_dir, 'yaml')

        try:
            if not os.path.exists(self.caliper_output):
                os.mkdir(self.caliper_output)
            if not os.path.exists(self.output_logs_dir):
                os.mkdir(self.output_logs_dir)
            if not os.path.exists(self.results_dir):
                os.mkdir(self.results_dir)
            if not os.path.exists(self.yaml_dir):
                os.mkdir(self.yaml_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                print 'Directory exists'
            elif e.errno != errno.EACCES:
                print 'Access violation'
            else:
                print 'Something else happened'

    def pre_parse(self, job):
        print 'DEBUG: Caliper:Prepare for Caliper parser  ...'


    def parser(self, job):
        # Read configuration file name from command line
        self.config_file = getattr(job.args, 'config_filename', False)
        if not self.config_file:
            print 'DEBUG: Caliper: Caliper parser is not enabled...'
            return

        if not os.path.exists(self.config_file):
            print 'DEBUG: Caliper: Caliper config file is not found...'
            return

        # Read output folder name from command line
        self.caliper_output = getattr(job.args, 'caliper_output', False)
        if not self.caliper_output:
            self.caliper_output = os.path.join(job.logdir, 'caliper_output')
            print 'Output folder is not specified in commandline'
            print 'Using default location %s' % self.caliper_output

        try:
            # Instantiate config
            self.config = Config(self.config_file, self.caliper_output)

            # Create ouput folders
            self.create_output_dir()
        except Exception:
            print 'DEBUG: Caliper:ERROR while initializing parser ...'

        # Start processing log files ...
        self.process_logs(job)

   
    pre = pre_parse
    post = parser
