import getopt
import sys
from loguru import logger
import colorama
import signal
from AnimeUnityEngine import scraper, logging_aux, res_obj_manipulator, jdownloader
import printer

config = {'crawl_path': None, 'download_path': None, 'print_level': 9, 'season': None, 'log_level': 'WARNING', 'file_log':False}
version = "v1.0"

def sig_handler(_signo, _stack_frame):
    print("\n")
    sys.exit(0)
@logging_aux.logger_wraps()
def main():
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    logging_aux.init_logger(level=config['log_level'], file_log=config['file_log'])
    if len(sys.argv) == 1:
        keyword = interactive_mode()
    else:
        keyword = cli_mode()
    logger.debug("Keyword selected: {}".format(keyword))
    search_res = scraper.search(title=keyword)
    logger.debug("search results: {}".format(search_res))
    if not search_res:
        print(f"{colorama.Fore.RED}No Anime Found{colorama.Style.RESET_ALL}")
        logger.debug("No anime found, keyword: {}".format(keyword))
        exit(1)
    logger.debug("Printing anime list")
    printer.print_anime_list(search_res, config, 1)
    anime_id = input("ID: ")
    logger.debug("ID selected: {}".format(anime_id))
    selected = res_obj_manipulator.get_selected_anime_obj_by_id(search_res, anime_id)
    logger.debug("Anime selected: {}".format(selected))
    logger.debug("Printing anime episodes")
    if config['season'] is not None:
        selected = scraper.season_scraper(selected, config)
        logger.debug(f"Season scraped: {selected}")
    printer.print_anime_list(selected, config, 2)
    if config['crawl_path'] is not None and config['download_path'] is not None:
        jdownloader.send_to_jdownloader(selected, config)


@logging_aux.logger_wraps()
def cli_mode():
    keyword = None
    global config

    argv = sys.argv[1:]

    try:
        opts = getopt.getopt(argv, 'k:s:p:hv', ['printlevel=', 'keyword=', 'crawlpath=', 'jdownloadpath=', 'season=', 'loglevel=','help','version', 'filelog'])
    except getopt.GetoptError:
        # stampa l'informazione di aiuto ed esce:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ['-k', '--keyword']:
            keyword = arg
        if opt in ['--jdownloadpath']:
            config['download_path'] = arg
        if opt in ['--crawlpath']:
            config['crawl_path'] = arg
        if opt in ['-p', '--printlevel']:
            config['print_level'] = int(arg)
        if opt in ['-s', '--season']:
            config['season'] = []
            for elem in str.split(arg, ','):
                config['season'].append(elem)
        if opt in ['--loglevel']:
            if arg in logging_aux.defined_log_levels:
                config['loglevel'] = arg
            else:
                logger.warning(
                    f"Log level '{arg}' not valid.\nValid log levels are {logging_aux.defined_log_levels}.\nSetting log level to {config['loglevel']}")
        if opt in ['-h', '--help']:
            usage()
            sys.exit(0)
        if opt in ['-v', '--version']:
            print(f"AnimeUnityCLIPy {version}")
            sys.exit(0)
        if opt in ['--filelog']:
            config['file_log'] = True

    if keyword is None:
        logger.warning("No keyword selected")
        sys.exit(1)
    return keyword


@logging_aux.logger_wraps()
def interactive_mode():
    keyword = input("Keyword: ")
    return keyword


def usage():
    usage = f"AnimeUnityCLIPy {version} Usage:\n" \
            f"\t-k, --keyword (str):\t\tSpecify the keyword to search\n" \
            f"\t-p, --printlevel (int):\t\tSpecify the print level (1: title only, 2: title and info, 3: title,info and episodes,...)\n" \
            f"\t-s, --season (str):\t\tSpecify what to look for ({scraper.defined_anime_types.append('ALL')}), Multiple options can be selected (TV,Movie)\n" \
            f"\t--loglevel (str):\t\tLog level -.- One of these options: {logging_aux.defined_log_levels}\n" \
            f"\t--filelog: \t\t\tSave log > warning to a file\n" \
            f"\t--jdownloadpath (Path):\t\tDestination folder for the anime dir. MUST be used in conjunction with --crawlpath\n" \
            f"\t--crawlpath (Path):\t\tDestination folder for the crawljobs. MUST be used in conjunction with -jdp\n" \
            f"\t-h, --help:\t\t\tShow this screen\n" \
            f"\t-v, --version:\t\t\tPrint software version\n"
    print(usage)


if __name__ == "__main__":
    main()
