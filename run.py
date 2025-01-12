import argparse
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

from harbinger.cli import create_update_operation
import defaults

def update(config):
    bulk_operation, prices, oracle_timestamp = create_update_operation(config)

    print()
    formatted_timestamp = str(datetime.fromtimestamp(int(oracle_timestamp)))
    print("[+] Data is from {}".format(formatted_timestamp))

    print()
    # Good luck :P
    formatted_prices = '\n'.join([
        "    |- {} : $ {}".format(
            k.ljust(4, ' '),
            str("{:.2f}".format(round(float(v), 2))).rjust(8, ' ')
        )
        for k, v in prices.items()
    ])
    print("[+] Updating oracle with prices:\n{}".format(formatted_prices))

    result = bulk_operation.autofill().sign().inject()

    print("[+] Injected in {}".format(result['hash']))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Update Harbinger, now with 100% more Python!')

    parser.add_argument('--node-url', dest='NODE_URL', default=defaults.NODE_URL,
                        help='Which node to connect to')
    parser.add_argument('--poster-key', dest='POSTER_KEY', default=defaults.POSTER_KEY,
                        help='Which key to use to post. Must have a XTZ balance!')
    parser.add_argument('--oracle-contract', dest='ORACLE_CONTRACT', default=defaults.ORACLE_CONTRACT,
                        help='The oracle contract to invoke update operations on')
    parser.add_argument('--normalizer-contract', dest='NORMALIZER_CONTRACT', default=defaults.NORMALIZER_CONTRACT,
                        help='The normalizer contract to have the oracle push updates to')
    parser.add_argument('--oracle-data-source', dest='ORACLE_DATA_SOURCE', default=defaults.ORACLE_DATA_SOURCE,
                        help='The oracle data source to retrieve, defaults to the source powering harbinger.live')
    parser.add_argument('--update-interval', dest='update_interval', default=15,
                        help='The update interval, defaults to 15 mins')


    args = parser.parse_args()

    if args.POSTER_KEY is None:
        raise Exception("The POSTER_KEY environment variable must be set to something!")

    print("Started poster at ", datetime.now())

    scheduler = BlockingScheduler()
    scheduler.add_job(update, 'interval', args=[args], minutes=15, next_run_time=datetime.now())

    try:
        print("First update successful, starting scheduler!")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

